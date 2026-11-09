import json
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, Mock

import pytest
from testfixtures import compare, replace_in_module

from xerotrust import files
from xerotrust.read_api import ReadAPI, QuotaExceeded

from .helpers import run_cli

ONE = '00000000-0000-0000-0000-000000000001'
TWO = '00000000-0000-0000-0000-000000000002'
OBJECT = '00000000-0000-0000-0000-000000000003'


def metadata(identity: str = ONE) -> dict[str, Any]:
    return {
        'Id': identity,
        'Name': '../../untrusted.pdf',
        'Size': 4,
        'UpdatedDateUtc': '2026-01-01',
    }


def page(items: list[dict[str, Any]], number: int = 1, total: int | None = None) -> dict[str, Any]:
    return {'Page': number, 'TotalCount': len(items) if total is None else total, 'Items': items}


def binary(data: bytes = b'file') -> MagicMock:
    response = MagicMock()
    response.__enter__.return_value = response
    response.iter_content.return_value = [data]
    return response


def api_for(rows: list[dict[str, Any]]) -> Mock:
    api = Mock(spec=ReadAPI)

    def get_json(resource: str, params: Any = None) -> Any:
        if resource == 'Files':
            return page(rows)
        if resource == 'Folders':
            return []
        return [{'FileId': resource.split('/')[1], 'ObjectId': OBJECT, 'ObjectGroup': 'Invoice'}]

    api.json.side_effect = get_json
    api.get.side_effect = lambda *a, **kw: binary()
    return api


def test_complete_files_and_cache(tmp_path: Path) -> None:
    api = api_for([metadata()])
    destination, cache = tmp_path / 'export', tmp_path / 'cache'
    first = files.export_files(api, destination, cache)
    compare(first['file_count'], expected=1)
    compare(first['total_bytes'], expected=4)
    compare((destination / f'blobs/{ONE}.bin').read_bytes(), expected=b'file')
    compare((tmp_path / 'untrusted.pdf').exists(), expected=False)
    index = json.loads((destination / 'index.json').read_text())
    compare(index[0]['metadata'], expected=metadata())
    compare(index[0]['associations'][0]['ObjectId'], expected=OBJECT)
    second = files.export_files(api, tmp_path / 'second', cache)
    compare(second['file_count'], expected=1)
    compare(api.get.call_count, expected=1)  # Binary reuse is checksum-verified.
    compare(sum(c.args[0].endswith('/Associations') for c in api.json.call_args_list), expected=2)


def test_resume_after_quota(tmp_path: Path) -> None:
    api = api_for([metadata(), metadata(TWO)])
    api.get.side_effect = [binary(), QuotaExceeded('daily quota'), binary()]
    destination, cache = tmp_path / 'export', tmp_path / 'cache'
    with pytest.raises(QuotaExceeded):
        files.export_files(api, destination, cache)
    compare((destination / 'manifest.json').exists(), expected=False)
    compare(json.loads((cache / 'cycle.json').read_text())['complete'], expected=False)
    files.export_files(api, destination, cache)
    compare(api.get.call_count, expected=3)
    compare(
        sum(c.args[0] == f'Files/{ONE}/Associations' for c in api.json.call_args_list), expected=1
    )
    compare(json.loads((destination / 'manifest.json').read_text())['file_count'], expected=2)


@pytest.mark.parametrize('change', ['corruption', 'metadata'])
def test_cache_revalidation(tmp_path: Path, change: str) -> None:
    row = metadata()
    api = api_for([row])
    cache = tmp_path / 'cache'
    files.export_files(api, tmp_path / 'first', cache)
    if change == 'corruption':
        (cache / ONE / 'content.bin').write_bytes(b'bad!')
    else:
        row['UpdatedDateUtc'] = '2026-01-02'
    files.export_files(api, tmp_path / 'second', cache)
    compare(api.get.call_count, expected=2)


@pytest.mark.parametrize('data', [b'cut', b'longer'])
def test_truncated_or_oversized_download(tmp_path: Path, data: bytes) -> None:
    api = api_for([metadata()])
    api.get.side_effect = lambda *a, **kw: binary(data)
    with pytest.raises(ValueError):
        files.export_files(api, tmp_path / 'export', tmp_path / 'cache')
    compare((tmp_path / 'cache' / ONE / 'content.part').exists(), expected=False)
    compare((tmp_path / 'export/manifest.json').exists(), expected=False)


