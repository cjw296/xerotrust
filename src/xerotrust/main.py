import csv
import json
import logging
import time
from collections import deque, defaultdict
from datetime import date
from pathlib import Path
from typing import Any, Iterable

import click
import enlighten
from rich import box
from rich.console import Console
from rich.table import Table
from xero import Xero

from xerotrust.jsonl import jsonl_stream
from .authentication import authenticate, credentials_from_file
from .check import CHECKERS
from .csv_export import TransactionCSVWriter
from .export import EXPORTS, FileManager, Split, LatestData, download_attachment
from .reconcile import RECONCILERS, AccountTotals
from .transform import TRANSFORMERS, show

# transaction endpoints that should be exported to CSV
TRANSACTION_ENDPOINTS = {'Invoices', 'Bills', 'BankTransactions', 'CreditNotes', 'Payments'}


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
    if 'expires_in' in credentials.token and 'expires_at' not in credentials.token:
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


OPTION_TRANSFORMS = {'page_size': 'pageSize'}


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
@click.option('--page', type=int)
@click.option('--page-size', type=int)
@click.pass_obj
def explore(
    auth_path: Path,
    /,
    endpoint: str,
    tenant: str | None,
    transform: tuple[str],
    field: tuple[str],
    newline: bool,
    id_: str | None,
    **filters: int | None,
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
    else:
        filter_options = {
            OPTION_TRANSFORMS.get(name, name): value
            for (name, value) in filters.items()
            if value is not None
        }
        if filter_options:
            items = manager.filter(**filter_options)
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
    type=click.Choice(Split, case_sensitive=False),
    default=Split.MONTHS,
    help='How to split the exported files',
)
@click.option(
    '--update',
    is_flag=True,
    default=False,
    help='Update the existing export where possible, rather than re-exporting and overwriting',
)
@click.option(
    '--download-attachments',
    is_flag=True,
    default=False,
    help='Download actual attachment files (not just metadata). This can use significant bandwidth and storage.',
)
@click.pass_obj
def export(
    auth_path: Path,
    tenant_ids: tuple[str],
    endpoints: tuple[str],
    path: Path,
    split: Split,
    update: bool,
    download_attachments: bool,
) -> None:
    """Export data from Xero API endpoints."""
    credentials = credentials_from_file(auth_path)
    xero = Xero(credentials)

    all_tenant_data = {t["tenantId"]: t for t in credentials.get_tenants()}
    if not tenant_ids:
        tenant_ids = all_tenant_data.keys()

    if not endpoints:
        # when no specific endpoints requested, exclude Attachments unless flag is set
        if download_attachments:
            endpoints = EXPORTS.keys()
        else:
            endpoints = [e for e in EXPORTS.keys() if e != 'Attachments']

    endpoints_list = list(endpoints)

    with FileManager(serializer=TRANSFORMERS['json']) as files:
        for tenant_id in tenant_ids:
            tenant_data = all_tenant_data[tenant_id]
            tenant_name = tenant_data["tenantName"]
            tenant_path = path / tenant_name
            files.write(tenant_data, tenant_path / "tenant.json")
            credentials.tenant_id = tenant_id

            latest_path = tenant_path / "latest.json"
            latest = LatestData.load(latest_path) if update else LatestData()

            # create CSV writer for combined transaction data (user-friendly location)
            csv_path = tenant_path / f"{tenant_name}_data.csv"
            csv_writer = TransactionCSVWriter(csv_path)

            counter_manager = enlighten.get_manager()
            # map export names to xero manager names
            endpoint_manager_map = {
                'Bills': 'invoices',  # bills use the invoices endpoint with Type=ACCPAY filter
                'Attachments': xero,  # attachments need the full xero instance
            }
            try:
                for endpoint in endpoints_list:
                    try:
                        exporter = EXPORTS[endpoint]
                        counter = counter_manager.counter(
                            desc=f'{tenant_name}: {endpoint}',
                            unit='items exported',
                        )

                        # get the manager, defaulting to lowercase endpoint name
                        # for Attachments, we pass the full xero instance
                        manager_name = endpoint_manager_map.get(endpoint, endpoint.lower())
                        if isinstance(manager_name, str):
                            manager = getattr(xero, manager_name)
                        else:
                            manager = manager_name  # already resolved (e.g., xero instance for Attachments)
                        items = exporter.items(manager, latest=latest.pop(endpoint, None))

                        for row in counter(items):
                            file_path = tenant_path / exporter.name(row, split)
                            files.write(
                                row,
                                file_path,
                                append=update and exporter.supports_update,
                            )

                            # write transaction data to CSV
                            if endpoint in TRANSACTION_ENDPOINTS:
                                csv_writer.write_item(row)

                            # download actual attachment file (always when attachments are exported)
                            if endpoint == 'Attachments':
                                entity_endpoint = row.get('Endpoint')
                                entity_id = row.get('EntityID')
                                filename = row.get('FileName')
                                if entity_endpoint and entity_id and filename:
                                    # remove .meta.json suffix to get actual file path
                                    actual_file_path = Path(
                                        str(file_path).replace('.meta.json', '')
                                    )
                                    # get the manager for the entity's endpoint
                                    entity_manager = getattr(xero, entity_endpoint.lower())
                                    try:
                                        download_attachment(
                                            entity_manager, entity_id, filename, actual_file_path
                                        )
                                    except Exception as download_error:
                                        logging.warning(
                                            f'Failed to download attachment {filename} for '
                                            f'{entity_endpoint} {entity_id}: {download_error}'
                                        )

                        if exporter.latest:
                            latest[endpoint] = exporter.latest
                        counter.refresh()
                    except Exception as e:
                        e.add_note(f'while exporting {endpoint!r}')
                        raise
            finally:
                # ensure CSV is closed even if export fails
                csv_writer.close()
            latest.save(latest_path)


