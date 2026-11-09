"""Export the fixed-asset register, types and settings using read-only requests."""

import hashlib
import json
from pathlib import Path
from typing import Any

import click

from .read_api import ReadAPI, tenants, write_json

STATUSES = ('DRAFT', 'REGISTERED', 'DISPOSED')


def export_assets(api: ReadAPI, destination: Path) -> dict[str, Any]:
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'manifest.json').unlink(missing_ok=True)
    assets: list[dict[str, Any]] = []
    seen: set[str] = set()
    counts = {}
    for status in STATUSES:
        page = 1
        expected = None
        count = 0
        while True:
            result = api.json('Assets', {'status': status, 'page': page, 'pageSize': 200})
            pagination = result['pagination']
            total = int(pagination['itemCount'])
            if expected is None:
                expected = total
            rows = result['items']
            if total != expected or int(pagination['page']) != page or not isinstance(rows, list):
                raise ValueError('Asset pagination changed or was malformed; retry a fresh export')
            for row in rows:
                identity = row['assetId']
                if identity in seen:
                    raise ValueError('Duplicate asset ID in paginated results')
                seen.add(identity)
                if str(row['assetStatus']).upper() != status:
                    raise ValueError('Asset status does not match its requested collection')
                assets.append(row)
                count += 1
            if page >= int(pagination['pageCount']):
                break
            if not rows:
                raise ValueError('Asset pagination ended before its advertised last page')
            page += 1
        if count != expected:
            raise ValueError('Asset count does not match the API pagination total')
        counts[status] = count

    # Collection responses omit fields such as description and originalInvoiceId.
    for index, summary in enumerate(assets):
        detail = api.json(f"Assets/{summary['assetId']}")
        if (
            not isinstance(detail, dict)
            or detail.get('assetId') != summary['assetId']
            or str(detail.get('assetStatus', '')).upper() != str(summary['assetStatus']).upper()
        ):
            raise ValueError(
                'Asset detail does not match its collection entry; retry a fresh export'
            )
        assets[index] = detail

    types = api.json('AssetTypes')
    settings = api.json('Settings')
    if (
        not isinstance(types, list)
        or any(not isinstance(row, dict) for row in types)
        or not isinstance(settings, dict)
    ):
        raise ValueError('Malformed asset types or settings response')
    write_json(destination / 'assets.json', assets)
    write_json(destination / 'types.json', types)
    write_json(destination / 'settings.json', settings)
    manifest = {
        'version': 1,
        'complete': True,
        'status_counts': counts,
        'asset_details': len(assets),
        'asset_types': len(types),
        'files': {
            name: hashlib.sha256((destination / name).read_bytes()).hexdigest()
            for name in ('assets.json', 'types.json', 'settings.json')
        },
    }
    write_json(destination / 'manifest.json', manifest)
    return manifest


@click.command('export-assets')
@click.option(
    '--path',
    type=click.Path(path_type=Path, exists=True, file_okay=False),
    required=True,
    help='Accounting export root containing tenant directories; use a fresh staging directory.',
)
@click.pass_obj
def command(auth: Path, path: Path) -> None:
    """Add fixed assets, asset types and settings to an accounting export."""
    for directory, tenant in tenants(path):
        manifest = export_assets(ReadAPI(auth, tenant, 'assets'), directory / 'fixed-assets')
        click.echo(
            f"Fixed assets: {sum(manifest['status_counts'].values())} assets, {manifest['asset_types']} types"
        )
