import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Iterable

import click
from xero import Xero

from .authentication import authenticate, credentials_from_file
from .transform import TRANSFORMERS, show


@click.group()
@click.option(
    '--auth',
    'auth_path',
    type=click.Path(path_type=Path),
    default=Path('.xerotrust.json'),
    help='Path to the authentication file.',
)
@click.pass_context
def cli(ctx: click.Context, auth_path: Path) -> None:
    ctx.obj = auth_path


@cli.command()
@click.pass_obj
@click.option('--client-id', default="")
def login(auth_path: Path, client_id: str) -> None:
    """Authenticate with Xero and store credentials."""
    if not client_id:
        client_id = click.prompt(
            'Client ID', hide_input=True, prompt_suffix=': ', default='', show_default=False
        )
    if not client_id and auth_path.exists():
        auth_data = json.loads(auth_path.read_text())
        client_id = auth_data.get('client_id', '')

    if not client_id:
        raise click.ClickException(f'No Client ID provided or found in {auth_path}.')

    now = time.time()
    credentials = authenticate(client_id)
    if 'expires_in' in credentials.token and 'expired_at' not in credentials.token:
        credentials.token['expires_at'] = now + credentials.token['expires_in']

    # Display tenants
    print('\nAvailable tenants:')
    for tenant in credentials.get_tenants():
        print(f'- {tenant["id"]}: {tenant["tenantName"]}')

    # Save authentication data
    auth_path.write_text(
        json.dumps(
            {
                'client_id': credentials.client_id,
                'client_secret': credentials.client_secret,
                'token': credentials.token,
            }
        )
    )


def transform_options(func: Any) -> Any:
    for option in (
        click.option(
            '-t',
            '--transform',
            type=click.Choice(list(TRANSFORMERS.keys())),
            multiple=True,
        ),
        click.option(
            '-f',
            '--field',
            multiple=True,
        ),
        click.option(
            '-n',
            '--newline',
            is_flag=True,
            default=False,
            help='Add a newline between row transforms instead of a space',
        ),
    ):
        func = option(func)
    return func


@cli.command()
@click.pass_obj
@transform_options
def tenants(auth_path: Path, transform: tuple[str], field: tuple[str], newline: bool) -> None:
    """Show the accessible tenants."""
    credentials = credentials_from_file(auth_path)
    show(credentials.get_tenants(), transform, field, newline)


@cli.command()
@click.argument(
    'endpoint',
    type=click.Choice(Xero.OBJECT_LIST, case_sensitive=False),
)
@click.option(
    '--tenant',
    type=str,
    help='Tenant ID, otherwise first tenant is used',
)
@click.option(
    '-i',
    '--id',
    'id_',
    help='Only return this entity',
)
@transform_options
@click.option('--since', type=click.DateTime())
@click.option('--offset', type=int)
@click.pass_obj
def explore(
    auth_path: Path,
    endpoint: str,
    tenant: str | None,
    transform: tuple[str],
    field: tuple[str],
    newline: bool,
    id_: str | None,
    since: datetime | None,
    offset: int | None,
) -> None:
    """Explore a specific Xero API endpoint."""
    credentials = credentials_from_file(auth_path)
    if tenant is None:
        credentials.set_default_tenant()
    else:
        credentials.tenant_id = tenant
    xero = Xero(credentials)

    manager = getattr(xero, endpoint.lower())
    items: Iterable[dict[str, Any]]

    if id_:
        items = manager.get(id_)
    elif since:
        items = manager.filter(since=since)
    elif offset:
        items = manager.filter(offset=offset)
    else:
        items = manager.all()

    show(items, transform, field, newline)