@pytest.mark.parametrize(
    'associations',
    [{}, [{'FileId': TWO, 'ObjectId': OBJECT}], [{'FileId': ONE, 'ObjectId': 'invalid'}]],
)
def test_invalid_associations(tmp_path: Path, associations: Any) -> None:
    api = api_for([metadata()])
    api.json.side_effect = [page([metadata()]), associations]
    with pytest.raises(ValueError):
        files.export_files(api, tmp_path / 'export', tmp_path / 'cache')
    compare((tmp_path / 'export/manifest.json').exists(), expected=False)


def test_binary_survives_association_failure(tmp_path: Path) -> None:
    api = api_for([metadata()])
    api.json.side_effect = [page([metadata()]), QuotaExceeded('quota')]
    cache = tmp_path / 'cache'
    with pytest.raises(QuotaExceeded):
        files.export_files(api, tmp_path / 'export', cache)
    api.json.side_effect = api_for([metadata()]).json.side_effect
    files.export_files(api, tmp_path / 'export', cache)
    compare(api.get.call_count, expected=1)


def test_empty_library(tmp_path: Path) -> None:
    manifest = files.export_files(api_for([]), tmp_path / 'export', tmp_path / 'cache')
    compare(manifest['file_count'], expected=0)
    compare(json.loads((tmp_path / 'export/index.json').read_text()), expected=[])


def test_catalog_multiple_pages() -> None:
    api = Mock(spec=ReadAPI)
    api.json.side_effect = [page([metadata()], 1, 2), page([metadata(TWO)], 2, 2)]
    compare(files.catalog(api), expected=[metadata(), metadata(TWO)])
    compare(api.json.call_args.args[1]['page'], expected=2)


@pytest.mark.parametrize(
    'kind', ['total', 'page', 'rows', 'duplicate', 'negative', 'early', 'extra', 'id']
)
def test_invalid_catalog(kind: str) -> None:
    data = [page([metadata()], 1, 2), page([metadata(TWO)], 2, 2)]
    if kind == 'total':
        data[1]['TotalCount'] = 3
    elif kind == 'page':
        data[1]['Page'] = 1
    elif kind == 'rows':
        data[0]['Items'] = {}
    elif kind == 'duplicate':
        data[1]['Items'] = [metadata()]
    elif kind == 'negative':
        data[0]['Items'][0]['Size'] = -1
    elif kind == 'early':
        data[0]['Items'] = []
    elif kind == 'extra':
        data[0]['TotalCount'] = 0
    else:
        data[0]['Items'][0]['Id'] = '../../outside'
    api = Mock(spec=ReadAPI)
    api.json.side_effect = data
    with pytest.raises(ValueError):
        files.catalog(api)


def test_invalid_folders(tmp_path: Path) -> None:
    api = api_for([])
    api.json.side_effect = [page([]), {}]
    with pytest.raises(ValueError):
        files.export_files(api, tmp_path / 'export', tmp_path / 'cache')
    compare((tmp_path / 'export/manifest.json').exists(), expected=False)


def test_command(tmp_path: Path) -> None:
    source = tmp_path / 'export/Tenant'
    source.mkdir(parents=True)
    (source / 'tenant.json').write_text(json.dumps({'tenantId': OBJECT}))
    factory = Mock(return_value=api_for([metadata()]))
    with replace_in_module(ReadAPI, factory, module=files):
        result = run_cli(
            tmp_path / 'auth',
            'export-files',
            '--path',
            str(source.parent),
            '--cache',
            str(tmp_path / 'cache'),
            '--reserve-requests',
            '200',
        )
    compare(result.output, expected='Files: 1 binaries, 4 bytes; complete\n')
    factory.assert_called_once_with(tmp_path / 'auth', OBJECT, 'files', 200)


def test_cache_must_be_external(tmp_path: Path) -> None:
    result = run_cli(
        tmp_path / 'auth',
        'export-files',
        '--path',
        str(tmp_path),
        '--cache',
        str(tmp_path / 'cache'),
        expected_return_code=2,
    )
    compare('Cache must be outside' in result.output, expected=True)
