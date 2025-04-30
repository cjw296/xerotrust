import asyncio
import base64
import hashlib
import importlib.resources
import json
import webbrowser
from contextvars import ContextVar
from pathlib import Path
from typing import Awaitable, Callable
from typing import cast

from fastapi import FastAPI, Request, Response
from fastapi.templating import Jinja2Templates
from hypercorn.asyncio import serve
from hypercorn.config import Config
from xero.auth import OAuth2PKCECredentials
from xero.constants import XeroScopes

from .exceptions import XeroAPIException

SCOPES = [
    XeroScopes.OFFLINE_ACCESS,
    XeroScopes.ACCOUNTING_TRANSACTIONS_READ,
    XeroScopes.ACCOUNTING_CONTACTS_READ,
    XeroScopes.ACCOUNTING_JOURNALS_READ,
    XeroScopes.ACCOUNTING_SETTINGS_READ,
    XeroScopes.FILES_READ,
    XeroScopes.ACCOUNTING_REPORTS_READ,
    XeroScopes.ACCOUNTING_ATTACHMENTS_READ,
]
app = FastAPI()

# Set up templates and static:
pkg_resources = importlib.resources.files("xerotrust")
templates_dir = cast(Path, pkg_resources / "templates")
templates = Jinja2Templates(directory=templates_dir)

# A global event to signal when to shut down
shutdown_event = asyncio.Event()

# A context var for the current credentials
credentials_context = ContextVar[OAuth2PKCECredentials]("credentials")


@app.middleware("http")
async def shutdown_after_response(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware to shut down after serving one response"""
    response = await call_next(request)
    shutdown_event.set()
    return response


@app.exception_handler(XeroAPIException)
async def value_errors(request: Request, exception: XeroAPIException) -> Response:
    return templates.TemplateResponse(
        request=request,
        name="error.html",
        context={"error": str(exception)},
        status_code=500,
    )


@app.get("/")
async def callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
) -> Response:
    if error:
        raise XeroAPIException(error)

    credentials = credentials_context.get()

    expected_state = credentials.state["auth_state"]
    if state != expected_state:
        raise XeroAPIException(f"Unexpected state: expected={expected_state!r}, actual={state!r}")
    credentials.get_token(code)

    return templates.TemplateResponse(request=request, name="success.html")


async def _authenticate(client_id: str, host: str, port: int) -> OAuth2PKCECredentials:
    credentials = OAuth2PKCECredentials(
        client_id,
        client_secret="PLACEHOLDER",
        port=port,
        callback_uri=f"http://{host}:{port}/",
        scope=SCOPES,
    )
    credentials_context.set(credentials)
    challenge = str(
        base64.urlsafe_b64encode(hashlib.sha256(credentials.verifier).digest())[:-1],
        "ascii",
    )
    url = f"{credentials.generate_url()}&code_challenge={challenge}&code_challenge_method=S256"
    print("If your web browser doesn't open, please visit: \n", url)
    webbrowser.open(url)

    config = Config()
    config.bind = [f"{host}:{port}"]
    # The type hint for serve's first argument expects a lower-level ASGI callable,
    # but FastAPI instances are valid ASGI applications.
    await serve(app, config, shutdown_trigger=shutdown_event.wait)  # type: ignore[arg-type]

    if not credentials.token:
        raise XeroAPIException("Authentication failed, see browser window")
    return credentials


def authenticate(
    client_id: str, host: str = "localhost", port: int = 12010
) -> OAuth2PKCECredentials:
    return asyncio.run(_authenticate(client_id, host, port))


def credentials_from_file(path: Path) -> OAuth2PKCECredentials:
    data = json.loads(path.read_text())
    credentials = OAuth2PKCECredentials(**data, scope=SCOPES)
    credentials._init_oauth(data['token'])
    if credentials.expired():
        try:
            credentials.refresh()
        except Exception as e:
            e.add_note("You will need to run `xerotrust login` now!")
            raise
        data['token'] = credentials.token
        path.write_text(json.dumps(data))
    return credentials
