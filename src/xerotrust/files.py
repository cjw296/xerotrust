"""Resumable Files API backup, including binaries and document associations."""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
from typing import Any
from uuid import UUID, uuid4

import click

from .read_api import ReadAPI, tenants, write_json


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def identifier(value: Any) -> str:
    return str(UUID(value))


def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            sha.update(block)
    return sha.hexdigest()


def catalog(api: ReadAPI) -> list[dict[str, Any]]:
    items = []
    seen = set()
    page = 1
    expected = None
    while True:
        result = api.json(
            'Files', {'page': page, 'pagesize': 100, 'sort': 'CreatedDateUTC', 'direction': 'ASC'}
        )
        total = int(result['TotalCount'])
        if expected is None:
            expected = total
        if total != expected or int(result['Page']) != page:
            raise ValueError('Files pagination changed during export; retry')
        rows = result['Items']
        if not isinstance(rows, list):
            raise ValueError('Malformed Files collection')
        for row in rows:
            identity = identifier(row['Id'])
            if identity in seen:
                raise ValueError('Duplicate file ID in catalog')
            seen.add(identity)
            if int(row['Size']) < 0:
                raise ValueError('Invalid file size')
            items.append(row)
        if len(items) >= total:
            break
        if not rows:
            raise ValueError('Files pagination ended before the advertised count')
        page += 1
    if len(items) != expected:
        raise ValueError('File count differs from the API total')
    return items


def cached_file(api: ReadAPI, cache: Path, metadata: dict[str, Any], cycle: str) -> dict[str, Any]:
    identity = identifier(metadata['Id'])
    directory = cache / identity
    directory.mkdir(parents=True, exist_ok=True)
    state_path = directory / 'state.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {}
    signature = hashlib.sha256(json.dumps(metadata, sort_keys=True).encode()).hexdigest()
    content = directory / 'content.bin'
    expected = int(metadata['Size'])
    valid = (
        state.get('signature') == signature
        and content.is_file()
        and content.stat().st_size == expected
        and digest(content) == state.get('sha256')
    )
    if not valid:
        partial = directory / 'content.part'
        try:
            with (
                api.get(f'Files/{identity}/Content', binary=True) as response,
                partial.open('wb') as target,
            ):
                length = 0
                for block in response.iter_content(chunk_size=1024 * 1024):
                    length += len(block)
                    if length > expected:
                        raise ValueError('Downloaded file exceeds its advertised size')
                    target.write(block)
            if length != expected:
                raise ValueError('Downloaded file is shorter than its advertised size')
            partial.replace(content)
        finally:
            partial.unlink(missing_ok=True)
        state = {'signature': signature, 'sha256': digest(content), 'downloaded_at': now()}
        write_json(state_path, state)
    if state.get('association_cycle') != cycle:
        associations = api.json(f'Files/{identity}/Associations')
        if not isinstance(associations, list):
            raise ValueError('Malformed file associations')
        for association in associations:
            if identifier(association['FileId']) != identity:
                raise ValueError('Association refers to a different file')
            identifier(association['ObjectId'])
        state.update(
            associations=associations, association_cycle=cycle, associations_checked_at=now()
        )
        write_json(state_path, state)
    return state


def export_files(api: ReadAPI, destination: Path, cache: Path) -> dict[str, Any]:
    destination.mkdir(parents=True, exist_ok=True)
    (destination / 'manifest.json').unlink(missing_ok=True)
    cycle_path = cache / 'cycle.json'
    cycle = json.loads(cycle_path.read_text()) if cycle_path.exists() else {}
    if not cycle or cycle.get('complete'):
        cycle = {'id': str(uuid4()), 'started_at': now(), 'complete': False}
        write_json(cycle_path, cycle)
    rows = catalog(api)
    write_json(cache / 'catalog.json', {'checked_at': now(), 'items': rows})
    records = []
    blobs = destination / 'blobs'
    blobs.mkdir(exist_ok=True)
    for metadata in rows:
        identity = identifier(metadata['Id'])
        state = cached_file(api, cache, metadata, cycle['id'])
        relative = f'blobs/{identity}.bin'
        shutil.copyfile(cache / identity / 'content.bin', destination / relative)
        records.append(
            {
                'metadata': metadata,
                'path': relative,
                'sha256': state['sha256'],
                'downloaded_at': state['downloaded_at'],
                'associations': state['associations'],
                'associations_checked_at': state['associations_checked_at'],
            }
        )
    folders = api.json('Folders')
    if not isinstance(folders, list):
        raise ValueError('Malformed Files folders response')
    write_json(destination / 'folders.json', folders)
    write_json(destination / 'index.json', records)
    manifest = {
        'version': 1,
        'complete': True,
        'file_count': len(records),
        'total_bytes': sum(int(row['metadata']['Size']) for row in records),
        'started_at': cycle['started_at'],
        'completed_at': now(),
        'files': {name: digest(destination / name) for name in ('folders.json', 'index.json')},
    }
    write_json(destination / 'manifest.json', manifest)
    cycle['complete'] = True
    write_json(cycle_path, cycle)
    return manifest


@click.command('export-files')
@click.option(
    '--path',
    type=click.Path(path_type=Path, exists=True, file_okay=False),
    required=True,
    help='Fresh accounting export root containing tenant directories.',
)
@click.option(
    '--cache',
    type=click.Path(path_type=Path, file_okay=False),
    required=True,
    help='Persistent private cache outside retained snapshots; keep it for resumption.',
)
@click.option(
    '--reserve-requests',
    type=click.IntRange(min=0),
    default=0,
    help='Stop before consuming this many remaining daily API calls.',
)
@click.pass_obj
def command(auth: Path, path: Path, cache: Path, reserve_requests: int) -> None:
    """Add uploaded files, inbox files, and their document associations to an export."""
    if cache.resolve().is_relative_to(path.resolve()):
        raise click.UsageError('Cache must be outside the export directory')
    for directory, tenant in tenants(path):
        manifest = export_files(
            ReadAPI(auth, tenant, 'files', reserve_requests),
            directory / 'files',
            cache / identifier(tenant),
        )
        click.echo(
            f"Files: {manifest['file_count']} binaries, {manifest['total_bytes']} bytes; complete"
        )
