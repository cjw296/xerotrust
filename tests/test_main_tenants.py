from pathlib import Path
from textwrap import dedent
from typing import Any
from unittest.mock import Mock

import pytest
from testfixtures import compare

from .helpers import XERO_CONNECTIONS_URL, run_cli


pytestmark = pytest.mark.usefixtures("mock_credentials_from_file")


class TestTenants:
    def test_tenants_default(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        pook.get(
            XERO_CONNECTIONS_URL,
            reply=200,
            # connections endpoint doesn't return the weird Date() format found elsewhere:
            response_json=[{"id": "xx", "createDateUtc": "2025-04-10T14:09:00.9954070"}],
        )
        result = run_cli(tmp_path, "tenants")
        mock_credentials_from_file.assert_called_once_with(tmp_path)
        compare(
            result.output, expected='{"id": "xx", "createDateUtc": "2025-04-10T14:09:00.9954070"}\n'
        )

    def test_tenants_transform_tenant_name(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        pook.get(
            XERO_CONNECTIONS_URL,
            reply=200,
            response_json=[
                {"id": "t1", "tenantName": "Tenant 1"},
                {"id": "t2", "tenantName": "Tenant 2"},
            ],
        )

        result = run_cli(tmp_path, "tenants", "-f", "tenantName")

        mock_credentials_from_file.assert_called_once_with(tmp_path)
        compare(result.output, expected="Tenant 1\nTenant 2\n")

    def test_tenants_transform_pretty(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        pook.get(
            XERO_CONNECTIONS_URL,
            reply=200,
            response_json=[
                {
                    "id": "t1",
                    "tenantName": "Tenant 1",
                    "createDateUtc": "2025-04-10T14:09:00.9954070",
                },
                {
                    "id": "t2",
                    "tenantName": "Tenant 2",
                    "createDateUtc": "2025-04-11T14:09:00.9954070",
                },
            ],
        )

        result = run_cli(tmp_path, "tenants", "-t", "pretty")

        mock_credentials_from_file.assert_called_once_with(tmp_path)
        compare(
            result.output,
            expected=dedent(
                """\
                {'createDateUtc': '2025-04-10T14:09:00.9954070',
                 'id': 't1',
                 'tenantName': 'Tenant 1'}
                {'createDateUtc': '2025-04-11T14:09:00.9954070',
                 'id': 't2',
                 'tenantName': 'Tenant 2'}
        """
            ),
        )
