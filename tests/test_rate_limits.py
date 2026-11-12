import json
from pathlib import Path
from time import sleep
from typing import Any
from unittest.mock import Mock, call

import pytest
from testfixtures import compare, replace_in_module

from xerotrust import export

from .helpers import XERO_API_URL, add_tenants_response, run_cli


pytestmark = pytest.mark.usefixtures('mock_credentials_from_file')


@pytest.mark.parametrize(
    'headers',
    [
        {'Retry-After': '12577'},
        {'Retry-After': '121'},
        {'Retry-After': '60', 'X-DayLimit-Remaining': '0'},
        {'Retry-After': '60', 'X-Rate-Limit-Problem': 'day'},
        {'Retry-After': '60', 'X-Rate-Limit-Problem': ' DAY '},
        {},
        {'Retry-After': 'invalid'},
        {'Retry-After': '-1'},
    ],
)
@pytest.mark.parametrize('update', [False, True])
def test_deferral_does_not_sleep_retry_or_save_checkpoint(
    tmp_path: Path, pook: Any, headers: dict[str, str], update: bool
) -> None:
    add_tenants_response(pook)
    pook.get(f'{XERO_API_URL}/Accounts', reply=429, response_headers=headers)
    tenant = tmp_path / 'Tenant 1'
    tenant.mkdir()
    checkpoint = tenant / 'latest.json'
    original = '{"Accounts": {"UpdatedDateUTC": "2023-01-01T00:00:00"}}'
    arguments = ['--update'] if update else []
    if update:
        checkpoint.write_text(original)
    sleeper = Mock(side_effect=AssertionError('Deferred requests must not sleep'))
    with replace_in_module(sleep, sleeper, module=export):
        result = run_cli(
            tmp_path,
            'export',
            'accounts',
            '--path',
            str(tmp_path),
            *arguments,
            expected_return_code=75,
        )
    sleeper.assert_not_called()
    compare('Accounts' in result.output, True)
    compare('incomplete' in result.output, True)
    compare(checkpoint.read_text() if checkpoint.exists() else None, original if update else None)


@pytest.mark.parametrize('seconds', [0, 120])
def test_short_rate_limits_still_retry(tmp_path: Path, pook: Any, seconds: int) -> None:
    add_tenants_response(pook)
    pook.get(
        f'{XERO_API_URL}/Accounts',
        reply=429,
        response_headers={'Retry-After': str(seconds), 'X-DayLimit-Remaining': '10'},
    )
    pook.get(f'{XERO_API_URL}/Accounts', reply=200, response_json={'Status': 'OK', 'Accounts': []})
    sleeper = Mock()
    with replace_in_module(sleep, sleeper, module=export):
        run_cli(tmp_path, 'export', 'accounts', '--path', str(tmp_path))
    sleeper.assert_called_once_with(seconds)
    compare((tmp_path / 'Tenant 1/latest.json').exists(), True)


def test_repeated_short_limits_are_bounded(tmp_path: Path, pook: Any) -> None:
    add_tenants_response(pook)
    pook.get(
        f'{XERO_API_URL}/Accounts',
        reply=429,
        times=5,
        response_headers={'Retry-After': '60'},
    )
    sleeper = Mock()
    with replace_in_module(sleep, sleeper, module=export):
        result = run_cli(
            tmp_path, 'export', 'accounts', '--path', str(tmp_path), expected_return_code=75
        )
    compare(sleeper.call_args_list, [call(60)] * 4)
    compare('5 attempts' in result.output, True)
    compare((tmp_path / 'Tenant 1/latest.json').exists(), False)


def test_deferral_after_a_page_leaves_checkpoint_unchanged(tmp_path: Path, pook: Any) -> None:
    add_tenants_response(pook)
    tenant = tmp_path / 'Tenant 1'
    tenant.mkdir()
    checkpoint = tenant / 'latest.json'
    original = '{"Journals": {"JournalNumber": 1, "JournalDate": "2022-12-31T00:00:00+00:00"}}'
    checkpoint.write_text(original)
    pook.get(
        f'{XERO_API_URL}/Journals',
        params={'offset': '1'},
        reply=200,
        response_json={
            'Status': 'OK',
            'Journals': [
                {'JournalID': 'j2', 'JournalNumber': 2, 'JournalDate': '/Date(1672531200000+0000)/'}
            ],
        },
    )
    pook.get(
        f'{XERO_API_URL}/Journals',
        params={'offset': '2'},
        reply=429,
        response_headers={'Retry-After': '12577'},
    )
    sleeper = Mock(side_effect=AssertionError('Deferred requests must not sleep'))
    with replace_in_module(sleep, sleeper, module=export):
        run_cli(
            tmp_path,
            'export',
            'journals',
            '--update',
            '--path',
            str(tmp_path),
            expected_return_code=75,
        )
    sleeper.assert_not_called()
    compare(checkpoint.read_text(), original)
    # Partial output remains readable, but is not a completed export or a safe update checkpoint.
    rows = [json.loads(row) for row in (tenant / 'journals-2023-01.jsonl').read_text().splitlines()]
    compare([row['JournalID'] for row in rows], ['j2'])
