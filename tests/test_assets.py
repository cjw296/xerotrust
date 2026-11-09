import json
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from testfixtures import ShouldRaise, compare, replace_in_module

from xerotrust import assets, read_api
from xerotrust.assets import export_assets

from .helpers import run_cli


def collection(status: str, page: int = 1, pages: int = 1, total: int = 1) -> dict[str, Any]:
    return {
        'pagination': {'page': page, 'pageCount': pages, 'itemCount': total},
        'items': [
            {
                'assetId': f'{status}-{page}',
                'assetStatus': status.title(),
                'bookDepreciationDetail': {'currentBookValue': 12.34},
            }
        ],
    }


def responses() -> list[Any]:
    return [
        collection('DRAFT', 1, 2, 2),
        collection('DRAFT', 2, 2, 2),
        collection('REGISTERED'),
        collection('DISPOSED'),
        [{'assetTypeId': 'type-1'}],
        {'assetNumberPrefix': 'FA-'},
    ]


def test_assets_all_statuses_and_pages(tmp_path: Path) -> None:
    api = Mock(spec=read_api.ReadAPI)
    api.json.side_effect = responses()
    manifest = export_assets(api, tmp_path)
    compare(manifest['status_counts'], expected={'DRAFT': 2, 'REGISTERED': 1, 'DISPOSED': 1})
    compare(manifest['asset_types'], expected=1)
    compare(
        json.loads((tmp_path / 'assets.json').read_text()),
        expected=[row for response in responses()[:4] for row in response['items']],
    )
    compare(list(manifest['files']), expected=['assets.json', 'types.json', 'settings.json'])
    compare(
        api.json.call_args_list[1].args,
        expected=('Assets', {'status': 'DRAFT', 'page': 2, 'pageSize': 200}),
    )


def test_empty_register_is_explicit(tmp_path: Path) -> None:
    api = Mock(spec=read_api.ReadAPI)
    api.json.side_effect = [
        {'pagination': {'page': 1, 'pageCount': 0, 'itemCount': 0}, 'items': []}
    ] * 3 + [[], {}]
    manifest = export_assets(api, tmp_path)
    compare(manifest['status_counts'], expected=dict.fromkeys(assets.STATUSES, 0))
    compare(json.loads((tmp_path / 'assets.json').read_text()), expected=[])


@pytest.mark.parametrize(
    'failure',
    ['count', 'page', 'changed', 'early', 'duplicate', 'status', 'types', 'settings', 'http'],
)
def test_incomplete_export_has_no_manifest(tmp_path: Path, failure: str) -> None:
    data = responses()
    if failure == 'count':
        data[1]['items'] = []
    elif failure == 'page':
        data[0]['pagination']['page'] = 2
    elif failure == 'changed':
        data[1]['pagination']['itemCount'] = 3
    elif failure == 'early':
        data[0]['items'] = []
    elif failure == 'duplicate':
        data[1]['items'] = data[0]['items']
    elif failure == 'status':
        data[0]['items'][0]['assetStatus'] = 'Disposed'
    elif failure == 'types':
        data[-2] = [None]
    elif failure == 'settings':
        data[-1] = []
    else:
        data[1] = read_api.APIError('synthetic request failure')
    (tmp_path / 'manifest.json').write_text('{"complete":true}')
    api = Mock(spec=read_api.ReadAPI)
    api.json.side_effect = data
    with pytest.raises((ValueError, read_api.APIError)):
        export_assets(api, tmp_path)
    compare((tmp_path / 'manifest.json').exists(), expected=False)


def test_command(tmp_path: Path) -> None:
    tenant = tmp_path / 'Synthetic Tenant'
    tenant.mkdir()
    (tenant / 'tenant.json').write_text('{"tenantId":"tenant-1"}')
    factory = Mock()
    factory.return_value.json.side_effect = responses()
    with replace_in_module(read_api.ReadAPI, factory, module=assets):
        result = run_cli(tmp_path / 'auth', 'export-assets', '--path', str(tmp_path))
    compare(result.output, expected='Fixed assets: 4 assets, 1 types\n')
    factory.assert_called_once_with(tmp_path / 'auth', 'tenant-1', 'assets')


def test_no_tenants(tmp_path: Path) -> None:
    with ShouldRaise(ValueError('No exported tenant.json files found; run export first')):
        list(read_api.tenants(tmp_path))


def test_symlink_tenant(tmp_path: Path) -> None:
    source = tmp_path / 'source'
    source.mkdir()
    (source / 'tenant.json').write_text('{}')
    (tmp_path / 'linked').symlink_to(source, target_is_directory=True)
    with ShouldRaise(ValueError('Tenant directories must not be symlinks')):
        list(read_api.tenants(tmp_path))
