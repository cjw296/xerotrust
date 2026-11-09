from pathlib import Path
import time
from typing import Any, Iterator
from unittest.mock import Mock

import pytest
import requests
from testfixtures import compare, replace_in_module

from xerotrust import read_api
from xerotrust.authentication import credentials_from_file
from xerotrust.read_api import APIError, QuotaExceeded, ReadAPI

from .helpers import SAMPLE_CREDENTIALS


@pytest.fixture()
def client(tmp_path: Path) -> Iterator[ReadAPI]:
    with replace_in_module(
        credentials_from_file, Mock(return_value=SAMPLE_CREDENTIALS), module=read_api
    ):
        yield ReadAPI(tmp_path / 'auth', 'tenant-1', 'assets')


def test_authenticated_json(client: ReadAPI, pook: Any) -> None:
    pook.get(
        client.base + 'Settings',
        headers={'Xero-tenant-id': 'tenant-1', 'Authorization': 'Bearer test_token'},
        reply=200,
        response_json={'assetNumberPrefix': 'FA-'},
        response_headers={'X-DayLimit-Remaining': '900'},
    )
    compare(client.json('Settings'), expected={'assetNumberPrefix': 'FA-'})
    compare(client.remaining, expected=900)


@pytest.mark.parametrize('status', [429, 503])
def test_transient_retry(client: ReadAPI, pook: Any, status: int) -> None:
    pook.get(client.base + 'Assets', reply=status, response_headers={'Retry-After': '2'})
    pook.get(client.base + 'Assets', reply=200, response_json={})
    sleep = Mock()
    with replace_in_module(time.sleep, sleep, module=read_api):
        compare(client.json('Assets'), expected={})
    sleep.assert_called_once_with(2 if status == 429 else 1)


@pytest.mark.parametrize('headers', [{'Retry-After': '3600'}, {'X-DayLimit-Remaining': '0'}])
def test_daily_limit(client: ReadAPI, pook: Any, headers: dict[str, str]) -> None:
    pook.get(client.base + 'Assets', reply=429, response_headers=headers)
    with pytest.raises(QuotaExceeded):
        client.json('Assets')


def test_reserve(client: ReadAPI) -> None:
    client.remaining = client.reserve = 100
    with pytest.raises(QuotaExceeded):
        client.json('Assets')


@pytest.mark.parametrize('status, attempts', [(401, 1), (403, 1), (302, 1), (500, 5)])
def test_errors(client: ReadAPI, pook: Any, status: int, attempts: int) -> None:
    for _ in range(attempts):
        pook.get(client.base + 'Assets', reply=status)
    with (
        replace_in_module(time.sleep, Mock(), module=read_api),
        pytest.raises(APIError, match=f'HTTP {status}'),
    ):
        client.json('Assets')


def test_transport_retry_and_exhaustion(client: ReadAPI) -> None:
    response = Mock(status_code=200, headers={})
    get = Mock(side_effect=[requests.ConnectionError(), response])
    with (
        replace_in_module(requests.get, get, module=requests),
        replace_in_module(time.sleep, Mock(), module=read_api),
    ):
        compare(client.get('Assets', binary=True), expected=response)
    compare(get.call_args.kwargs['headers']['Accept'], expected='*/*')
    get.side_effect = requests.Timeout()
    with (
        replace_in_module(requests.get, get, module=requests),
        replace_in_module(time.sleep, Mock(), module=read_api),
        pytest.raises(APIError, match='five transport attempts'),
    ):
        client.get('Assets')
