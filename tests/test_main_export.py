import json
import time
from pathlib import Path
from textwrap import dedent
from typing import Any

from unittest.mock import Mock

import pytest
from pytest_insta import SnapshotFixture
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
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
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
        pook.get(
            f"{XERO_API_URL}/BankTransactions",
            headers={'Xero-Tenant-Id': 't1'},
            params={'page': '1', 'pageSize': '1000'},
            reply=200,
            response_json={
                'Status': 'OK',
                'BankTransactions': [
                    {
                        'BankTransactionID': 'bt1',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'Total': 100.0,
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/BankTransactions",
            headers={'Xero-Tenant-Id': 't1'},
            params={'page': '2', 'pageSize': '1000'},
            reply=200,
            response_json={'Status': 'OK', 'BankTransactions': []},
        )
        pook.get(
            f"{XERO_API_URL}/BankTransfers",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'BankTransfers': [
                    {
                        'BankTransferID': 'bt1',
                        'Amount': 100.0,
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Invoices",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Invoices': [
                    {
                        'InvoiceID': 'inv1',
                        'Type': 'ACCREC',
                        'InvoiceNumber': '12345',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'Total': 100.0,
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/CreditNotes",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'CreditNotes': [
                    {
                        'CreditNoteID': 'cn1',
                        'Type': 'ACCRECCREDIT',
                        'CreditNoteNumber': 'CN-12345',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'Total': 50.0,
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Currencies",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Currencies': [
                    {
                        'Code': 'USD',
                        'Description': 'United States Dollar',
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Employees",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Employees': [
                    {
                        'EmployeeID': 'emp1',
                        'FirstName': 'John',
                        'LastName': 'Doe',
                        'Status': 'ACTIVE',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Items",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Items': [
                    {
                        'ItemID': 'item1',
                        'Code': 'WIDGET',
                        'Name': 'Blue Widget',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/ManualJournals",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'ManualJournals': [
                    {
                        'ManualJournalID': 'mj1',
                        'Narration': 'Test manual journal',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'Status': 'POSTED',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Organisations",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Organisations': [
                    {
                        'OrganisationID': 'org1',
                        'Name': 'Test Organisation',
                        'LegalName': 'Test Organisation Ltd',
                        'BaseCurrency': 'USD',
                        'CountryCode': 'US',
                        'CreatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Overpayments",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Overpayments': [
                    {
                        'OverpaymentID': 'op1',
                        'Type': 'RECEIVE-OVERPAYMENT',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'Total': 150.0,
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Payments",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Payments': [
                    {
                        'PaymentID': 'pay1',
                        'Amount': 100.0,
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'PaymentType': 'ACCRECPAYMENT',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Prepayments",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Prepayments': [
                    {
                        'PrepaymentID': 'pp1',
                        'Type': 'RECEIVE-PREPAYMENT',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'Total': 200.0,
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/PurchaseOrders",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'PurchaseOrders': [
                    {
                        'PurchaseOrderID': 'po1',
                        'PurchaseOrderNumber': 'PO-001',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'Status': 'DRAFT',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path))

        check_files(
            {
                'Tenant 1/accounts.jsonl': '{"AccountID": "a1", "Name": "Acc 1", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/contacts.jsonl': '{"ContactID": "c1", "Name": "Cont 1", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/transactions-2023-01.jsonl': '{"BankTransactionID": "bt1", "Date": "2023-01-01T00:00:00+00:00", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00", "Total": 100.0}\n',
                'Tenant 1/banktransfers.jsonl': '{"BankTransferID": "bt1", "Amount": 100.0, "Date": "2023-01-01T00:00:00+00:00", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/invoices.jsonl': '{"InvoiceID": "inv1", "Type": "ACCREC", "InvoiceNumber": "12345", "Date": "2023-01-01T00:00:00+00:00", "Total": 100.0, "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/creditnotes.jsonl': '{"CreditNoteID": "cn1", "Type": "ACCRECCREDIT", "CreditNoteNumber": "CN-12345", "Date": "2023-01-01T00:00:00+00:00", "Total": 50.0, "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/currencies.jsonl': '{"Code": "USD", "Description": "United States Dollar"}\n',
                'Tenant 1/employees.jsonl': '{"EmployeeID": "emp1", "FirstName": "John", "LastName": "Doe", "Status": "ACTIVE", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/items.jsonl': '{"ItemID": "item1", "Code": "WIDGET", "Name": "Blue Widget", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/manualjournals.jsonl': '{"ManualJournalID": "mj1", "Narration": "Test manual journal", "Date": "2023-01-01T00:00:00+00:00", "Status": "POSTED", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/organisations.jsonl': '{"OrganisationID": "org1", "Name": "Test Organisation", "LegalName": "Test Organisation Ltd", "BaseCurrency": "USD", "CountryCode": "US", "CreatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/overpayments.jsonl': '{"OverpaymentID": "op1", "Type": "RECEIVE-OVERPAYMENT", "Date": "2023-01-01T00:00:00+00:00", "Total": 150.0, "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/payments.jsonl': '{"PaymentID": "pay1", "Amount": 100.0, "Date": "2023-01-01T00:00:00+00:00", "PaymentType": "ACCRECPAYMENT", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/prepayments.jsonl': '{"PrepaymentID": "pp1", "Type": "RECEIVE-PREPAYMENT", "Date": "2023-01-01T00:00:00+00:00", "Total": 200.0, "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/purchaseorders.jsonl': '{"PurchaseOrderID": "po1", "PurchaseOrderNumber": "PO-001", "Date": "2023-01-01T00:00:00+00:00", "Status": "DRAFT", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_banktransfers(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/BankTransfers",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'BankTransfers': [
                    {
                        'BankTransferID': 'bt1',
                        'Amount': 100.0,
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'banktransfers')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/banktransfers.jsonl': '{"BankTransferID": "bt1", "Amount": 100.0, "Date": "2023-01-01T00:00:00+00:00", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_invoices(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Invoices",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Invoices': [
                    {
                        'InvoiceID': 'inv1',
                        'Type': 'ACCREC',
                        'InvoiceNumber': '12345',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'Total': 100.0,
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'invoices')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/invoices.jsonl': '{"InvoiceID": "inv1", "Type": "ACCREC", "InvoiceNumber": "12345", "Date": "2023-01-01T00:00:00+00:00", "Total": 100.0, "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_creditnotes(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/CreditNotes",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'CreditNotes': [
                    {
                        'CreditNoteID': 'cn1',
                        'Type': 'ACCRECCREDIT',
                        'CreditNoteNumber': 'CN-12345',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'Total': 50.0,
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'creditnotes')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/creditnotes.jsonl': '{"CreditNoteID": "cn1", "Type": "ACCRECCREDIT", "CreditNoteNumber": "CN-12345", "Date": "2023-01-01T00:00:00+00:00", "Total": 50.0, "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_currencies(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Currencies",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Currencies': [
                    {
                        'Code': 'USD',
                        'Description': 'United States Dollar',
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'currencies')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/currencies.jsonl': '{"Code": "USD", "Description": "United States Dollar"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_employees(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Employees",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Employees': [
                    {
                        'EmployeeID': 'emp1',
                        'FirstName': 'John',
                        'LastName': 'Doe',
                        'Status': 'ACTIVE',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'employees')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/employees.jsonl': '{"EmployeeID": "emp1", "FirstName": "John", "LastName": "Doe", "Status": "ACTIVE", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_items(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Items",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Items': [
                    {
                        'ItemID': 'item1',
                        'Code': 'WIDGET',
                        'Name': 'Blue Widget',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'items')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/items.jsonl': '{"ItemID": "item1", "Code": "WIDGET", "Name": "Blue Widget", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_manualjournals(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/ManualJournals",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'ManualJournals': [
                    {
                        'ManualJournalID': 'mj1',
                        'Narration': 'Test manual journal',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'Status': 'POSTED',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'manualjournals')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/manualjournals.jsonl': '{"ManualJournalID": "mj1", "Narration": "Test manual journal", "Date": "2023-01-01T00:00:00+00:00", "Status": "POSTED", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_specific_endpoint_multiple_tenants(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
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
                'Tenant 1/latest.json': snapshot,
                'Tenant 2/contacts.jsonl': '{"ContactID": "c2", "Name": "Cont 2", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 2/tenant.json': '{"tenantId": "t2", "tenantName": "Tenant 2"}\n',
                'Tenant 2/latest.json': snapshot,
            },
        )

    def test_journals_uses_journals_export(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
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
                'Tenant 1/journals-2023-03.jsonl': snapshot,
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_journals_with_rate_limit(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
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
                'Tenant 1/journals-2023-04.jsonl': snapshot,
                'Tenant 1/latest.json': snapshot,
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

    def test_journals_split_days(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
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
            'days',
        )

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/journals-2023-03-15.jsonl': snapshot,
                'Tenant 1/journals-2023-03-16.jsonl': snapshot,
                'Tenant 1/journals-2024-03-15.jsonl': snapshot,
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_journals_split_months(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
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
                'Tenant 1/journals-2023-03.jsonl': snapshot,
                'Tenant 1/journals-2024-03.jsonl': snapshot,
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_journals_split_years(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
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
                'Tenant 1/journals-2023.jsonl': snapshot,
                'Tenant 1/journals-2024.jsonl': snapshot,
                'Tenant 1/latest.json': snapshot,
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
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
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
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_export_update_contacts_new_data(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
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
                f'Tenant 1/contacts.jsonl': snapshot,
                f'Tenant 1/latest.json': snapshot,
            }
        )

    def test_export_update_contacts_no_new_data(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
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
                f'Tenant 1/contacts.jsonl': snapshot,
                f'Tenant 1/latest.json': snapshot,
            }
        )

    def test_export_update_multiple_endpoints(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
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
                'Tenant 1/accounts.jsonl': snapshot,  # Overwritten with new a1 (updated) and a2
                'Tenant 1/contacts.jsonl': snapshot,  # Overwritten with c1 (no change)
                'Tenant 1/latest.json': snapshot,
            }
        )

    def add_bank_transaction_response(self, pook: Any, tenant_id: str = 't1') -> None:
        pook.get(
            f"{XERO_API_URL}/BankTransactions",
            headers={'Xero-Tenant-Id': tenant_id},
            params={'page': '1', 'pageSize': '1000'},
            reply=200,
            response_json={
                'Status': 'OK',
                'BankTransactions': [
                    {
                        'BankTransactionID': 'bt1',
                        'Date': '/Date(1678838400000+0000)/',  # 2023-03-15
                        "DateString": "2023-03-15T00:00:00",
                        'UpdatedDateUTC': '/Date(1678838400000+0000)/',
                        'Total': 100.0,
                        'Type': 'SPEND',
                        'BankAccount': {'Name': 'Test Account'},
                    },
                    {
                        'BankTransactionID': 'bt2',
                        'Date': '/Date(1678924800000+0000)/',  # 2023-03-16
                        "DateString": "2023-03-16T00:00:00",
                        'UpdatedDateUTC': '/Date(1678924800000+0000)/',
                        'Total': 200.0,
                        'Type': 'RECEIVE',
                        'BankAccount': {'Name': 'Test Account'},
                    },
                    {
                        'BankTransactionID': 'bt3',
                        'Date': '/Date(1710460800000+0000)/',  # 2024-03-15
                        "DateString": "2024-03-15T00:00:00",
                        'UpdatedDateUTC': '/Date(1710460800000+0000)/',
                        'Total': 300.0,
                        'Type': 'SPEND',
                        'BankAccount': {'Name': 'Test Account'},
                    },
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/BankTransactions",
            headers={'Xero-Tenant-Id': tenant_id},
            params={'page': '2', 'pageSize': '1000'},
            reply=200,
            response_json={'Status': 'OK', 'BankTransactions': []},
        )

    def test_bank_transactions_uses_bank_transactions_export(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])
        self.add_bank_transaction_response(pook)

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'banktransactions')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/transactions-2023-03.jsonl': snapshot,
                'Tenant 1/transactions-2024-03.jsonl': snapshot,
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_bank_transactions_split_days(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])
        self.add_bank_transaction_response(pook)

        run_cli(
            tmp_path,
            'export',
            '--path',
            str(tmp_path),
            '--tenant',
            't1',
            'banktransactions',
            '--split',
            'days',
        )

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/transactions-2023-03-15.jsonl': snapshot,
                'Tenant 1/transactions-2023-03-16.jsonl': snapshot,
                'Tenant 1/transactions-2024-03-15.jsonl': snapshot,
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_bank_transactions_split_months(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])
        self.add_bank_transaction_response(pook)

        run_cli(
            tmp_path,
            'export',
            '--path',
            str(tmp_path),
            '--tenant',
            't1',
            'banktransactions',
            '--split',
            'months',
        )

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/transactions-2023-03.jsonl': snapshot,
                'Tenant 1/transactions-2024-03.jsonl': snapshot,
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_bank_transactions_split_none(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])
        self.add_bank_transaction_response(pook)

        run_cli(
            tmp_path,
            'export',
            '--path',
            str(tmp_path),
            '--tenant',
            't1',
            'banktransactions',
            '--split',
            'none',
        )

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/transactions.jsonl': snapshot,
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_export_update_bank_transactions_new_data(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        tenant_path = tmp_path / "Tenant 1"
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        self.write_json(
            tenant_path / 'latest.json',
            {"BankTransactions": {"UpdatedDateUTC": "2023-03-15T00:00:00+00:00"}},
        )
        self.write_json(
            tenant_path / 'transactions-2023-03.jsonl',
            {
                'BankTransactionID': 'bt1',
                'Date': '2023-03-15T00:00:00+00:00',
                'UpdatedDateUTC': '2023-03-15T00:00:00+00:00',
                'Total': 100.0,
                'Type': 'SPEND',
                'BankAccount': {'Name': 'Test Account'},
            },
        )

        pook.get(
            f"{XERO_API_URL}/BankTransactions",
            headers={
                'Xero-Tenant-Id': 't1',
                'If-Modified-Since': 'Wed, 15 Mar 2023 00:00:00 GMT',
            },
            params={'page': '1', 'pageSize': '1000'},
            reply=200,
            response_json={
                'Status': 'OK',
                'BankTransactions': [
                    {
                        'BankTransactionID': 'bt2',
                        'Date': '/Date(1678924800000+0000)/',
                        'UpdatedDateUTC': '/Date(1678924800000+0000)/',
                        'Total': 200.0,
                        'Type': 'RECEIVE',
                        'BankAccount': {'Name': 'Test Account'},
                    },
                    {
                        'BankTransactionID': 'bt3',
                        'Date': '/Date(1710460800000+0000)/',
                        'UpdatedDateUTC': '/Date(1710460800000+0000)/',
                        'Total': 300.0,
                        'Type': 'SPEND',
                        'BankAccount': {'Name': 'Test Account'},
                    },
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/BankTransactions",
            headers={
                'Xero-Tenant-Id': 't1',
                'If-Modified-Since': 'Fri, 15 Mar 2024 00:00:00 GMT',
            },
            params={'page': '2', 'pageSize': '1000'},
            reply=200,
            response_json={'Status': 'OK', 'BankTransactions': []},
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'banktransactions')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/transactions-2023-03.jsonl': snapshot,
                'Tenant 1/transactions-2024-03.jsonl': snapshot,
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_export_update_bank_transactions_no_new_data(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        tenant_path = tmp_path / "Tenant 1"
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        self.write_json(
            tenant_path / 'latest.json',
            {"BankTransactions": {"UpdatedDateUTC": "2023-03-15T00:00:00+00:00"}},
        )
        self.write_json(tenant_path / 'transactions-2023-03.jsonl', {"LEAVE": "THIS"})

        pook.get(
            f"{XERO_API_URL}/BankTransactions",
            headers={
                'Xero-Tenant-Id': 't1',
                'If-Modified-Since': 'Wed, 15 Mar 2023 00:00:00 GMT',
            },
            reply=200,
            response_json={'Status': 'OK', 'BankTransactions': []},
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'banktransactions')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/transactions-2023-03.jsonl': snapshot,
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_export_update_bank_transactions_duplicate_last_item(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        tenant_path = tmp_path / "Tenant 1"
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        timestamp = "2023-03-15T00:00:00.123456+00:00"
        item = {
            'BankTransactionID': 'bt1',
            'Date': '/Date(1678838400123+0000)/',
            'UpdatedDateUTC': '/Date(1678838400123+0000)/',
            'Total': 100.0,
            'Type': 'SPEND',
            'BankAccount': {'Name': 'Test Account'},
        }

        self.write_json(
            tenant_path / 'latest.json',
            {"BankTransactions": {"UpdatedDateUTC": timestamp}},
        )
        self.write_json(
            tenant_path / 'transactions-2023-03.jsonl',
            {
                'BankTransactionID': 'bt1',
                'Date': '2023-03-15T00:00:00+00:00',
                'UpdatedDateUTC': timestamp,
                'Total': 100.0,
                'Type': 'SPEND',
                'BankAccount': {'Name': 'Test Account'},
            },
        )

        pook.get(
            f"{XERO_API_URL}/BankTransactions",
            headers={
                'Xero-Tenant-Id': 't1',
                'If-Modified-Since': 'Wed, 15 Mar 2023 00:00:00 GMT',
            },
            params={'page': '1', 'pageSize': '1000'},
            reply=200,
            response_json={'Status': 'OK', 'BankTransactions': [item]},
        )
        pook.get(
            f"{XERO_API_URL}/BankTransactions",
            headers={
                'Xero-Tenant-Id': 't1',
                'If-Modified-Since': 'Wed, 15 Mar 2023 00:00:00 GMT',
            },
            params={'page': '2', 'pageSize': '1000'},
            reply=200,
            response_json={'Status': 'OK', 'BankTransactions': []},
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'banktransactions')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/transactions-2023-03.jsonl': snapshot,
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_export_update_bank_transactions_with_rate_limit(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        tenant_path = tmp_path / "Tenant 1"
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        self.write_json(
            tenant_path / 'latest.json',
            {"BankTransactions": {"UpdatedDateUTC": "2023-03-15T00:00:00+00:00"}},
        )
        self.write_json(tenant_path / 'transactions-2023-03.jsonl', {"LEAVE": "THIS"})

        # First request hits rate limit
        pook.get(
            f"{XERO_API_URL}/BankTransactions",
            headers={
                'Xero-Tenant-Id': 't1',
                'If-Modified-Since': 'Wed, 15 Mar 2023 00:00:00 GMT',
            },
            params={'page': '1', 'pageSize': '1000'},
            reply=429,  # Rate limit exceeded
            response_headers={'retry-after': '1'},
        )

        # Second request (after retry) succeeds
        pook.get(
            f"{XERO_API_URL}/BankTransactions",
            headers={
                'Xero-Tenant-Id': 't1',
                'If-Modified-Since': 'Wed, 15 Mar 2023 00:00:00 GMT',
            },
            params={'page': '1', 'pageSize': '1000'},
            reply=200,
            response_json={
                'Status': 'OK',
                'BankTransactions': [
                    {
                        'BankTransactionID': 'bt1',
                        'Date': '/Date(1678924800000+0000)/',  # 2023-03-16
                        'UpdatedDateUTC': '/Date(1678924800000+0000)/',
                        'Total': 100.0,
                        'Type': 'SPEND',
                        'BankAccount': {'Name': 'Test Account'},
                    },
                ],
            },
        )

        # End of pagination
        pook.get(
            f"{XERO_API_URL}/BankTransactions",
            headers={
                'Xero-Tenant-Id': 't1',
                'If-Modified-Since': 'Thu, 16 Mar 2023 00:00:00 GMT',
            },
            params={'page': '2', 'pageSize': '1000'},
            reply=200,
            response_json={'Status': 'OK', 'BankTransactions': []},
        )

        # Mock the sleep function to avoid actually waiting
        mock_sleep = Mock()

        with replace_in_module(time.sleep, mock_sleep, module=export):
            run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'banktransactions')

        # Verify sleep was called with retry-after value
        mock_sleep.assert_called_once_with(1)

        # Verify the bank transaction was exported after retrying
        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/transactions-2023-03.jsonl': snapshot,
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_export_update_bank_transactions_same_updated_date(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        tenant_path = tmp_path / "Tenant 1"
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        self.write_json(
            tenant_path / 'latest.json',
            {"BankTransactions": {"UpdatedDateUTC": "2023-03-15T00:00:00+00:00"}},
        )
        self.write_json(
            tenant_path / 'transactions-2023-03.jsonl',
            {
                'BankTransactionID': 'bt1',
                'Date': '2023-03-15T00:00:00+00:00',
                'UpdatedDateUTC': '2023-03-15T00:00:00+00:00',
                'Total': 100.0,
                'Type': 'SPEND',
                'BankAccount': {'Name': 'Test Account'},
            },
        )

        pook.get(
            f"{XERO_API_URL}/BankTransactions",
            headers={
                'Xero-Tenant-Id': 't1',
                'If-Modified-Since': 'Wed, 15 Mar 2023 00:00:00 GMT',
            },
            params={'page': '1', 'pageSize': '1000'},
            reply=200,
            response_json={
                'Status': 'OK',
                'BankTransactions': [
                    {
                        'BankTransactionID': 'bt2',
                        'Date': '/Date(1678924800000+0000)/',
                        'UpdatedDateUTC': '/Date(1679184000000+0000)/',
                        'Total': 200.0,
                        'Type': 'RECEIVE',
                        'BankAccount': {'Name': 'Test Account'},
                    },
                    {
                        'BankTransactionID': 'bt3',
                        'Date': '/Date(1679011200000+0000)/',
                        'UpdatedDateUTC': '/Date(1679184000000+0000)/',
                        'Total': 300.0,
                        'Type': 'SPEND',
                        'BankAccount': {'Name': 'Test Account'},
                    },
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/BankTransactions",
            headers={
                'Xero-Tenant-Id': 't1',
                'If-Modified-Since': 'Sun, 19 Mar 2023 00:00:00 GMT',
            },
            params={'page': '2', 'pageSize': '1000'},
            reply=200,
            response_json={'Status': 'OK', 'BankTransactions': []},
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'banktransactions')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/transactions-2023-03.jsonl': snapshot,
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_organisations(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Organisations",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Organisations': [
                    {
                        'OrganisationID': 'org1',
                        'Name': 'Test Organisation',
                        'LegalName': 'Test Organisation Ltd',
                        'BaseCurrency': 'USD',
                        'CountryCode': 'US',
                        'CreatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'organisations')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/organisations.jsonl': '{"OrganisationID": "org1", "Name": "Test Organisation", "LegalName": "Test Organisation Ltd", "BaseCurrency": "USD", "CountryCode": "US", "CreatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_overpayments(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Overpayments",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Overpayments': [
                    {
                        'OverpaymentID': 'op1',
                        'Type': 'RECEIVE-OVERPAYMENT',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'Total': 150.0,
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'overpayments')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/overpayments.jsonl': '{"OverpaymentID": "op1", "Type": "RECEIVE-OVERPAYMENT", "Date": "2023-01-01T00:00:00+00:00", "Total": 150.0, "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_payments(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Payments",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Payments': [
                    {
                        'PaymentID': 'pay1',
                        'Amount': 100.0,
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'PaymentType': 'ACCRECPAYMENT',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'payments')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/payments.jsonl': '{"PaymentID": "pay1", "Amount": 100.0, "Date": "2023-01-01T00:00:00+00:00", "PaymentType": "ACCRECPAYMENT", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_prepayments(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Prepayments",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Prepayments': [
                    {
                        'PrepaymentID': 'pp1',
                        'Type': 'RECEIVE-PREPAYMENT',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'Total': 200.0,
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'prepayments')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/prepayments.jsonl': '{"PrepaymentID": "pp1", "Type": "RECEIVE-PREPAYMENT", "Date": "2023-01-01T00:00:00+00:00", "Total": 200.0, "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_purchaseorders(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/PurchaseOrders",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'PurchaseOrders': [
                    {
                        'PurchaseOrderID': 'po1',
                        'PurchaseOrderNumber': 'PO-001',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'Status': 'DRAFT',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'purchaseorders')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/purchaseorders.jsonl': '{"PurchaseOrderID": "po1", "PurchaseOrderNumber": "PO-001", "Date": "2023-01-01T00:00:00+00:00", "Status": "DRAFT", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )
