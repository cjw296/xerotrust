import json
import logging
import time
from pathlib import Path
from textwrap import dedent
from typing import Any, Iterator, Sequence
from unittest.mock import Mock

import pytest
from click.testing import CliRunner, Result
from testfixtures import compare, replace_in_module, mock_time, Replacer, ShouldRaise
from testfixtures.datetime import MockTime
from xero.auth import OAuth2PKCECredentials

from xerotrust import export
from xerotrust import main
from xerotrust.authentication import authenticate, SCOPES, credentials_from_file
from xerotrust.export import ALL_JOURNAL_KEYS
from xerotrust.main import cli
from xerotrust.transform import show
from .helpers import FileChecker

XERO_API_URL = "https://api.xero.com/api.xro/2.0"
XERO_CONNECTIONS_URL = "https://api.xero.com/connections"
XERO_CONTACTS_URL = f"{XERO_API_URL}/Contacts"
XERO_JOURNALS_URL = f"{XERO_API_URL}/Journals"


def run_cli(
    auth_path: Path, *args: str, input: str | None = None, expected_return_code: int = 0
) -> Result:
    args_ = ['--auth', str(auth_path)]
    args_.extend(args)
    result = CliRunner().invoke(cli, args_, catch_exceptions=False, input=input)
    compare(result.exit_code, expected=expected_return_code, suffix=result.output)
    return result


@pytest.fixture(autouse=True)
def mock_credentials_from_file() -> Iterator[Mock]:
    mock = Mock(spec=credentials_from_file)
    mock.return_value = SAMPLE_CREDENTIALS
    with replace_in_module(credentials_from_file, mock, module=main):
        yield mock


def check_auth_file(auth_path: Path) -> None:
    compare(
        expected={
            'client_id': 'CLIENT_ID',
            'client_secret': 'FOO',
            'token': {'access_token': 'test_token'},
        },
        actual=json.loads(auth_path.read_text()),
    )


def add_tenants_response(pook: Any, tenants: list[dict[str, str]] | None = None) -> None:
    pook.get(
        XERO_CONNECTIONS_URL,
        reply=200,
        # id and tenantID are not the same here, we need to use tenantId
        response_json=tenants or [{'id': 'bad', 'tenantId': 't1', 'tenantName': 'Tenant 1'}],
    )


SAMPLE_CREDENTIALS = OAuth2PKCECredentials(
    client_id='CLIENT_ID',
    client_secret='FOO',
    scope=SCOPES,
    token={'access_token': 'test_token'},
)


class TestLogin:
    @pytest.fixture(autouse=True)
    def mock_authenticate(self) -> Iterator[Mock]:
        mock = Mock(spec=authenticate)
        mock.return_value = SAMPLE_CREDENTIALS
        with replace_in_module(authenticate, mock, module=main):
            yield mock

    def test_login_with_client_id_option(
        self, mock_authenticate: Mock, tmp_path: Path, pook: Any
    ) -> None:
        auth_path = tmp_path / '.xerotrust.json'
        add_tenants_response(pook)

        result = run_cli(auth_path, 'login', '--client-id', 'test_client_id_option')

        mock_authenticate.assert_called_once_with('test_client_id_option')
        check_auth_file(auth_path)
        compare(result.output, expected='\nAvailable tenants:\n- t1: Tenant 1\n')

    def test_login_prompt_for_client_id(
        self, mock_authenticate: Mock, tmp_path: Path, pook: Any
    ) -> None:
        auth_path = tmp_path / '.xerotrust.json'
        add_tenants_response(pook)

        result = run_cli(auth_path, 'login', input='test_client_id_prompt\n')

        compare(
            result.output,
            expected='Client ID: \n\nAvailable tenants:\n- t1: Tenant 1\n',
        )
        mock_authenticate.assert_called_once_with('test_client_id_prompt')
        check_auth_file(auth_path)

    def test_login_client_id_from_auth_file(
        self, mock_authenticate: Mock, tmp_path: Path, pook: Any
    ) -> None:
        auth_path = tmp_path / '.xerotrust.json'
        add_tenants_response(pook)
        auth_path.write_text(json.dumps({'client_id': 'existing_client_id'}))

        result = run_cli(auth_path, 'login', input='\n')

        compare(
            result.output,
            expected='Client ID: \n\nAvailable tenants:\n- t1: Tenant 1\n',
        )
        mock_authenticate.assert_called_once_with('existing_client_id')
        check_auth_file(auth_path)

    def test_login_no_client_id(self, mock_authenticate: Mock, tmp_path: Path) -> None:
        auth_path = tmp_path / '.xerotrust.json'

        result = run_cli(auth_path, 'login', input='\n', expected_return_code=1)

        compare(
            result.output,
            expected=f'Client ID: \nError: No Client ID provided or found in {auth_path}.\n',
        )
        mock_authenticate.assert_not_called()
        assert not auth_path.exists()

    def test_login_with_expires_in(
        self, mock_authenticate: Mock, tmp_path: Path, pook: Any
    ) -> None:
        """Test the login command calculates expired_at from expires_in."""
        auth_path = tmp_path / '.xerotrust.json'
        add_tenants_response(pook)

        mock_authenticate.return_value.token = {'access_token': 'test_token', 'expires_in': 3600}

        mock: type[MockTime] = mock_time(delta=0)

        with replace_in_module(time.time, mock):
            run_cli(auth_path, 'login', '--client-id', 'ID')

        current_time = mock()
        compare(
            expected={
                'client_id': 'CLIENT_ID',
                'client_secret': 'FOO',
                'token': {
                    'access_token': 'test_token',
                    'expires_in': 3600,
                    'expires_at': current_time + 3600,
                },
            },
            actual=json.loads(auth_path.read_text()),
        )


