from asyncio import Event
from contextvars import ContextVar
from typing import Iterator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from testfixtures import Replace
from xero.auth import OAuth2PKCECredentials

from xerotrust import authentication as authentication_module
from xerotrust.authentication import app, credentials_context, shutdown_event

XERO_TOKEN_URL = "https://identity.xero.com/connect/token"


@pytest.fixture()
def client() -> TestClient:
    """Provides a TestClient instance for the FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_credentials() -> Iterator[MagicMock]:
    """Provides a mock OAuth2PKCECredentials object and manages its context."""
    credentials = MagicMock(spec=OAuth2PKCECredentials)
    credentials.state = {"auth_state": "test_state_123"}
    credentials.get_token.return_value = None
    mock_context = ContextVar("credentials")
    mock_context.set(credentials)
    with Replace(
        credentials_context,
        mock_context,
        container=authentication_module,
        name="credentials_context",
    ):
        yield credentials


@pytest.fixture(autouse=True)
def mock_shutdown_event() -> Iterator[Event]:
    mock_event = Event()
    with Replace(
        shutdown_event,
        mock_event,
        container=authentication_module,
        name="shutdown_event",
    ):
        yield mock_event


def test_callback_success(
    client: TestClient, mock_credentials: MagicMock, mock_shutdown_event: Event
) -> None:
    code = "valid_code"

    response = client.get(f"/?code={code}&state={mock_credentials.state['auth_state']}")

    assert response.status_code == 200
    assert "Authentication Success" in response.text
    mock_credentials.get_token.assert_called_once_with(code)
    assert mock_shutdown_event.is_set(), "Shutdown event was not set after response"


def test_callback_state_mismatch(
    client: TestClient, mock_credentials: MagicMock, mock_shutdown_event: Event
) -> None:
    test_code = "valid_code"
    invalid_state = "invalid_state_456"

    response = client.get(f"/?code={test_code}&state={invalid_state}")

    assert response.status_code == 500
    message = (
        "Unexpected state: expected=&#39;test_state_123&#39;, actual=&#39;invalid_state_456&#39;"
    )
    assert message in response.text
    mock_credentials.get_token.assert_not_called()
    assert mock_shutdown_event.is_set()


def test_callback_error_parameter(
    client: TestClient, mock_credentials: MagicMock, mock_shutdown_event: Event
) -> None:
    error_message = "access_denied"

    response = client.get(f"/?error={error_message}&state=some_state")

    assert response.status_code == 500
    assert 'access_denied' in response.text
    mock_credentials.get_token.assert_not_called()
    assert mock_shutdown_event.is_set()
