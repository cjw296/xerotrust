import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from click.testing import CliRunner, Result
from pytest_insta import SnapshotFixture
from testfixtures import compare
from xero.auth import OAuth2PKCECredentials

from xerotrust.authentication import SCOPES
from xerotrust.main import cli


@dataclass
class FileChecker:
    tmp_path: Path

    def __call__(self, expected: dict[str, str | SnapshotFixture]) -> None:
        expected_files = {}
        for relative_path, expected_value in expected.items():
            if isinstance(expected_value, SnapshotFixture):
                expected_content = expected_value(Path(relative_path).with_suffix('.txt').name)
            else:
                expected_content = expected_value
            if isinstance(expected_content, str):
                expected_content = expected_content.rstrip('\n')
            expected_files[relative_path] = expected_content
        actual_files = {}
        for path in self.tmp_path.rglob('*'):
            if path.is_file():
                relative_path = str(path.relative_to(self.tmp_path))
                actual_files[relative_path] = path.read_text().rstrip('\n')
        compare(expected=expected_files, actual=actual_files)


XERO_API_URL = "https://api.xero.com/api.xro/2.0"
XERO_CONNECTIONS_URL = "https://api.xero.com/connections"
XERO_CONTACTS_URL = f"{XERO_API_URL}/Contacts"
XERO_JOURNALS_URL = f"{XERO_API_URL}/Journals"


SAMPLE_CREDENTIALS = OAuth2PKCECredentials(
    client_id="CLIENT_ID",
    client_secret="FOO",
    scope=SCOPES,
    token={"access_token": "test_token"},
)


def run_cli(
    auth_path: Path, *args: str, input: str | None = None, expected_return_code: int = 0
) -> Result:
    args_ = ["--auth", str(auth_path)]
    args_.extend(args)
    result = CliRunner().invoke(cli, args_, catch_exceptions=False, input=input)
    compare(result.exit_code, expected=expected_return_code, suffix=result.output)
    return result


def add_tenants_response(pook: Any, tenants: list[dict[str, str]] | None = None) -> None:
    pook.get(
        XERO_CONNECTIONS_URL,
        reply=200,
        # id and tenantID are not the same here, we need to use tenantId
        response_json=tenants or [{"id": "bad", "tenantId": "t1", "tenantName": "Tenant 1"}],
    )


def write_jsonl_file(path: Path, lines: list[dict[str, Any]]) -> None:
    path.write_text('\n'.join(json.dumps(j) for j in lines) + '\n')
