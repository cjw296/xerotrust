import json
import time
from pathlib import Path
from textwrap import dedent
from typing import Any

from unittest.mock import Mock

import pytest
from testfixtures import replace_in_module

from xerotrust import export

from .helpers import (
    FileChecker,
    XERO_API_URL,
    add_tenants_response,
    run_cli,
)


pytestmark = pytest.mark.usefixtures("mock_credentials_from_file")


class TestExport:
    def test_all_endpoints_single_tenant(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Accounts",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Accounts': [
                    {
                        'AccountID': 'a1',
                        'Name': 'Acc 1',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Contacts",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Contacts': [
                    {
                        'ContactID': 'c1',
                        'Name': 'Cont 1',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Journals': [],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path))

        check_files(
            {
                'Tenant 1/accounts.jsonl': '{"AccountID": "a1", "Name": "Acc 1", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/contacts.jsonl': '{"ContactID": "c1", "Name": "Cont 1", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/latest.json': dedent("""\
                    {
                      "Accounts": {
                        "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"
                      },
                      "Contacts": {
                        "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"
                      },
                      "Journals": null
                    }"""),
            }
        )

    def test_specific_endpoint_multiple_tenants(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        add_tenants_response(
            pook,
            [
                {'tenantId': 't1', 'tenantName': 'Tenant 1'},
                {'tenantId': 't2', 'tenantName': 'Tenant 2'},
            ],
        )
        pook.get(
            f"{XERO_API_URL}/Contacts",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Contacts': [
                    {
                        'ContactID': 'c1',
                        'Name': 'Cont 1',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Contacts",
            headers={'Xero-Tenant-Id': 't2'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Contacts': [
                    {
                        'ContactID': 'c2',
                        'Name': 'Cont 2',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), 'contacts')

        check_files(
            {
                'Tenant 1/contacts.jsonl': '{"ContactID": "c1", "Name": "Cont 1", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/latest.json': dedent("""\
                    {
                      "Contacts": {
                        "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"
                      }
                    }"""),
                'Tenant 2/contacts.jsonl': '{"ContactID": "c2", "Name": "Cont 2", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 2/tenant.json': '{"tenantId": "t2", "tenantName": "Tenant 2"}\n',
                'Tenant 2/latest.json': dedent("""\
                    {
                      "Contacts": {
                        "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"
                      }
                    }"""),
            },
        )

    def test_journals_uses_journals_export(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Journals': [
                    {
                        'JournalID': 'j1',
                        'JournalDate': '/Date(1678838400000+0000)/',  # 2023-03-15
                        'JournalNumber': 1,
                    },
                    {
                        'JournalID': 'j2',
                        'JournalDate': '/Date(1678924800000+0000)/',  # 2023-03-16
                        'JournalNumber': 2,
                    },
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': 't1'},
            params={'offset': '2'},
            reply=200,
            response_json={'Status': 'OK', 'Journals': []},
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'journals')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/journals-2023-03.jsonl': (
                    '{"JournalID": "j1", "JournalDate": "2023-03-15T00:00:00+00:00", "JournalNumber": 1}\n'
                    '{"JournalID": "j2", "JournalDate": "2023-03-16T00:00:00+00:00", "JournalNumber": 2}\n'
                ),
                'Tenant 1/latest.json': dedent("""\
                    {
                      "Journals": {
                        "JournalDate": "2023-03-16T00:00:00+00:00",
                        "JournalNumber": 2
                      }
                    }"""),
            }
        )

    def test_journals_with_rate_limit(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        # First request hits rate limit
        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': 't1'},
            reply=429,  # Rate limit exceeded
            response_headers={'retry-after': '1'},  # Server responds with retry-after header
        )

        # Second request (after retry) succeeds
        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': 't1'},
            params={'offset': '0'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Journals': [
                    {
                        'JournalID': 'j1',
                        'JournalDate': '/Date(1681948800000+0000)/',
                        'JournalNumber': 1,
                    },
                ],
            },
        )

        # End of pagination
        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': 't1'},
            params={'offset': '1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Journals': [],
            },
        )

        # Mock the sleep function to avoid actually waiting
        mock_sleep = Mock()

        with replace_in_module(time.sleep, mock_sleep, module=export):
            # Run the export command for journals only
            run_cli(tmp_path, 'export', 'journals', '--path', str(tmp_path))

        # Verify sleep was called with retry-after value
        mock_sleep.assert_called_once_with(1)

        # Verify the journal was exported after retrying
        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/journals-2023-04.jsonl': (
                    '{"JournalID": "j1", "JournalDate": "2023-04-20T00:00:00+00:00", "JournalNumber": 1}\n'
                ),
                'Tenant 1/latest.json': dedent("""\
                    {
                      "Journals": {
                        "JournalDate": "2023-04-20T00:00:00+00:00",
                        "JournalNumber": 1
                      }
                    }"""),
            }
        )

    def setup_journal_mocks(self, pook: Any, tenant_id: str = 't1') -> None:
        """Helper to set up common pook mocks for journal exports."""
        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': tenant_id},
            reply=200,
            response_json={
                'Status': 'OK',
                'Journals': [
                    {
                        'JournalID': 'j1',
                        'JournalDate': '/Date(1678838400000+0000)/',  # 2023-03-15
                        'JournalNumber': 1,
                    },
                    {
                        'JournalID': 'j2',
                        'JournalDate': '/Date(1678924800000+0000)/',  # 2023-03-16
                        'JournalNumber': 2,
                    },
                    {
                        'JournalID': 'j3',
                        'JournalDate': '/Date(1710460800000+0000)/',  # 2024-03-15
                        'JournalNumber': 3,
                    },
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': tenant_id},
            params={'offset': '3'},
            reply=200,
            response_json={'Status': 'OK', 'Journals': []},
        )

    def test_journals_split_days(self, tmp_path: Path, pook: Any, check_files: FileChecker) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])
        self.setup_journal_mocks(pook)

        run_cli(
            tmp_path,
            'export',
            '--path',
            str(tmp_path),
            '--tenant',
            't1',
            'journals',
            '--split',
            'days',
        )

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/journals-2023-03-15.jsonl': (
                    '{"JournalID": "j1", "JournalDate": "2023-03-15T00:00:00+00:00", "JournalNumber": 1}\n'
                ),
                'Tenant 1/journals-2023-03-16.jsonl': (
                    '{"JournalID": "j2", "JournalDate": "2023-03-16T00:00:00+00:00", "JournalNumber": 2}\n'
                ),
                'Tenant 1/journals-2024-03-15.jsonl': (
                    '{"JournalID": "j3", "JournalDate": "2024-03-15T00:00:00+00:00", "JournalNumber": 3}\n'
                ),
                'Tenant 1/latest.json': dedent("""\
                    {
                      "Journals": {
                        "JournalDate": "2024-03-15T00:00:00+00:00",
                        "JournalNumber": 3
                      }
                    }"""),
            }
        )

    def test_journals_split_months(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])
        self.setup_journal_mocks(pook)

        run_cli(
            tmp_path,
            'export',
            '--path',
            str(tmp_path),
            '--tenant',
            't1',
            'journals',
            '--split',
            'months',
        )

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/journals-2023-03.jsonl': (
                    '{"JournalID": "j1", "JournalDate": "2023-03-15T00:00:00+00:00", "JournalNumber": 1}\n'
                    '{"JournalID": "j2", "JournalDate": "2023-03-16T00:00:00+00:00", "JournalNumber": 2}\n'
                ),
                'Tenant 1/journals-2024-03.jsonl': (
                    '{"JournalID": "j3", "JournalDate": "2024-03-15T00:00:00+00:00", "JournalNumber": 3}\n'
                ),
                'Tenant 1/latest.json': dedent("""\
                    {
                      "Journals": {
                        "JournalDate": "2024-03-15T00:00:00+00:00",
                        "JournalNumber": 3
                      }
                    }"""),
            }
        )

    def test_journals_split_years(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])
        self.setup_journal_mocks(pook)

        run_cli(
            tmp_path,
            'export',
            '--path',
            str(tmp_path),
            '--tenant',
            't1',
            'journals',
            '--split',
            'years',
        )

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/journals-2023.jsonl': (
                    '{"JournalID": "j1", "JournalDate": "2023-03-15T00:00:00+00:00", "JournalNumber": 1}\n'
                    '{"JournalID": "j2", "JournalDate": "2023-03-16T00:00:00+00:00", "JournalNumber": 2}\n'
                ),
                'Tenant 1/journals-2024.jsonl': (
                    '{"JournalID": "j3", "JournalDate": "2024-03-15T00:00:00+00:00", "JournalNumber": 3}\n'
                ),
                'Tenant 1/latest.json': dedent("""\
                    {
                      "Journals": {
                        "JournalDate": "2024-03-15T00:00:00+00:00",
                        "JournalNumber": 3
                      }
                    }"""),
            }
        )

    def write_json(self, path: Path, content: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(content) + '\n')

    def test_export_update_journals_new_data(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        tenant_path = tmp_path / "Tenant 1"

        add_tenants_response(pook, [{'tenantId': "t1", 'tenantName': "Tenant 1"}])

        self.write_json(
            tenant_path / 'latest.json',
            {"Journals": {"JournalDate": "2023-03-15T00:00:00+00:00", "JournalNumber": 1}},
        )
        self.write_json(
            tenant_path / "journals-2023-03.jsonl",
            {"JournalID": "j1", "JournalDate": "2023-03-15T00:00:00+00:00", "JournalNumber": 1},
        )

        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': "t1"},
            params={'offset': '1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Journals': [
                    {
                        'JournalID': 'j2',
                        'JournalDate': '/Date(1678924800000+0000)/',
                        'JournalNumber': 2,
                    },  # 2023-03-16
                    {
                        'JournalID': 'j3',
                        'JournalDate': '/Date(1680307200000+0000)/',
                        'JournalNumber': 3,
                    },  # 2023-04-01
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': "t1"},
            params={'offset': '3'},
            reply=200,
            response_json={'Status': 'OK', 'Journals': []},
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'journals')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/journals-2023-03.jsonl': (
                    '{"JournalID": "j1", "JournalDate": "2023-03-15T00:00:00+00:00", "JournalNumber": 1}\n'
                    '{"JournalID": "j2", "JournalDate": "2023-03-16T00:00:00+00:00", "JournalNumber": 2}\n'
                ),
                'Tenant 1/journals-2023-04.jsonl': (
                    '{"JournalID": "j3", "JournalDate": "2023-04-01T00:00:00+00:00", "JournalNumber": 3}\n'
                ),
                'Tenant 1/latest.json': dedent('''\
                    {
                      "Journals": {
                        "JournalDate": "2023-04-01T00:00:00+00:00",
                        "JournalNumber": 3
                      }
                    }'''),
            }
        )

    def test_export_update_journals_no_new_data(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        tenant_path = tmp_path / "Tenant 1"
        add_tenants_response(pook, [{'tenantId': "t1", 'tenantName': "Tenant 1"}])

        self.write_json(
            tenant_path / "latest.json",
            {"Journals": {"JournalDate": "2023-03-15T00:00:00+00:00", "JournalNumber": 1}},
        )
        self.write_json(
            tenant_path / "journals-2023-03.jsonl",
            {"LEAVE": "THIS"},
        )

        pook.get(
            f"{XERO_API_URL}/Journals",
            headers={'Xero-Tenant-Id': "t1"},
            params={'offset': '1'},
            reply=200,
            response_json={'Status': 'OK', 'Journals': []},
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'journals')

        check_files(
            {
                f'Tenant 1/tenant.json': f'{{"tenantId": "t1", "tenantName": "Tenant 1"}}\n',
                # Journal file should be untouched as no new data for its period was fetched:
                f'Tenant 1/journals-2023-03.jsonl': '{"LEAVE": "THIS"}\n',
                # latest.json should be as it was before:
                'Tenant 1/latest.json': dedent('''\
                    {
                      "Journals": {
                        "JournalDate": "2023-03-15T00:00:00+00:00",
                        "JournalNumber": 1
                      }
                    }'''),
            }
        )

    def test_export_update_contacts_new_data(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        tenant_path = tmp_path / "Tenant 1"
        add_tenants_response(pook, [{'tenantId': "t1", 'tenantName': "Tenant 1"}])

        self.write_json(
            tenant_path / "latest.json",
            {"Contacts": {"UpdatedDateUTC": "2023-03-15T00:00:00+00:00"}},
        )
        self.write_json(
            tenant_path / "contacts.jsonl",
            {"ContactID": "c1", "Name": "Cont 1", "UpdatedDateUTC": "2023-03-15T00:00:00+00:00"},
        )

        pook.get(
            f"{XERO_API_URL}/Contacts",
            headers={'Xero-Tenant-Id': "t1"},
            reply=200,
            response_json={
                'Status': 'OK',
                'Contacts': [
                    {
                        'ContactID': 'c1',
                        'Name': 'Cont 1',
                        'UpdatedDateUTC': '/Date(1678838400000+0000)/',
                    },  # 2023-03-15
                    {
                        'ContactID': 'c2',
                        'Name': 'Cont 2',
                        'UpdatedDateUTC': '/Date(1678924800000+0000)/',
                    },  # 2023-03-16
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'contacts')

        # Contacts file is overwritten with all items from API
        check_files(
            {
                f'Tenant 1/tenant.json': f'{{"tenantId": "t1", "tenantName": "Tenant 1"}}\n',
                f'Tenant 1/contacts.jsonl': (
                    '{"ContactID": "c1", "Name": "Cont 1", "UpdatedDateUTC": "2023-03-15T00:00:00+00:00"}\n'
                    '{"ContactID": "c2", "Name": "Cont 2", "UpdatedDateUTC": "2023-03-16T00:00:00+00:00"}\n'
                ),
                f'Tenant 1/latest.json': dedent("""\
                    {
                      "Contacts": {
                        "UpdatedDateUTC": "2023-03-16T00:00:00+00:00"
                      }
                    }"""),
            }
        )

    def test_export_update_contacts_no_new_data(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        tenant_path = tmp_path / "Tenant 1"
        add_tenants_response(pook, [{'tenantId': "t1", 'tenantName': "Tenant 1"}])

        self.write_json(
            tenant_path / "latest.json",
            {"Contacts": {"UpdatedDateUTC": "2023-03-15T00:00:00+00:00"}},
        )
        self.write_json(
            tenant_path / "contacts.jsonl",
            {"ContactID": "c1", "Name": "Cont 1", "UpdatedDateUTC": "2023-03-15T00:00:00+00:00"},
        )

        pook.get(
            f"{XERO_API_URL}/Contacts",
            headers={'Xero-Tenant-Id': "t1"},
            reply=200,
            response_json={
                'Status': 'OK',
                'Contacts': [
                    {
                        'ContactID': 'c1',
                        'Name': 'Cont 1',
                        'UpdatedDateUTC': '/Date(1678838400000+0000)/',
                    },  # 2023-03-15
                ],
            },
        )
        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'contacts')

        check_files(
            {
                f'Tenant 1/tenant.json': f'{{"tenantId": "t1", "tenantName": "Tenant 1"}}\n',
                f'Tenant 1/contacts.jsonl': (
                    '{"ContactID": "c1", "Name": "Cont 1", "UpdatedDateUTC": "2023-03-15T00:00:00+00:00"}\n'
                ),
                f'Tenant 1/latest.json': dedent("""\
                    {
                      "Contacts": {
                        "UpdatedDateUTC": "2023-03-15T00:00:00+00:00"
                      }
                    }"""),
            }
        )

    def test_export_update_multiple_endpoints(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        tenant_path = tmp_path / "Tenant 1"
        add_tenants_response(pook, [{'tenantId': "t1", 'tenantName': "Tenant 1"}])

        self.write_json(
            tenant_path / "latest.json",
            {
                "Accounts": {"UpdatedDateUTC": "2023-03-15T00:00:00+00:00"},
                "Contacts": {"UpdatedDateUTC": "2023-03-15T00:00:00+00:00"},
            },
        )

        self.write_json(  # Pre-existing accounts file
            tenant_path / "accounts.jsonl",
            {"AccountID": "a1", "Name": "Acc 1", "UpdatedDateUTC": "2023-03-15T00:00:00+00:00"},
        )
        self.write_json(  # Pre-existing contacts file
            tenant_path / "contacts.jsonl",
            {"ContactID": "c1", "Name": "Cont 1", "UpdatedDateUTC": "2023-03-15T00:00:00+00:00"},
        )

        # Accounts: new data
        pook.get(
            f"{XERO_API_URL}/Accounts",
            headers={'Xero-Tenant-Id': "t1"},
            reply=200,
            response_json={
                'Status': 'OK',
                'Accounts': [
                    {  # Existing item, potentially updated
                        'AccountID': 'a1',
                        'Name': 'Acc 1 Updated',
                        'UpdatedDateUTC': '/Date(1678924800000+0000)/',  # 2023-03-16
                    },
                    {  # New item
                        'AccountID': 'a2',
                        'Name': 'Acc 2',
                        'UpdatedDateUTC': '/Date(1678924800000+0000)/',  # 2023-03-16
                    },
                ],
            },
        )
        # Contacts: no new data
        pook.get(
            f"{XERO_API_URL}/Contacts",
            headers={'Xero-Tenant-Id': "t1"},
            reply=200,
            response_json={
                'Status': 'OK',
                'Contacts': [
                    {
                        'ContactID': 'c1',
                        'Name': 'Cont 1',
                        'UpdatedDateUTC': '/Date(1678838400000+0000)/',
                    }  # 2023-03-15
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'accounts', 'contacts')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/accounts.jsonl': (  # Overwritten with new a1 (updated) and a2
                    '{"AccountID": "a1", "Name": "Acc 1 Updated", "UpdatedDateUTC": "2023-03-16T00:00:00+00:00"}\n'
                    '{"AccountID": "a2", "Name": "Acc 2", "UpdatedDateUTC": "2023-03-16T00:00:00+00:00"}\n'
                ),
                'Tenant 1/contacts.jsonl': (  # Overwritten with c1 (no change)
                    '{"ContactID": "c1", "Name": "Cont 1", "UpdatedDateUTC": "2023-03-15T00:00:00+00:00"}\n'
                ),
                'Tenant 1/latest.json': dedent("""\
                    {
                      "Accounts": {
                        "UpdatedDateUTC": "2023-03-16T00:00:00+00:00"
                      },
                      "Contacts": {
                        "UpdatedDateUTC": "2023-03-15T00:00:00+00:00"
                      }
                    }"""),
            }
        )
