import asyncio
import importlib.resources
from contextvars import ContextVar
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from xero.auth import OAuth2PKCECredentials

from .exceptions import XeroAPIException

app = FastAPI()

# Set up templates and static:
pkg_resources = importlib.resources.files("xerotrust")
templates_dir: Path = pkg_resources / "templates"
templates = Jinja2Templates(directory=templates_dir)

# A global event to signal when to shut down
shutdown_event = asyncio.Event()

# A context var for the current credentials
credentials_context = ContextVar[OAuth2PKCECredentials]("credentials")


@app.middleware("http")
async def shutdown_after_response(request: Request, call_next):
    """Middleware to shut down after serving one response"""
    response = await call_next(request)
    shutdown_event.set()
    return response


@app.exception_handler(XeroAPIException)
async def value_errors(request: Request, exception: XeroAPIException):
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
):
    if error:
        raise XeroAPIException(error)

    credentials = credentials_context.get()

    expected_state = credentials.state["auth_state"]
    if state != expected_state:
        raise XeroAPIException(f"Unexpected state: expected={expected_state!r}, actual={state!r}")
    credentials.get_token(code)

    return templates.TemplateResponse(request=request, name="success.html")
