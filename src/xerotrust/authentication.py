# Setup the server
import base64
import hashlib
import webbrowser
from contextvars import ContextVar

from hypercorn.asyncio import serve
from hypercorn.config import Config

import importlib.resources
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import asyncio

from xero.auth import OAuth2PKCECredentials

app = FastAPI()

# Determine package resource paths
pkg_resources = importlib.resources.files("xerotrust")
templates_dir: Path = pkg_resources / "templates"
static_dir: Path = pkg_resources / "static"

# Set up templates directory
templates = Jinja2Templates(directory=templates_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

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


@app.get("/")
async def callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
):
    if error:
        raise Exception(error)

    credentials = credentials_context.get()

    expected_state = credentials.state["auth_state"]
    if state != expected_state:
        raise RuntimeError(f"Unexpected state {state=} != {expected_state=}")
    credentials.get_token(code)

    return templates.TemplateResponse(
        "success.html", {"request": request, "message": "LOGIN SUCCESS"}
    )


def authenticate(
    client_secret: str, host="localhost", port=12010
) -> OAuth2PKCECredentials:
    credentials = OAuth2PKCECredentials(
        client_secret,
        client_secret="",
        port=port,
        callback_uri=f"http://{host}:{port}/",
    )
    credentials_context.set(credentials)
    challenge = str(
        base64.urlsafe_b64encode(hashlib.sha256(credentials.verifier).digest())[:-1],
        "ascii",
    )
    url = f"{credentials.generate_url()}&code_challenge={challenge}&code_challenge_method=S256"
    print(url)
    webbrowser.open(url)

    config = Config()
    config.bind = [f"{host}:{port}"]
    loop = asyncio.get_event_loop()
    loop.run_until_complete(serve(app, config, shutdown_trigger=shutdown_event.wait))

    return credentials
