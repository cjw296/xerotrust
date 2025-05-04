import json
import logging
import time
from pathlib import Path
from textwrap import dedent
from typing import Any, Iterator
from unittest.mock import Mock

import pytest
from click.testing import CliRunner, Result
from testfixtures import compare, replace_in_module, mock_time, Replacer
from xero.auth import OAuth2PKCECredentials

from xerotrust import export
from xerotrust import main
from xerotrust.authentication import authenticate, SCOPES, credentials_from_file
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

        mock = mock_time(delta=0)

        with replace_in_module(time, mock, module=time):
            run_cli(auth_path, 'login', '--client-id', 'ID')

        compare(
            expected={
                'client_id': 'CLIENT_ID',
                'client_secret': 'FOO',
                'token': {
                    'access_token': 'test_token',
                    'expires_in': 3600,
                    'expires_at': mock() + 3600,
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