@cli.command()
@click.argument('endpoint')
@click.argument(
    'paths',
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=Path),
    nargs=-1,
    required=True,
)
def check(endpoint: str, paths: tuple[Path, ...]) -> None:
    """Check exported data for issues."""

    endpoint_lower = endpoint.lower()
    if endpoint_lower not in CHECKERS:
        raise click.ClickException(f'Unsupported endpoint: {endpoint}')

    stream = jsonl_stream(paths)
    steps = CHECKERS[endpoint_lower]
    for step in steps:
        stream = step(stream)

    # Consume the final stream to run the checks:
    deque(stream, maxlen=0)


class KeyValueType(click.ParamType):
    name = 'key=value'

    def convert(
        self, value: str, param: click.Parameter | None, ctx: click.Context | None
    ) -> list[str]:
        if '=' not in value:
            self.fail(f"Expected key=value format, got: {value}", param, ctx)
        return value.split('=', 1)


@cli.command()
@click.argument('sources', nargs=-1, type=KeyValueType())
@click.option(
    '-s', '--stop-on-diff', is_flag=True, help='Stop on the first date a difference is found'
)
def reconcile(
    sources: tuple[tuple[str, str], ...],
    stop_on_diff: bool,
) -> None:
    """
    Run reconciliation on exported data.

    Sources are specified as {endpoint}={path glob}, eg: journals=journal*.jsonl
    Exactly two sources must be specified.
    """
    if len(sources) != 2:
        raise click.ClickException(f'Exactly two sources must be specified, got: {sources}')

    # First validate all endpoints
    for endpoint, _ in sources:
        if endpoint.lower() not in RECONCILERS:
            raise click.ClickException(
                f'Unsupported endpoint: {endpoint}. '
                f'Supported endpoints: {", ".join(RECONCILERS.keys())}'
            )

    source_date_totals: list[defaultdict[date, AccountTotals]] = []
    source_account_totals: list[AccountTotals] = []
    endpoints = []
    for endpoint, glob in sources:
        reconciler = RECONCILERS[endpoint.lower()]
        date_totals = defaultdict[date, AccountTotals](AccountTotals)
        account_totals = AccountTotals()
        for item in jsonl_stream([glob]):
            for change in reconciler.parse(item):
                date_totals[reconciler.date(item)].add(change)
                account_totals.add(change)
        source_date_totals.append(date_totals)
        source_account_totals.append(account_totals)
        endpoints.append(endpoint)

    a_data, b_data = source_date_totals

    # compare and stop on the first date where a difference is found:
    diff_dates = set()
    for date_key in sorted(set(a_data) | set(b_data)):
        a_totals = a_data[date_key]
        b_totals = b_data[date_key]
        all_keys = set(a_totals.keys()) | set(b_totals.keys())
        for key in all_keys:
            a_total = a_totals.get(key)
            b_total = b_totals.get(key)
            if a_total.total != b_total.total:
                diff_dates.add(date_key)
                if stop_on_diff:
                    break
        if stop_on_diff and diff_dates:
            break
    else:
        a_totals, b_totals = source_account_totals

    console = Console()
    differences = []
    all_keys = set(a_totals) | set(b_totals)
    for key in all_keys:
        a_total = a_totals.get(key)
        b_total = b_totals.get(key)
        if a_total.total != b_total.total or not stop_on_diff:
            differences.append(
                (
                    a_total.code or b_total.code or '',
                    a_total.name or b_total.name,
                    a_total.type or b_total.type,
                    f"{a_total.total:,}",
                    f"{b_total.total:,}",
                    f"{a_total.total - b_total.total:,}",
                )
            )

    table = Table(box=box.ROUNDED)
    table.add_column("code")
    table.add_column("name")
    table.add_column("type")
    table.add_column(endpoints[0], justify="right")
    table.add_column(endpoints[1], justify="right")
    table.add_column("Difference", justify="right")

    for row in sorted(differences, key=lambda x: x[:2]):
        table.add_row(*row)
    console.print(table)

    if diff_dates:
        dates_text = ', '.join(str(d) for d in sorted(diff_dates))
        message = f"[red]✗ Differences found on date(s): {dates_text}[/red]"
    else:
        message = "[green]✓ All dates reconcile successfully[/green]"
    console.print(message)
