import csv
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Iterator

import click
from xero import Xero

from .authentication import authenticate, credentials_from_file
from .check import check_journals, show_summary
from .export import EXPORTS, FileManager, Split, ALL_JOURNAL_KEYS, flatten
from .transform import TRANSFORMERS, show


@click.group()
@click.option(
    '--auth',
    'auth_path',
    type=click.Path(path_type=Path),
    default=Path('.xerotrust.json'),
    help='Path to the authentication file.',
)
@click.option(
    '-l',
    '--log-level',
    type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
)
@click.pass_context
def cli(ctx: click.Context, auth_path: Path, log_level: str | None) -> None:
    ctx.obj = auth_path
    if log_level:
        logging.basicConfig(level=getattr(logging, log_level))


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
        print(f'- {tenant["tenantId"]}: {tenant["tenantName"]}')

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


@cli.command()
@click.argument(
    'endpoints',
    type=click.Choice(list(EXPORTS.keys()), case_sensitive=False),
    nargs=-1,
)
@click.option(
    '-t',
    '--tenant',
    'tenant_ids',
    type=str,
    help='Tenant ID, otherwise all tenants are exported',
    multiple=True,
)
@click.option(
    '--path',
    type=click.Path(path_type=Path, file_okay=False, writable=True),
    default=Path.cwd(),
    help='The path into which data should be exported',
)
@click.option(
    '--split',
    type=click.Choice(Split, case_sensitive=False),  # type: ignore[arg-type]  # needs Click 8.2
    default=Split.MONTHS,
    help='How to split the exported files',
)
@click.pass_obj
def export(
    auth_path: Path, tenant_ids: tuple[str], endpoints: tuple[str], path: Path, split: Split
) -> None:
    """Export data from Xero API endpoints."""
    credentials = credentials_from_file(auth_path)
    xero = Xero(credentials)

    all_tenant_data = {t["tenantId"]: t for t in credentials.get_tenants()}
    if not tenant_ids:
        tenant_ids = all_tenant_data.keys()

    if not endpoints:
        endpoints = EXPORTS.keys()

    with FileManager(serializer=TRANSFORMERS['json']) as files:
        for tenant_id in tenant_ids:
            tenant_data = all_tenant_data[tenant_id]
            tenant_path = path / tenant_data["tenantName"]
            files.write(tenant_data, tenant_path / "tenant.json")
            credentials.tenant_id = tenant_id

            latest_path = tenant_path / "latest.json"
            latest = {}

            for endpoint in endpoints:
                manager = getattr(xero, endpoint.lower())
                exporter = EXPORTS[endpoint]
                for row in exporter.items(manager, latest=latest.get(endpoint)):
                    files.write(row, tenant_path / exporter.name(row, split))
                latest[endpoint] = exporter.latest

            latest_path.write_text(json.dumps(latest, cls=DateTimeEncoder, indent=2))


@cli.group()
def journals() -> None:
    """Commands for working with journals."""
    pass


def journal_stream(paths_: Iterable[Path]) -> Iterator[dict[str, Any]]:
    for path_ in paths_:
        with path_.open() as source:
            for line in source:
                yield json.loads(line)


@journals.command('check')
@click.argument(
    'paths',
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
    nargs=-1,
    required=True,
)
def check_command(paths: tuple[Path, ...]) -> None:
    """
    Check journals export files for duplicate IDs, duplicate numbers, and number gaps.

    Accepts one or more PATHS. Shell globbing (e.g., *.jsonl) can be used.
    """

    check_journals(
        show_summary(
            journal_stream(paths), fields=['JournalNumber', 'JournalDate', 'CreatedDateUTC']
        )
    )


@journals.command('flatten')
@click.argument(
    'paths',
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
    nargs=-1,
    required=True,
)
@click.option(
    '-o',
    '--output',
    'output_file',
    type=click.File('w'),
    default='-',
    help='Output file path. Defaults to stdout.',
)
def flatten_command(paths: tuple[Path, ...], output_file: click.utils.LazyFile) -> None:
    """
    Flatten journal entries from JSONL files into CSV format.

    Each JournalLine within a Journal becomes a row in the CSV,
    combined with data from its parent Journal.
    """
    # The type hint for output_file from click.File('w') is IO[str],
    # but click.utils.LazyFile is what's actually passed at runtime before it's opened.
    # We'll let the csv.DictWriter handle the file object.
    csv_writer = csv.DictWriter(output_file, fieldnames=ALL_JOURNAL_KEYS)
    csv_writer.writeheader()
    for row in flatten(journal_stream(paths)):
        csv_writer.writerow(row)