class TestTenants:
    @pytest.fixture(autouse=True)
    def mock_credentials_from_file(self) -> Iterator[Mock]:
        mock = Mock(spec=credentials_from_file)
        mock.return_value = SAMPLE_CREDENTIALS
        with replace_in_module(credentials_from_file, mock, module=main):
            yield mock

    def test_tenants_default(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        pook.get(
            XERO_CONNECTIONS_URL,
            reply=200,
            # connections endpoint doesn't return the weird Date() format found elsewhere:
            response_json=[{'id': 'xx', 'createDateUtc': '2025-04-10T14:09:00.9954070'}],
        )
        result = run_cli(tmp_path, 'tenants')
        mock_credentials_from_file.assert_called_once_with(tmp_path)
        compare(
            result.output, expected='{"id": "xx", "createDateUtc": "2025-04-10T14:09:00.9954070"}\n'
        )

    def test_tenants_transform_tenant_name(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        pook.get(
            XERO_CONNECTIONS_URL,
            reply=200,
            response_json=[
                {'id': 't1', 'tenantName': 'Tenant 1'},
                {'id': 't2', 'tenantName': 'Tenant 2'},
            ],
        )

        result = run_cli(tmp_path, 'tenants', '-f', 'tenantName')

        mock_credentials_from_file.assert_called_once_with(tmp_path)
        compare(result.output, expected='Tenant 1\nTenant 2\n')

    def test_tenants_transform_pretty(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        pook.get(
            XERO_CONNECTIONS_URL,
            reply=200,
            response_json=[
                {
                    'id': 't1',
                    'tenantName': 'Tenant 1',
                    "createDateUtc": "2025-04-10T14:09:00.9954070",
                },
                {
                    'id': 't2',
                    'tenantName': 'Tenant 2',
                    "createDateUtc": "2025-04-11T14:09:00.9954070",
                },
            ],
        )

        result = run_cli(tmp_path, 'tenants', '-t', 'pretty')

        mock_credentials_from_file.assert_called_once_with(tmp_path)
        compare(
            result.output,
            expected=dedent("""\
                {'createDateUtc': '2025-04-10T14:09:00.9954070',
                 'id': 't1',
                 'tenantName': 'Tenant 1'}
                {'createDateUtc': '2025-04-11T14:09:00.9954070',
                 'id': 't2',
                 'tenantName': 'Tenant 2'}
         """),
        )


class TestLogLevel:
    @pytest.fixture(autouse=True)
    def mocks(self) -> Iterator[Mock]:
        mocks_ = Mock()
        mocks_.basicConfig = Mock(spec=logging.basicConfig)
        mocks_.credentials_from_file = Mock(spec=credentials_from_file)
        mocks_.show = Mock(spec=show)
        with Replacer() as replace:
            replace.in_module(logging.basicConfig, mocks_.basicConfig)
            replace.in_module(credentials_from_file, mocks_.credentials_from_file, module=main)
            replace.in_module(show, mocks_.show, module=main)
            yield mocks_

    def test_log_level_option(self, tmp_path: Path, mocks: Mock) -> None:
        run_cli(tmp_path, '--log-level', 'DEBUG', 'tenants')
        mocks.basicConfig.assert_called_once_with(level=logging.DEBUG)

    def test_log_level_shorthand(self, tmp_path: Path, mocks: Mock) -> None:
        run_cli(tmp_path, '-l', 'WARNING', 'tenants')
        mocks.basicConfig.assert_called_once_with(level=logging.WARNING)


class TestExplore:
    def test_explore_simple(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        pook.get(
            XERO_CONNECTIONS_URL,
            reply=200,
            response_json=[
                {'tenantId': 't1', 'tenantName': 'Tenant 1'},
                {'tenantId': 't2', 'tenantName': 'Tenant 2'},
            ],
        )
        pook.get(
            XERO_CONTACTS_URL,
            reply=200,
            response_json={
                'Status': 'OK',
                'Contacts': [{'ContactID': 'c1', 'Name': 'Contact 1'}],
            },
        )
        result = run_cli(tmp_path, 'explore', 'contacts')
        mock_credentials_from_file.assert_called_once_with(tmp_path)
        compare(result.output, expected='{"ContactID": "c1", "Name": "Contact 1"}\n')

    def test_explore_explicit_tenant_id(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        pook.get(
            XERO_CONTACTS_URL,
            headers={'Xero-Tenant-Id': 't2'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Contacts': [{'ContactID': 'c2', 'Name': 'Contact 2'}],
            },
        )
        result = run_cli(tmp_path, 'explore', 'Contacts', '--tenant', 't2')
        mock_credentials_from_file.assert_called_once_with(tmp_path)
        compare(result.output, expected='{"ContactID": "c2", "Name": "Contact 2"}\n')

    def test_explore_with_entity_id(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            f"{XERO_CONTACTS_URL}/c3",
            reply=200,
            response_json={
                'Status': 'OK',
                'Contacts': [{'ContactID': 'c3', 'Name': 'Contact 3'}],
            },
        )
        result = run_cli(tmp_path, 'explore', 'Contacts', '--id', 'c3')
        compare(result.output, expected='{"ContactID": "c3", "Name": "Contact 3"}\n')

    def test_explore_with_since(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            XERO_JOURNALS_URL,
            headers={'If-Modified-Since': "Sun, 20 Apr 2025 00:00:00 GMT"},
            reply=200,
            response_json={
                'Status': 'OK',
                'Journals': [{'JournalID': 'j1', 'JournalNumber': 1}],
            },
        )
        result = run_cli(tmp_path, 'explore', 'journals', '--since', '2025-04-20')
        compare(result.output, expected='{"JournalID": "j1", "JournalNumber": 1}\n')

    def test_explore_with_offset(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            XERO_JOURNALS_URL,
            params={'offset': '100'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Journals': [{'JournalID': 'j101', 'JournalNumber': 101}],
            },
        )
        result = run_cli(tmp_path, 'explore', 'Journals', '--offset', '100')
        compare(result.output, expected='{"JournalID": "j101", "JournalNumber": 101}\n')

    def test_explore_with_field(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            XERO_CONTACTS_URL,
            reply=200,
            response_json={
                'Status': 'OK',
                'Contacts': [
                    {'ContactID': 'c1', 'Name': 'Contact 1'},
                    {'ContactID': 'c2', 'Name': 'Contact 2'},
                ],
            },
        )
        result = run_cli(tmp_path, 'explore', 'contacts', '-f', 'Name', '-n')
        compare(result.output, expected='Contact 1\nContact 2\n')

    def test_explore_with_transform(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            XERO_CONTACTS_URL,
            reply=200,
            response_json={
                'Status': 'OK',
                'Contacts': [
                    {'ContactID': 'c1', 'Name': 'Contact 1'},
                    {'ContactID': 'c2', 'Name': 'Contact 2'},
                ],
            },
        )
        result = run_cli(tmp_path, 'explore', 'contacts', '-t', 'pretty')
        compare(
            result.output,
            expected=dedent("""\
                {'ContactID': 'c1', 'Name': 'Contact 1'}
                {'ContactID': 'c2', 'Name': 'Contact 2'}
            """),
        )

    def test_explore_with_date_and_datetime_in_json(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            XERO_CONTACTS_URL,
            reply=200,
            response_json={
                'Status': 'OK',
                'Contacts': [
                    {
                        'ContactID': 'c1',
                        'Name': 'Contact 1',
                        # Represents 2023-03-15T13:20:00+00:00, pyxero turns this into a datetime:
                        'CreatedDateUTC': '/Date(1678886400000+0000)/',
                    }
                ],
            },
        )
        result = run_cli(tmp_path, 'explore', 'contacts', '-t', 'json')
        # Our XeroEncoder should serialize date/datetime back to ISO format
        compare(
            result.output,
            expected=(
                '{"ContactID": "c1", "Name": "Contact 1", '
                '"CreatedDateUTC": "2023-03-15T13:20:00+00:00"}\n'
            ),
        )


class TestExport:
    def test_all_endpoints_single_tenant(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Accounts",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={'Status': 'OK', 'Accounts': [{'AccountID': 'a1', 'Name': 'Acc 1'}]},
        )
        pook.get(
            f"{XERO_API_URL}/Contacts",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={'Status': 'OK', 'Contacts': [{'ContactID': 'c1', 'Name': 'Cont 1'}]},
        )
        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Journals': [],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path))

        check_files(
            {
                'Tenant 1/accounts.jsonl': '{"AccountID": "a1", "Name": "Acc 1"}\n',
                'Tenant 1/contacts.jsonl': '{"ContactID": "c1", "Name": "Cont 1"}\n',
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
            }
        )

    def test_specific_endpoint_multiple_tenants(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        add_tenants_response(
            pook,
            [
                {'tenantId': 't1', 'tenantName': 'Tenant 1'},
                {'tenantId': 't2', 'tenantName': 'Tenant 2'},
            ],
        )
        pook.get(
            f"{XERO_API_URL}/Contacts",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={'Status': 'OK', 'Contacts': [{'ContactID': 'c1', 'Name': 'Cont 1'}]},
        )
        pook.get(
            f"{XERO_API_URL}/Contacts",
            headers={'Xero-Tenant-Id': 't2'},
            reply=200,
            response_json={'Status': 'OK', 'Contacts': [{'ContactID': 'c2', 'Name': 'Cont 2'}]},
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), 'contacts')

        check_files(
            {
                'Tenant 1/contacts.jsonl': '{"ContactID": "c1", "Name": "Cont 1"}\n',
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 2/contacts.jsonl': '{"ContactID": "c2", "Name": "Cont 2"}\n',
                'Tenant 2/tenant.json': '{"tenantId": "t2", "tenantName": "Tenant 2"}\n',
            },
        )

    def test_journals_uses_journals_export(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Journals': [
                    {
                        'JournalID': 'j1',
                        'JournalDate': '/Date(1678838400000+0000)/',  # 2023-03-15
                        'JournalNumber': 1,
                    },
                    {
                        'JournalID': 'j2',
                        'JournalDate': '/Date(1678924800000+0000)/',  # 2023-03-16
                        'JournalNumber': 2,
                    },
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': 't1'},
            params={'offset': '2'},
            reply=200,
            response_json={'Status': 'OK', 'Journals': []},
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'journals')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/journals-2023-03.jsonl': (
                    '{"JournalID": "j1", "JournalDate": "2023-03-15T00:00:00+00:00", "JournalNumber": 1}\n'
                    '{"JournalID": "j2", "JournalDate": "2023-03-16T00:00:00+00:00", "JournalNumber": 2}\n'
                ),
            }
        )

    def test_journals_with_rate_limit(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        # First request hits rate limit
        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': 't1'},
            reply=429,  # Rate limit exceeded
            response_headers={'retry-after': '1'},  # Server responds with retry-after header
        )

        # Second request (after retry) succeeds
        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': 't1'},
            params={'offset': '0'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Journals': [
                    {
                        'JournalID': 'j1',
                        'JournalDate': '/Date(1681948800000+0000)/',
                        'JournalNumber': 1,
                    },
                ],
            },
        )

        # End of pagination
        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': 't1'},
            params={'offset': '1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Journals': [],
            },
        )

        # Mock the sleep function to avoid actually waiting
        mock_sleep = Mock()

        with replace_in_module(time.sleep, mock_sleep, module=export):
            # Run the export command for journals only
            run_cli(tmp_path, 'export', 'journals', '--path', str(tmp_path))

        # Verify sleep was called with retry-after value
        mock_sleep.assert_called_once_with(1)

        # Verify the journal was exported after retrying
        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/journals-2023-04.jsonl': (
                    '{"JournalID": "j1", "JournalDate": "2023-04-20T00:00:00+00:00", "JournalNumber": 1}\n'
                ),
            }
        )

    def setup_journal_mocks(self, pook: Any, tenant_id: str = 't1') -> None:
        """Helper to set up common pook mocks for journal exports."""
        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': tenant_id},
            reply=200,
            response_json={
                'Status': 'OK',
                'Journals': [
                    {
                        'JournalID': 'j1',
                        'JournalDate': '/Date(1678838400000+0000)/',  # 2023-03-15
                        'JournalNumber': 1,
                    },
                    {
                        'JournalID': 'j2',
                        'JournalDate': '/Date(1678924800000+0000)/',  # 2023-03-16
                        'JournalNumber': 2,
                    },
                    {
                        'JournalID': 'j3',
                        'JournalDate': '/Date(1710460800000+0000)/',  # 2024-03-15
                        'JournalNumber': 3,
                    },
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': tenant_id},
            params={'offset': '3'},
            reply=200,
            response_json={'Status': 'OK', 'Journals': []},
        )

    def test_journals_split_days(self, tmp_path: Path, pook: Any, check_files: FileChecker) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])
        self.setup_journal_mocks(pook)

        run_cli(
            tmp_path,
            'export',
            '--path',
            str(tmp_path),
            '--tenant',
            't1',
            'journals',
            '--split',
            'days',
        )

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/journals-2023-03-15.jsonl': (
                    '{"JournalID": "j1", "JournalDate": "2023-03-15T00:00:00+00:00", "JournalNumber": 1}\n'
                ),
                'Tenant 1/journals-2023-03-16.jsonl': (
                    '{"JournalID": "j2", "JournalDate": "2023-03-16T00:00:00+00:00", "JournalNumber": 2}\n'
                ),
                'Tenant 1/journals-2024-03-15.jsonl': (
                    '{"JournalID": "j3", "JournalDate": "2024-03-15T00:00:00+00:00", "JournalNumber": 3}\n'
                ),
            }
        )

    def test_journals_split_months(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])
        self.setup_journal_mocks(pook)

        run_cli(
            tmp_path,
            'export',
            '--path',
            str(tmp_path),
            '--tenant',
            't1',
            'journals',
            '--split',
            'months',
        )

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/journals-2023-03.jsonl': (
                    '{"JournalID": "j1", "JournalDate": "2023-03-15T00:00:00+00:00", "JournalNumber": 1}\n'
                    '{"JournalID": "j2", "JournalDate": "2023-03-16T00:00:00+00:00", "JournalNumber": 2}\n'
                ),
                'Tenant 1/journals-2024-03.jsonl': (
                    '{"JournalID": "j3", "JournalDate": "2024-03-15T00:00:00+00:00", "JournalNumber": 3}\n'
                ),
            }
        )

    def test_journals_split_years(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])
        self.setup_journal_mocks(pook)

        run_cli(
            tmp_path,
            'export',
            '--path',
            str(tmp_path),
            '--tenant',
            't1',
            'journals',
            '--split',
            'years',
        )

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/journals-2023.jsonl': (
                    '{"JournalID": "j1", "JournalDate": "2023-03-15T00:00:00+00:00", "JournalNumber": 1}\n'
                    '{"JournalID": "j2", "JournalDate": "2023-03-16T00:00:00+00:00", "JournalNumber": 2}\n'
                ),
                'Tenant 1/journals-2024.jsonl': (
                    '{"JournalID": "j3", "JournalDate": "2024-03-15T00:00:00+00:00", "JournalNumber": 3}\n'
                ),
            }
        )


