import json
import time
from pathlib import Path
from pprint import pprint

import click

from .authentication import authenticate


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
