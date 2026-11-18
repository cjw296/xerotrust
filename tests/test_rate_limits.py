from pathlib import Path
from time import sleep
from typing import Any
from unittest.mock import Mock, call

import pytest
from testfixtures import compare, replace_in_module

from xerotrust import export
from xerotrust.export import RateLimitPolicy

from .helpers import FileChecker, XERO_API_URL, add_tenants_response, run_cli


pytestmark = pytest.mark.usefixtures('mock_credentials_from_file')


@pytest.mark.parametrize(
    'headers',
    [
        {'Retry-After': '12577'},
        {'Retry-After': '121'},
        {'Retry-After': '60', 'X-DayLimit-Remaining': '0'},
        {'Retry-After': '60', 'X-Rate-Limit-Problem': 'day'},
        {'Retry-After': '60', 'X-Rate-Limit-Problem': ' DAY '},
    ],
)
@pytest.mark.parametrize('update', [False, True])
def test_deferral_does_not_sleep_retry_or_change_destination(
    tmp_path: Path, pook: Any, headers: dict[str, str], update: bool, check_files: FileChecker
) -> None:
    add_tenants_response(pook)
    pook.get(f'{XERO_API_URL}/Accounts', reply=429, response_headers=headers)
    tenant = tmp_path / 'Tenant 1'
    tenant.mkdir()
    original = '{"Accounts": {"UpdatedDateUTC": "2023-01-01T00:00:00"}}'
    arguments = ['--update'] if update else []
    if update:
        (tenant / 'latest.json').write_text(original)
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
    compare(
        actual=result.output,
        expected=(
            'Error: Accounts: Rate limit requires deferral; '
            f'retry in at least {headers["Retry-After"]} seconds. Export incomplete.\n'
        ),
    )
    check_files({'Tenant 1/latest.json': original} if update else {})


@pytest.mark.parametrize(
    'headers,exception,message',
    [
        ({}, KeyError, "'retry-after'"),
        (
            {'Retry-After': 'invalid'},
            ValueError,
            "invalid literal for int() with base 10: 'invalid'",
        ),
    ],
)
def test_invalid_delay_is_an_error_not_deferral(
    tmp_path: Path,
    pook: Any,
    headers: dict[str, str],
    exception: type[Exception],
    message: str,
    check_files: FileChecker,
) -> None:
    add_tenants_response(pook)
    pook.get(f'{XERO_API_URL}/Accounts', reply=429, response_headers=headers)
    with pytest.raises(exception) as error:
        run_cli(tmp_path, 'export', 'accounts', '--path', str(tmp_path))
    compare(actual=str(error.value), expected=message)
    check_files({})


@pytest.mark.parametrize('seconds,max_wait', [(0, 0), (120, 120), (200, 300)])
def test_short_rate_limits_respect_configured_wait(
    tmp_path: Path, pook: Any, seconds: int, max_wait: int
) -> None:
    add_tenants_response(pook)
    pook.get(
        f'{XERO_API_URL}/Accounts',
        reply=429,
        response_headers={'Retry-After': str(seconds), 'X-DayLimit-Remaining': '10'},
    )
    pook.get(f'{XERO_API_URL}/Accounts', reply=200, response_json={'Status': 'OK', 'Accounts': []})
    sleeper = Mock()
    with replace_in_module(sleep, sleeper, module=export):
        result = run_cli(
            tmp_path,
            'export',
            'accounts',
            '--path',
            str(tmp_path),
            '--rate-limit-max-wait',
            str(max_wait),
        )
    sleeper.assert_called_once_with(seconds)
    compare(actual=result.output, expected='')
    compare(actual=(tmp_path / 'Tenant 1/latest.json').read_text(), expected='{}')


@pytest.mark.parametrize('attempts', [1, 2, 5])
def test_repeated_minute_limits_with_daily_capacity_are_bounded(
    tmp_path: Path, pook: Any, attempts: int, check_files: FileChecker
) -> None:
    add_tenants_response(pook)
    pook.get(
        f'{XERO_API_URL}/Accounts',
        reply=429,
        times=attempts,
        response_headers={
            'Retry-After': '60',
            'X-Rate-Limit-Problem': 'minute',
            'X-DayLimit-Remaining': '900',
        },
    )
    sleeper = Mock()
    with replace_in_module(sleep, sleeper, module=export):
        result = run_cli(
            tmp_path,
            'export',
            'accounts',
            '--path',
            str(tmp_path),
            '--rate-limit-max-attempts',
            str(attempts),
            expected_return_code=75,
        )
    compare(actual=sleeper.call_args_list, expected=[call(60)] * (attempts - 1))
    compare(
        actual=result.output,
        expected=(
            f'Error: Accounts: Rate limit persisted after {attempts} attempts; '
            'retry in at least 60 seconds. Export incomplete.\n'
        ),
    )
    check_files({})


def test_cli_policy_does_not_leak_to_subsequent_exports(tmp_path: Path, pook: Any) -> None:
    for _ in range(2):
        add_tenants_response(pook)
        pook.get(f'{XERO_API_URL}/Accounts', reply=429, response_headers={'Retry-After': '2'})
    pook.get(f'{XERO_API_URL}/Accounts', reply=200, response_json={'Status': 'OK', 'Accounts': []})
    sleeper = Mock()
    with replace_in_module(sleep, sleeper, module=export):
        result = run_cli(
            tmp_path,
            'export',
            'accounts',
            '--path',
            str(tmp_path),
            '--rate-limit-max-wait',
            '1',
            expected_return_code=75,
        )
        sleeper.assert_not_called()
        compare(
            actual=result.output,
            expected=(
                'Error: Accounts: Rate limit requires deferral; retry in at least 2 seconds. '
                'Export incomplete.\n'
            ),
        )
        run_cli(tmp_path, 'export', 'accounts', '--path', str(tmp_path))
    sleeper.assert_called_once_with(2)
    compare(actual=export.EXPORTS['Accounts'].rate_limit, expected=RateLimitPolicy())


def test_attempt_budget_is_per_request(tmp_path: Path, pook: Any) -> None:
    add_tenants_response(pook)
    for endpoint in ('Accounts', 'Contacts'):
        pook.get(f'{XERO_API_URL}/{endpoint}', reply=429, response_headers={'Retry-After': '1'})
        pook.get(
            f'{XERO_API_URL}/{endpoint}', reply=200, response_json={'Status': 'OK', endpoint: []}
        )
    sleeper = Mock()
    with replace_in_module(sleep, sleeper, module=export):
        result = run_cli(
            tmp_path,
            'export',
            'accounts',
            'contacts',
            '--path',
            str(tmp_path),
            '--rate-limit-max-attempts',
            '2',
        )
    compare(actual=sleeper.call_args_list, expected=[call(1), call(1)])
    compare(actual=result.output, expected='')
    compare(actual=(tmp_path / 'Tenant 1/latest.json').read_text(), expected='{}')


@pytest.mark.parametrize('max_wait,max_attempts', [(-1, 5), (120, 0)])
def test_invalid_policy(max_wait: int, max_attempts: int) -> None:
    with pytest.raises(ValueError) as error:
        RateLimitPolicy(max_wait, max_attempts)
    compare(
        actual=str(error.value),
        expected='Rate limit max_wait must be nonnegative and max_attempts positive',
    )
