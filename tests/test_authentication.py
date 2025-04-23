import asyncio
import webbrowser
from asyncio import Event
from contextvars import ContextVar
from socket import socket
from typing import Iterator, Any
from unittest.mock import MagicMock, Mock, call

import httpx
import pytest
from fastapi.testclient import TestClient
from oauthlib.common import generate_token
from requests_oauthlib import oauth2_session
from testfixtures import (
    Replace,
    replace_in_module,
    compare,
    Comparison,
    StringComparison,
    Replacer,
    ShouldRaise,
)
from xero.auth import OAuth2PKCECredentials
from xero.constants import XERO_OAUTH2_AUTHORIZE_URL, XERO_OAUTH2_TOKEN_URL

from xerotrust import authentication as authentication_module
from xerotrust.authentication import (
    app,
    credentials_context,
    shutdown_event,
    _authenticate,
    authenticate,
    SCOPES,
)
from xerotrust.exceptions import XeroAPIException

XERO_TOKEN_URL = "https://identity.xero.com/connect/token"


@pytest.fixture()
def client() -> TestClient:
    """Provides a TestClient instance for the FastAPI app."""
    return TestClient(app)


@pytest.fixture()
def mock_credentials() -> Iterator[MagicMock]:
    """Provides a mock OAuth2PKCECredentials object and manages its context."""
    credentials = MagicMock(spec=OAuth2PKCECredentials)
    credentials.state = {"auth_state": "test_state_123"}
    credentials.get_token.return_value = None
    mock_context = ContextVar[MagicMock]("credentials")
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
    assert "access_denied" in response.text
    mock_credentials.get_token.assert_not_called()
    assert mock_shutdown_event.is_set()


@pytest.fixture()
def port() -> int:
    s = socket()
    s.bind(("127.0.0.1", 0))
    _, port = s.getsockname()
    return int(port)


@pytest.mark.asyncio
async def test_async_authenticate_success(
    pook: Any, port: int, capsys: pytest.CaptureFixture[str]
) -> None:
    pook.enable_network("127.0.0.1")
    secret = "EXAMPLE_CLIENT_SECRET"
    mock_open = Mock()
    (
        pook.post(XERO_OAUTH2_TOKEN_URL)
        .body(
            pook.regex(
                f"grant_type=authorization_code&client_id={secret}"
                f"&redirect_uri=http%3A%2F%2F127.0.0.1%3A{port}%2F"
                f"&code=test_code.+"
            )
        )
        .reply(200)
        .json({"access_token": "mock_token"})
    )
    with (
        replace_in_module(webbrowser.open, mock_open),
        # Make sure we get a stable state token:
        replace_in_module(generate_token, lambda: "mock_token", module=oauth2_session),
    ):
        task = asyncio.create_task(_authenticate(secret, host="127.0.0.1", port=port))
        await asyncio.sleep(0.1)
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://127.0.0.1:{port}/?code=test_code&state=mock_token")
        result = await asyncio.wait_for(task, timeout=1)

    mock_open.assert_called_once_with(StringComparison(XERO_OAUTH2_AUTHORIZE_URL + ".+"))
    compare(response.status_code, expected=200, suffix=response.text)
    compare(
        result,
        expected=Comparison(
            OAuth2PKCECredentials,
            auth_state="mock_token",
            scope=SCOPES,
            client_secret="PLACEHOLDER",
            client_id=secret,
            port=port,
            callback_uri=f"http://127.0.0.1:{port}/",
            token={"access_token": "mock_token"},
            partial=True,
        ),
    )

    assert XERO_OAUTH2_AUTHORIZE_URL in capsys.readouterr().out


@pytest.mark.asyncio
async def test_async_authenticate_failure(
    pook: Any, port: int, capsys: pytest.CaptureFixture[str]
) -> None:
    pook.enable_network("127.0.0.1")
    secret = "EXAMPLE_CLIENT_SECRET"
    mock_open = Mock()
    with (
        replace_in_module(webbrowser.open, mock_open),
        # Make sure we get a stable state token:
        replace_in_module(generate_token, lambda: "mock_token", module=oauth2_session),
    ):
        task = asyncio.create_task(_authenticate(secret, host="127.0.0.1", port=port))
        await asyncio.sleep(0.1)
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://127.0.0.1:{port}/?error=unauth&state=mock_token")
        with ShouldRaise(XeroAPIException("Authentication failed, see browser window")):
            await asyncio.wait_for(task, timeout=1)

    compare(response.status_code, expected=500, suffix=response.text)


def test_authenticate() -> None:
    credentials = OAuth2PKCECredentials(client_id="", client_secret="")
    mock = Mock()
    mock._authenticate.return_value = credentials
    mock.asyncio_run.side_effect = lambda x: x
    with Replacer() as replace:
        replace.in_module(_authenticate, mock._authenticate)
        replace.in_module(asyncio.run, mock.asyncio_run, module=asyncio)
        assert authenticate("secret") is credentials
    compare(
        mock.mock_calls,
        expected=[
            call._authenticate("secret", "localhost", 12010),
            call.asyncio_run(credentials),
        ],
    )
