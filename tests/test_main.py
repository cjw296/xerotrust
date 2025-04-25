import json
import time
from pathlib import Path
from textwrap import dedent
from typing import Any, Iterator
from unittest.mock import Mock

import pytest
from click.testing import CliRunner, Result
from testfixtures import compare, replace_in_module, mock_time
from xero.auth import OAuth2PKCECredentials

from xerotrust import main
from xerotrust.authentication import authenticate, SCOPES, credentials_from_file
from xerotrust.main import cli

XERO_CONNECTIONS_URL = "https://api.xero.com/connections"


def run_cli(
    auth_path: Path, *args: str, input: str | None = None, expected_return_code: int = 0
) -> Result:
    args_ = ['--auth', str(auth_path)]
    args_.extend(args)
    result = CliRunner().invoke(cli, args_, catch_exceptions=False, input=input)
    compare(result.exit_code, expected=expected_return_code, suffix=result.output)
    return result


def check_auth_file(auth_path: Path) -> None:
    compare(
        expected={
            'client_id': 'CLIENT_ID',
            'client_secret': 'FOO',
            'token': {'access_token': 'test_token'},
        },
        actual=json.loads(auth_path.read_text()),
    )


def add_tenants_response(pook: Any) -> None:
    pook.get(
        XERO_CONNECTIONS_URL,
        reply=200,
        response_json=[{'id': 't1', 'tenantName': 'Tenant 1'}],
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

        result = run_cli(tmp_path, 'tenants', '-t', 'tenant')

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
