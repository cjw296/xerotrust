from pathlib import Path
from textwrap import dedent
from typing import Any
from unittest.mock import Mock

import pytest
from testfixtures import compare

from .helpers import (
    XERO_CONNECTIONS_URL,
    XERO_CONTACTS_URL,
    XERO_JOURNALS_URL,
    add_tenants_response,
    run_cli,
)


pytestmark = pytest.mark.usefixtures("mock_credentials_from_file")


class TestExplore:
    def test_explore_simple(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        pook.get(
            XERO_CONNECTIONS_URL,
            reply=200,
            response_json=[
                {"tenantId": "t1", "tenantName": "Tenant 1"},
                {"tenantId": "t2", "tenantName": "Tenant 2"},
            ],
        )
        pook.get(
            XERO_CONTACTS_URL,
            reply=200,
            response_json={
                "Status": "OK",
                "Contacts": [{"ContactID": "c1", "Name": "Contact 1"}],
            },
        )
        result = run_cli(tmp_path, "explore", "contacts")
        mock_credentials_from_file.assert_called_once_with(tmp_path)
        compare(result.output, expected='{"ContactID": "c1", "Name": "Contact 1"}\n')

    def test_explore_explicit_tenant_id(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        pook.get(
            XERO_CONTACTS_URL,
            headers={"Xero-Tenant-Id": "t2"},
            reply=200,
            response_json={
                "Status": "OK",
                "Contacts": [{"ContactID": "c2", "Name": "Contact 2"}],
            },
        )
        result = run_cli(tmp_path, "explore", "Contacts", "--tenant", "t2")
        mock_credentials_from_file.assert_called_once_with(tmp_path)
        compare(result.output, expected='{"ContactID": "c2", "Name": "Contact 2"}\n')

    def test_explore_with_entity_id(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            f"{XERO_CONTACTS_URL}/c3",
            reply=200,
            response_json={
                "Status": "OK",
                "Contacts": [{"ContactID": "c3", "Name": "Contact 3"}],
            },
        )
        result = run_cli(tmp_path, "explore", "Contacts", "--id", "c3")
        compare(result.output, expected='{"ContactID": "c3", "Name": "Contact 3"}\n')

    def test_explore_with_since(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            XERO_JOURNALS_URL,
            headers={"If-Modified-Since": "Sun, 20 Apr 2025 00:00:00 GMT"},
            reply=200,
            response_json={
                "Status": "OK",
                "Journals": [{"JournalID": "j1", "JournalNumber": 1}],
            },
        )
        result = run_cli(tmp_path, "explore", "journals", "--since", "2025-04-20")
        compare(result.output, expected='{"JournalID": "j1", "JournalNumber": 1}\n')

    def test_explore_with_offset(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            XERO_JOURNALS_URL,
            params={"offset": "100"},
            reply=200,
            response_json={
                "Status": "OK",
                "Journals": [{"JournalID": "j101", "JournalNumber": 101}],
            },
        )
        result = run_cli(tmp_path, "explore", "Journals", "--offset", "100")
        compare(result.output, expected='{"JournalID": "j101", "JournalNumber": 101}\n')

    def test_explore_with_page(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            XERO_CONTACTS_URL,
            params={"page": "2"},
            reply=200,
            response_json={
                "Status": "OK",
                "Contacts": [{"ContactID": "c201", "Name": "Contact 201"}],
            },
        )
        result = run_cli(tmp_path, "explore", "contacts", "--page", "2")
        compare(result.output, expected='{"ContactID": "c201", "Name": "Contact 201"}\n')

    def test_explore_with_page_size(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            XERO_CONTACTS_URL,
            params={"pageSize": "5"},
            reply=200,
            response_json={
                "Status": "OK",
                "Contacts": [{"ContactID": "c1", "Name": "Contact 1"}],
            },
        )
        result = run_cli(tmp_path, "explore", "contacts", "--page-size", "5")
        compare(
            result.output,
            expected=dedent(
                """\
                {"ContactID": "c1", "Name": "Contact 1"}
            """
            ),
        )

    def test_explore_with_page_and_page_size(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            XERO_CONTACTS_URL,
            params={"page": "3", "pageSize": "2"},
            reply=200,
            response_json={
                "Status": "OK",
                "Contacts": [
                    {"ContactID": "c5", "Name": "Contact 5"},
                ],
            },
        )
        result = run_cli(tmp_path, "explore", "contacts", "--page", "3", "--page-size", "2")
        compare(
            result.output,
            expected=dedent(
                """\
                {"ContactID": "c5", "Name": "Contact 5"}
            """
            ),
        )

    def test_explore_with_field(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            XERO_CONTACTS_URL,
            reply=200,
            response_json={
                "Status": "OK",
                "Contacts": [
                    {"ContactID": "c1", "Name": "Contact 1"},
                    {"ContactID": "c2", "Name": "Contact 2"},
                ],
            },
        )
        result = run_cli(tmp_path, "explore", "contacts", "-f", "Name", "-n")
        compare(result.output, expected="Contact 1\nContact 2\n")

    def test_explore_with_transform(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            XERO_CONTACTS_URL,
            reply=200,
            response_json={
                "Status": "OK",
                "Contacts": [
                    {"ContactID": "c1", "Name": "Contact 1"},
                    {"ContactID": "c2", "Name": "Contact 2"},
                ],
            },
        )
        result = run_cli(tmp_path, "explore", "contacts", "-t", "pretty")
        compare(
            result.output,
            expected=dedent(
                """\
                {'ContactID': 'c1', 'Name': 'Contact 1'}
                {'ContactID': 'c2', 'Name': 'Contact 2'}
            """
            ),
        )

    def test_explore_pretty_with_newline(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            XERO_CONTACTS_URL,
            reply=200,
            response_json={
                "Status": "OK",
                "Contacts": [
                    {"ContactID": "c1", "Name": "Contact 1"},
                    {"ContactID": "c2", "Name": "Contact 2"},
                ],
            },
        )
        result = run_cli(tmp_path, "explore", "contacts", "-t", "pretty", "-n")
        compare(
            result.output,
            expected=dedent(
                """\
                {'ContactID': 'c1', 'Name': 'Contact 1'}
                {'ContactID': 'c2', 'Name': 'Contact 2'}
                """
            ),
        )

    def test_explore_with_date_and_datetime_in_json(
        self, mock_credentials_from_file: Mock, tmp_path: Path, pook: Any
    ) -> None:
        add_tenants_response(pook)
        pook.get(
            XERO_CONTACTS_URL,
            reply=200,
            response_json={
                "Status": "OK",
                "Contacts": [
                    {
                        "ContactID": "c1",
                        "Name": "Contact 1",
                        # Represents 2023-03-15T13:20:00+00:00, pyxero turns this into a datetime:
                        "CreatedDateUTC": "/Date(1678886400000+0000)/",
                    }
                ],
            },
        )
        result = run_cli(tmp_path, "explore", "contacts", "-t", "json")
        # Our XeroEncoder should serialize date/datetime back to ISO format
        compare(
            result.output,
            expected=(
                '{"ContactID": "c1", "Name": "Contact 1", '
                '"CreatedDateUTC": "2023-03-15T13:20:00+00:00"}\n'
            ),
        )