class TestJournalsCheck:
    def write_journal_file(self, path: Path, journals: list[dict[str, Any]]) -> None:
        """Helper to write a JSON Lines file."""
        path.write_text('\n'.join(json.dumps(j) for j in journals) + '\n')

    def test_check_success_single_file(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals.jsonl"
        journals_data = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalDate": "2025-01-15T10:00:00",
                "CreatedDateUTC": "2025-01-15T10:00:00Z",
            },
            {
                "JournalID": "j2",
                "JournalNumber": 2,
                "JournalDate": "2025-01-16T11:00:00",
                "CreatedDateUTC": "2025-01-16T11:00:00Z",
            },
            {
                "JournalID": "j3",
                "JournalNumber": 3,
                "JournalDate": "2025-01-17T12:00:00",
                "CreatedDateUTC": "2025-01-17T12:00:00Z",
            },
        ]
        self.write_journal_file(journal_file, journals_data)

        result = run_cli(tmp_path, 'journals', 'check', str(journal_file))

        compare(
            result.output,
            expected=dedent("""\
                 entries: 3
           JournalNumber: 1 -> 3
             JournalDate: 2025-01-15T10:00:00 -> 2025-01-17T12:00:00
          CreatedDateUTC: 2025-01-15T10:00:00Z -> 2025-01-17T12:00:00Z
        """),
        )

    def test_check_success_multiple_files(self, tmp_path: Path) -> None:
        file1 = tmp_path / "journals-1.jsonl"
        file2 = tmp_path / "journals-2.jsonl"
        journals1 = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalDate": "2025-01-15T10:00:00",
                "CreatedDateUTC": "2025-01-15T10:00:00Z",
            },
            {
                "JournalID": "j3",
                "JournalNumber": 3,
                "JournalDate": "2025-01-17T10:00:00",
                "CreatedDateUTC": "2025-01-17T10:00:00Z",
            },
        ]
        journals2 = [
            {
                "JournalID": "j2",
                "JournalNumber": 2,
                "JournalDate": "2025-01-16T11:00:00",
                "CreatedDateUTC": "2025-01-16T11:00:00Z",
            }
        ]
        self.write_journal_file(file1, journals1)
        self.write_journal_file(file2, journals2)

        result = run_cli(tmp_path, 'journals', 'check', str(file1), str(file2))

        compare(
            result.output,
            expected=dedent("""\
                 entries: 3
           JournalNumber: 1 -> 3
             JournalDate: 2025-01-15T10:00:00 -> 2025-01-17T10:00:00
          CreatedDateUTC: 2025-01-15T10:00:00Z -> 2025-01-17T10:00:00Z
        """),
        )

    def test_check_duplicate_id(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals_dup_id.jsonl"
        journals_data = [
            {"JournalID": "j1", "JournalNumber": 1},
            {"JournalID": "j1", "JournalNumber": 2},
        ]
        self.write_journal_file(journal_file, journals_data)

        with ShouldRaise(
            ExceptionGroup(
                "Journal validation errors",
                (ValueError("Duplicate JournalID found: j1"),),
            )
        ):
            run_cli(tmp_path, 'journals', 'check', str(journal_file), expected_return_code=1)

    def test_check_duplicate_number(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals_dup_num.jsonl"
        journals_data = [
            {"JournalID": "j1", "JournalNumber": 1},
            {"JournalID": "j2", "JournalNumber": 1},
        ]
        self.write_journal_file(journal_file, journals_data)

        with ShouldRaise(
            ExceptionGroup(
                "Journal validation errors",
                (ValueError("Duplicate JournalNumber found: 1"),),
            )
        ):
            run_cli(tmp_path, 'journals', 'check', str(journal_file), expected_return_code=1)

    def test_check_missing_number(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals_missing_num.jsonl"
        journals_data = [
            {"JournalID": "j1", "JournalNumber": 1},
            {"JournalID": "j3", "JournalNumber": 3},
        ]
        self.write_journal_file(journal_file, journals_data)

        with ShouldRaise(
            ExceptionGroup(
                "Journal validation errors",
                (ValueError("Missing JournalNumbers: 2"),),
            )
        ):
            run_cli(tmp_path, 'journals', 'check', str(journal_file), expected_return_code=1)

    def test_check_missing_number_range(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals_missing_range.jsonl"
        journals_data = [
            {"JournalID": "j1", "JournalNumber": 1},
            {"JournalID": "j5", "JournalNumber": 5},
        ]
        self.write_journal_file(journal_file, journals_data)

        with ShouldRaise(
            ExceptionGroup(
                "Journal validation errors",
                (ValueError("Missing JournalNumbers: 2-4"),),
            )
        ):
            run_cli(tmp_path, 'journals', 'check', str(journal_file), expected_return_code=1)

    def test_check_combined_errors(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals_combined_errors.jsonl"
        journals_data = [
            {"JournalID": "j1", "JournalNumber": 1},
            {"JournalID": "j1", "JournalNumber": 2},  # Duplicate ID
            {"JournalID": "j3", "JournalNumber": 2},  # Duplicate Number
            {"JournalID": "j5", "JournalNumber": 5},  # Missing 4
        ]
        self.write_journal_file(journal_file, journals_data)

        # Errors are sorted alphabetically by message in check_journals before raising
        with ShouldRaise(
            ExceptionGroup(
                "Journal validation errors",
                (
                    ValueError("Duplicate JournalID found: j1"),
                    ValueError("Duplicate JournalNumber found: 2"),
                    ValueError("Missing JournalNumbers: 3-4"),
                ),
            )
        ):
            run_cli(tmp_path, 'journals', 'check', str(journal_file), expected_return_code=1)

    def test_check_empty_file(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "empty.jsonl"
        journal_file.touch()

        result = run_cli(tmp_path, 'journals', 'check', str(journal_file))
        compare(
            result.output,
            expected=dedent("""\
                 entries: 0
           JournalNumber: None -> None
             JournalDate: None -> None
          CreatedDateUTC: None -> None
        """),
        )

    def test_check_single_entry(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "single.jsonl"
        journals_data = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalDate": "2025-01-15T10:00:00",
                "CreatedDateUTC": "2025-01-15T10:00:00Z",
            }
        ]
        self.write_journal_file(journal_file, journals_data)

        result = run_cli(tmp_path, 'journals', 'check', str(journal_file))
        compare(
            result.output,
            expected=dedent("""\
                 entries: 1
           JournalNumber: 1 -> 1
             JournalDate: 2025-01-15T10:00:00 -> 2025-01-15T10:00:00
          CreatedDateUTC: 2025-01-15T10:00:00Z -> 2025-01-15T10:00:00Z
        """),
        )


class TestJournalsFlatten:
    def write_journal_file(self, path: Path, journals: list[dict[str, Any]]) -> None:
        """Helper to write a JSON Lines file."""
        path.write_text('\n'.join(json.dumps(j) for j in journals) + '\n')

    def check_output(self, output: str, *, expected: Sequence[dict[str, Any]]) -> None:
        expected_lines = [','.join(ALL_JOURNAL_KEYS)]
        for row in expected:
            expected_lines.append(','.join(str(row.get(k, '')) for k in ALL_JOURNAL_KEYS))
        compare(output, expected='\n'.join(expected_lines) + '\n')

    def test_flatten_single_file(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals.jsonl"
        journals_data = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalDate": "2025-01-15T00:00:00",
                "JournalLines": [
                    {"JournalLineID": "jl1a", "AccountCode": "100", "NetAmount": 10.0},
                    {"JournalLineID": "jl1b", "AccountCode": "200", "NetAmount": -10.0},
                ],
            },
            {
                "JournalID": "j2",
                "JournalNumber": 2,
                "JournalDate": "2025-01-16T00:00:00",
                "JournalLines": [
                    {"JournalLineID": "jl2a", "AccountCode": "300", "NetAmount": 20.0}
                ],
            },
        ]
        self.write_journal_file(journal_file, journals_data)

        result = run_cli(tmp_path, 'journals', 'flatten', str(journal_file))

        # We don't use check_output here so we can see what the raw csv looks like,
        header = ','.join(ALL_JOURNAL_KEYS)
        expected_csv = dedent(f"""\
            {header}
            j1,2025-01-15T00:00:00,1,,jl1a,,100,,,,10.0,,,,,,,,
            j1,2025-01-15T00:00:00,1,,jl1b,,200,,,,-10.0,,,,,,,,
            j2,2025-01-16T00:00:00,2,,jl2a,,300,,,,20.0,,,,,,,,
        """)
        compare(result.output, expected=expected_csv)

    def test_flatten_multiple_files(self, tmp_path: Path) -> None:
        file1 = tmp_path / "journals1.jsonl"
        file2 = tmp_path / "journals2.jsonl"
        journals_data1 = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalLines": [{"JournalLineID": "jl1a"}],
            }
        ]
        journals_data2 = [
            {
                "JournalID": "j2",
                "JournalNumber": 2,
                "JournalLines": [{"JournalLineID": "jl2a"}],
            }
        ]
        self.write_journal_file(file1, journals_data1)
        self.write_journal_file(file2, journals_data2)

        result = run_cli(tmp_path, 'journals', 'flatten', str(file1), str(file2))

        expected_rows = [
            {'JournalID': 'j1', 'JournalNumber': 1, 'JournalLineID': 'jl1a'},
            {'JournalID': 'j2', 'JournalNumber': 2, 'JournalLineID': 'jl2a'},
        ]
        self.check_output(result.output, expected=expected_rows)

    def test_flatten_empty_file(self, tmp_path: Path) -> None:
        empty_file = tmp_path / "empty.jsonl"
        empty_file.touch()

        result = run_cli(tmp_path, 'journals', 'flatten', str(empty_file))

        self.check_output(result.output, expected=[])

    def test_flatten_file_with_no_journal_lines(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "no_lines.jsonl"
        journals_data = [
            {"JournalID": "j1", "JournalNumber": 1, "JournalLines": []},
            {"JournalID": "j2", "JournalNumber": 2},  # JournalLines key missing
        ]
        self.write_journal_file(journal_file, journals_data)

        result = run_cli(tmp_path, 'journals', 'flatten', str(journal_file))

        self.check_output(result.output, expected=[])

    def test_flatten_file_with_some_journal_lines_empty(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "some_lines_empty.jsonl"
        journals_data = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalLines": [{"JournalLineID": "jl1a", "AccountCode": "100"}],
            },
            {"JournalID": "j2", "JournalNumber": 2, "JournalLines": []},  # Empty JournalLines
            {
                "JournalID": "j3",
                "JournalNumber": 3,
                # JournalLines key missing
            },
            {
                "JournalID": "j4",
                "JournalNumber": 4,
                "JournalLines": [{"JournalLineID": "jl4a", "AccountCode": "400"}],
            },
        ]
        self.write_journal_file(journal_file, journals_data)

        result = run_cli(tmp_path, 'journals', 'flatten', str(journal_file))

        expected_rows = [
            {
                'JournalID': 'j1',
                'JournalNumber': 1,
                'JournalLineID': 'jl1a',
                'AccountCode': '100',
            },
            {
                'JournalID': 'j4',
                'JournalNumber': 4,
                'JournalLineID': 'jl4a',
                'AccountCode': '400',
            },
        ]
        self.check_output(result.output, expected=expected_rows)

    def test_flatten_to_output_file(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals.jsonl"
        output_csv_file = tmp_path / "output.csv"
        journals_data = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalLines": [{"JournalLineID": "jl1a", "AccountCode": "100"}],
            }
        ]
        self.write_journal_file(journal_file, journals_data)

        run_cli(
            tmp_path,
            'journals',
            'flatten',
            str(journal_file),
            '--output',
            str(output_csv_file),
        )

        expected_rows = [
            {'JournalID': 'j1', 'JournalNumber': 1, 'JournalLineID': 'jl1a', 'AccountCode': '100'}
        ]
        self.check_output(output_csv_file.read_text(), expected=expected_rows)

    def test_flatten_with_tracking_categories(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals_with_tracking.jsonl"
        journals_data = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalDate": "2025-01-15T00:00:00",
                "JournalLines": [
                    {
                        "JournalLineID": "jl1a",
                        "AccountCode": "100",
                        "NetAmount": 10.0,
                        "TrackingCategories": ["Region A", "Project X"],
                        "Reference": {'one': 1, 'aye': 'A'},
                    }
                ],
            }
        ]
        self.write_journal_file(journal_file, journals_data)

        result = run_cli(tmp_path, 'journals', 'flatten', str(journal_file))

        expected_rows = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalDate": "2025-01-15T00:00:00",
                "JournalLineID": "jl1a",
                "AccountCode": "100",
                "NetAmount": 10.0,
                "TrackingCategories": '"[""Region A"", ""Project X""]"',
                "Reference": '"{""one"": 1, ""aye"": ""A""}"',
            }
        ]
        self.check_output(result.output, expected=expected_rows)
