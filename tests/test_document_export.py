import json
import time
from pathlib import Path
from typing import Any
from unittest.mock import Mock

import pytest
from testfixtures import ShouldRaise, compare, replace_in_module
from xero.exceptions import XeroInternalError

from xerotrust import export

from .helpers import XERO_API_URL, add_tenants_response, run_cli


pytestmark = pytest.mark.usefixtures("mock_credentials_from_file")


@pytest.fixture(
    params=[
        ('Invoices', 'InvoiceID', 'LineItems'),
        ('CreditNotes', 'CreditNoteID', 'LineItems'),
        ('ManualJournals', 'ManualJournalID', 'JournalLines'),
    ]
)
def document(request: pytest.FixtureRequest) -> tuple[str, str, str]:
    endpoint, identity, lines = request.param
    return endpoint, identity, lines


def page_response(pook: Any, endpoint: str, page: int, rows: list[dict[str, Any]]) -> None:
    pook.get(
        f'{XERO_API_URL}/{endpoint}',
        headers={'Xero-Tenant-Id': 't1'},
        params={'page': str(page), 'pageSize': '1000'},
        reply=200,
        response_json={'Status': 'OK', endpoint: rows},
    )


@pytest.mark.parametrize('update', [False, True])
def test_document_lines_across_pages(
    tmp_path: Path, pook: Any, document: tuple[str, str, str], update: bool
) -> None:
    endpoint, identity, lines = document
    add_tenants_response(pook)
    tenant = tmp_path / 'Tenant 1'
    tenant.mkdir()
    output = tenant / f'{endpoint.lower()}.jsonl'
    checkpoint = tenant / 'latest.json'
    if update:
        output.write_text(json.dumps({identity: 'old-summary', lines: []}) + '\n')
        checkpoint.write_text(
            json.dumps({endpoint: {'UpdatedDateUTC': '2023-01-01T00:00:00+00:00'}})
        )
    rows = [
        {
            identity: f'doc-{n}',
            lines: [{'Description': f'Line {n}', 'LineAmount': n}],
            'UpdatedDateUTC': '/Date(1672531200000+0000)/',
        }
        for n in (1, 2)
    ]
    # A short non-empty page is not used as a reason to omit the next request.
    page_response(pook, endpoint, 1, rows[:1])
    page_response(pook, endpoint, 2, rows[1:])
    page_response(pook, endpoint, 3, [])

    args = ['export', endpoint, '--path', str(tmp_path)]
    if update:
        args.append('--update')
    run_cli(tmp_path, *args)

    expected = [dict(row, UpdatedDateUTC='2023-01-01T00:00:00+00:00') for row in rows]
    compare([json.loads(line) for line in output.read_text().splitlines()], expected=expected)
    compare(
        json.loads(checkpoint.read_text()),
        expected={endpoint: {'UpdatedDateUTC': '2023-01-01T00:00:00+00:00'}},
    )


def test_empty_document_collection(
    tmp_path: Path, pook: Any, document: tuple[str, str, str]
) -> None:
    endpoint, _, _ = document
    add_tenants_response(pook)
    page_response(pook, endpoint, 1, [])
    run_cli(tmp_path, 'export', endpoint, '--path', str(tmp_path))
    compare((tmp_path / 'Tenant 1' / f'{endpoint.lower()}.jsonl').exists(), expected=False)
    compare(json.loads((tmp_path / 'Tenant 1/latest.json').read_text()), expected={})


def test_document_page_rate_limit(
    tmp_path: Path, pook: Any, document: tuple[str, str, str]
) -> None:
    endpoint, identity, lines = document
    add_tenants_response(pook)
    first = {identity: 'doc-1', lines: [{'LineAmount': 1}]}
    second = {identity: 'doc-2', lines: [{'LineAmount': 2}]}
    page_response(pook, endpoint, 1, [first])
    pook.get(
        f'{XERO_API_URL}/{endpoint}',
        params={'page': '2', 'pageSize': '1000'},
        reply=429,
        response_headers={'retry-after': '2'},
    )
    page_response(pook, endpoint, 2, [second])
    page_response(pook, endpoint, 3, [])
    sleep = Mock()
    with replace_in_module(time.sleep, sleep, module=export):
        run_cli(tmp_path, 'export', endpoint, '--path', str(tmp_path))
    sleep.assert_called_once_with(2)
    output = tmp_path / 'Tenant 1' / f'{endpoint.lower()}.jsonl'
    compare(
        [json.loads(line) for line in output.read_text().splitlines()], expected=[first, second]
    )


def test_document_page_failure_preserves_checkpoint(
    tmp_path: Path, pook: Any, document: tuple[str, str, str]
) -> None:
    endpoint, identity, lines = document
    add_tenants_response(pook)
    tenant = tmp_path / 'Tenant 1'
    tenant.mkdir()
    checkpoint = tenant / 'latest.json'
    previous = json.dumps({endpoint: {'UpdatedDateUTC': '2022-01-01T00:00:00+00:00'}})
    checkpoint.write_text(previous)
    page_response(
        pook,
        endpoint,
        1,
        [
            {
                identity: 'doc-1',
                lines: [{'LineAmount': 1}],
                'UpdatedDateUTC': '/Date(1672531200000+0000)/',
            }
        ],
    )
    pook.get(
        f'{XERO_API_URL}/{endpoint}',
        params={'page': '2', 'pageSize': '1000'},
        reply=500,
        response_json={'Status': 'ERROR'},
    )
    with ShouldRaise(XeroInternalError) as raised:
        run_cli(tmp_path, 'export', endpoint, '--path', str(tmp_path), '--update')
    compare(checkpoint.read_text(), expected=previous)
    compare(raised.raised.__notes__, expected=[f'while exporting {endpoint!r}'])
