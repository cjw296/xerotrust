import json
import time
from pathlib import Path
from typing import Iterator, Any
from unittest.mock import Mock

import pytest
from testfixtures import compare, replace_in_module, mock_time
from testfixtures.datetime import MockTime

from xerotrust import main
from xerotrust.authentication import authenticate

from .helpers import (
    SAMPLE_CREDENTIALS,
    add_tenants_response,
    run_cli,
)


def check_auth_file(auth_path: Path) -> None:
    compare(
        expected={
            "client_id": "CLIENT_ID",
            "client_secret": "FOO",
            "token": {"access_token": "test_token"},
        },
        actual=json.loads(auth_path.read_text()),
    )


pytestmark = pytest.mark.usefixtures("mock_credentials_from_file")


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
        auth_path = tmp_path / ".xerotrust.json"
        add_tenants_response(pook)

        result = run_cli(auth_path, "login", "--client-id", "test_client_id_option")

        mock_authenticate.assert_called_once_with("test_client_id_option")
        check_auth_file(auth_path)
        compare(result.output, expected="\nAvailable tenants:\n- t1: Tenant 1\n")

    def test_login_prompt_for_client_id(
        self, mock_authenticate: Mock, tmp_path: Path, pook: Any
    ) -> None:
        auth_path = tmp_path / ".xerotrust.json"
        add_tenants_response(pook)

        result = run_cli(auth_path, "login", input="test_client_id_prompt\n")

        compare(
            result.output,
            expected="Client ID: \n\nAvailable tenants:\n- t1: Tenant 1\n",
        )
        mock_authenticate.assert_called_once_with("test_client_id_prompt")
        check_auth_file(auth_path)

    def test_login_client_id_from_auth_file(
        self, mock_authenticate: Mock, tmp_path: Path, pook: Any
    ) -> None:
        auth_path = tmp_path / ".xerotrust.json"
        add_tenants_response(pook)
        auth_path.write_text(json.dumps({"client_id": "existing_client_id"}))

        result = run_cli(auth_path, "login", input="\n")

        compare(
            result.output,
            expected="Client ID: \n\nAvailable tenants:\n- t1: Tenant 1\n",
        )
        mock_authenticate.assert_called_once_with("existing_client_id")
        check_auth_file(auth_path)

    def test_login_no_client_id(self, mock_authenticate: Mock, tmp_path: Path) -> None:
        auth_path = tmp_path / ".xerotrust.json"

        result = run_cli(auth_path, "login", input="\n", expected_return_code=1)

        compare(
            result.output,
            expected=f"Client ID: \nError: No Client ID provided or found in {auth_path}.\n",
        )
        mock_authenticate.assert_not_called()
        assert not auth_path.exists()

    def test_login_with_expires_in(
        self, mock_authenticate: Mock, tmp_path: Path, pook: Any
    ) -> None:
        """Test the login command calculates expires_at from expires_in."""
        auth_path = tmp_path / ".xerotrust.json"
        add_tenants_response(pook)

        mock_authenticate.return_value.token = {
            "access_token": "test_token",
            "expires_in": 3600,
        }

        mock: type[MockTime] = mock_time(delta=0)

        with replace_in_module(time.time, mock):
            run_cli(auth_path, "login", "--client-id", "ID")

        current_time = mock()
        compare(
            expected={
                "client_id": "CLIENT_ID",
                "client_secret": "FOO",
                "token": {
                    "access_token": "test_token",
                    "expires_in": 3600,
                    "expires_at": current_time + 3600,
                },
            },
            actual=json.loads(auth_path.read_text()),
        )

    def test_login_preserves_expires_at(
        self, mock_authenticate: Mock, tmp_path: Path, pook: Any
    ) -> None:
        expires_at = 1234.0
        auth_path = tmp_path / ".xerotrust.json"
        add_tenants_response(pook)

        mock_authenticate.return_value.token = {
            "access_token": "test_token",
            "expires_in": 3600,
            "expires_at": expires_at,
        }

        run_cli(auth_path, "login", "--client-id", "ID")

        compare(
            json.loads(auth_path.read_text())["token"]["expires_at"],
            expected=expires_at,
        )
