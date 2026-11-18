import json
from pathlib import Path
from typing import Any

import pytest
from testfixtures import compare

from .helpers import XERO_API_URL, add_tenants_response, run_cli


pytestmark = pytest.mark.usefixtures('mock_credentials_from_file')


def contents(directory: Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(directory)): path.read_bytes()
        for path in directory.rglob('*')
        if path.is_file()
    }


@pytest.mark.parametrize('endpoint', ['Journals', 'BankTransactions'])
@pytest.mark.parametrize('update', [False, True])
@pytest.mark.parametrize('failure', ['later_page', 'later_endpoint'])
def test_quota_then_rerun_is_idempotent(
    tmp_path: Path, pook: Any, endpoint: str, update: bool, failure: str
) -> None:
    tenant = tmp_path / 'Tenant 1'
    tenant.mkdir()
    (tenant / 'tenant.json').write_text('{"previous": true}\n')
    (tenant / 'accounts.jsonl').write_text('{"AccountID": "original"}\n')
    (tenant / 'unrelated.txt').write_text('preserved')
    old_date = '2022-12-31T00:00:00+00:00'
    new_date = '2023-01-01T00:00:00+00:00'
    if endpoint == 'Journals':
        filename = 'journals.jsonl'
        original_row = {'JournalID': 'j1', 'JournalNumber': 1, 'JournalDate': old_date}
        api_row = {
            'JournalID': 'j2',
            'JournalNumber': 2,
            'JournalDate': '/Date(1672531200000+0000)/',
        }
        expected_row = dict(api_row, JournalDate=new_date)
        previous_latest = {'JournalNumber': 1, 'JournalDate': old_date}
        expected_latest = {'JournalNumber': 2, 'JournalDate': new_date}
    else:
        filename = 'transactions.jsonl'
        original_row = {'BankTransactionID': 'b1', 'Date': old_date, 'UpdatedDateUTC': old_date}
        api_row = {
            'BankTransactionID': 'b2',
            'Date': '/Date(1672531200000+0000)/',
            'UpdatedDateUTC': '/Date(1672531200000+0000)/',
        }
        expected_row = dict(api_row, Date=new_date, UpdatedDateUTC=new_date)
        previous_latest = {'UpdatedDateUTC': old_date}
        expected_latest = {'UpdatedDateUTC': new_date}
    (tenant / filename).write_text(json.dumps(original_row) + '\n')
    (tenant / 'latest.json').write_text(json.dumps({endpoint: previous_latest}))
    before = contents(tmp_path)

    def responses(fail: bool) -> None:
        add_tenants_response(pook)
        pook.get(
            f'{XERO_API_URL}/Accounts',
            reply=200,
            response_json={'Status': 'OK', 'Accounts': [{'AccountID': 'replacement'}]},
        )
        pook.get(
            f'{XERO_API_URL}/{endpoint}',
            reply=200,
            response_json={'Status': 'OK', endpoint: [api_row]},
        )
        if fail and failure == 'later_page':
            pook.get(
                f'{XERO_API_URL}/{endpoint}', reply=429, response_headers={'Retry-After': '12577'}
            )
        else:
            pook.get(
                f'{XERO_API_URL}/{endpoint}',
                reply=200,
                response_json={'Status': 'OK', endpoint: []},
            )
            if fail:
                pook.get(
                    f'{XERO_API_URL}/Contacts', reply=429, response_headers={'Retry-After': '12577'}
                )
            else:
                pook.get(
                    f'{XERO_API_URL}/Contacts',
                    reply=200,
                    response_json={'Status': 'OK', 'Contacts': []},
                )

    arguments = ['--update'] if update else []
    responses(fail=True)
    run_cli(
        tmp_path,
        'export',
        'accounts',
        endpoint,
        'contacts',
        '--split',
        'none',
        '--path',
        str(tmp_path),
        *arguments,
        expected_return_code=75,
    )
    compare(actual=contents(tmp_path), expected=before)
    responses(fail=False)
    run_cli(
        tmp_path,
        'export',
        'accounts',
        endpoint,
        'contacts',
        '--split',
        'none',
        '--path',
        str(tmp_path),
        *arguments,
    )
    expected_rows = [original_row, expected_row] if update else [expected_row]
    compare(
        actual=[json.loads(line) for line in (tenant / filename).read_text().splitlines()],
        expected=expected_rows,
    )
    compare(
        actual=json.loads((tenant / 'latest.json').read_text()),
        expected={endpoint: expected_latest},
    )
    compare(
        actual=(tenant / 'accounts.jsonl').read_text(), expected='{"AccountID": "replacement"}\n'
    )
    compare(actual=(tenant / 'unrelated.txt').read_text(), expected='preserved')
    compare(actual=sorted(path.name for path in tmp_path.iterdir()), expected=['Tenant 1'])


def test_later_tenant_quota_discards_earlier_tenant_changes(tmp_path: Path, pook: Any) -> None:
    tenant = tmp_path / 'Tenant 1'
    tenant.mkdir()
    (tenant / 'accounts.jsonl').write_text('{"AccountID": "previous"}\n')
    (tenant / 'latest.json').write_text('{}')
    before = contents(tmp_path)
    add_tenants_response(
        pook,
        [
            {'tenantId': 't1', 'tenantName': 'Tenant 1'},
            {'tenantId': 't2', 'tenantName': 'Tenant 2'},
        ],
    )
    pook.get(
        f'{XERO_API_URL}/Accounts',
        headers={'Xero-Tenant-Id': 't1'},
        reply=200,
        response_json={'Status': 'OK', 'Accounts': [{'AccountID': 'replacement'}]},
    )
    pook.get(
        f'{XERO_API_URL}/Accounts',
        headers={'Xero-Tenant-Id': 't2'},
        reply=429,
        response_headers={'Retry-After': '12577'},
    )
    run_cli(tmp_path, 'export', 'accounts', '--path', str(tmp_path), expected_return_code=75)
    compare(actual=contents(tmp_path), expected=before)
    compare(actual=sorted(path.name for path in tmp_path.iterdir()), expected=['Tenant 1'])
