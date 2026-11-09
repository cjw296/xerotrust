"""Bounded, authenticated GET requests for optional Xero backup APIs."""

import json
from pathlib import Path
from time import sleep
from typing import Any, Iterator

import requests

from .authentication import credentials_from_file

BASES = {
    'assets': 'https://api.xero.com/assets.xro/1.0/',
    'files': 'https://api.xero.com/files.xro/1.0/',
}


class APIError(RuntimeError):
    pass


class QuotaExceeded(APIError):
    """The caller must preserve partial work and resume after the quota resets."""


class ReadAPI:
    def __init__(self, auth: Path, tenant: str, api: str, reserve: int = 0) -> None:
        self.auth = auth
        self.tenant = tenant
        self.base = BASES[api]
        self.reserve = reserve
        self.remaining: int | None = None

    def get(
        self, resource: str, params: dict[str, str | int] | None = None, binary: bool = False
    ) -> Any:
        for attempt in range(5):
            if self.remaining is not None and self.remaining <= self.reserve:
                raise QuotaExceeded('Daily API quota reserved; resume after the daily limit resets')
            credentials = credentials_from_file(self.auth)
            try:
                response = requests.get(
                    self.base + resource,
                    params=params,
                    auth=credentials.oauth,
                    headers={
                        'Xero-tenant-id': self.tenant,
                        'Accept': '*/*' if binary else 'application/json',
                    },
                    timeout=(10, 60),
                    stream=binary,
                    allow_redirects=False,
                )
            except requests.RequestException:
                if attempt == 4:
                    raise APIError('Xero request failed after five transport attempts') from None
                sleep(2**attempt)
                continue
            remaining = response.headers.get('X-DayLimit-Remaining')
            if remaining is not None:
                self.remaining = int(remaining)
            if response.status_code == 200:
                return response
            status = response.status_code
            retry_after = int(response.headers.get('Retry-After', '1'))
            response.close()
            if status == 429 and (self.remaining == 0 or retry_after > 120):
                raise QuotaExceeded(
                    'Xero daily quota exhausted; partial work retained for resumption'
                )
            if attempt == 4 or (status != 429 and status < 500):
                raise APIError(f'Xero API returned HTTP {status}; export is incomplete')
            sleep(retry_after if status == 429 else 2**attempt)
        raise AssertionError('unreachable')  # pragma: no cover

    def json(self, resource: str, params: dict[str, str | int] | None = None) -> Any:
        with self.get(resource, params) as response:
            return response.json()


def tenants(path: Path) -> Iterator[tuple[Path, str]]:
    """Use the tenant metadata from a preceding accounting export."""
    found = sorted(path.glob('*/tenant.json'))
    if not found:
        raise ValueError('No exported tenant.json files found; run export first')
    for metadata in found:
        if metadata.parent.is_symlink():
            raise ValueError('Tenant directories must not be symlinks')
        yield metadata.parent, str(json.loads(metadata.read_text())['tenantId'])


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)
