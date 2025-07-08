import json
import time
from pathlib import Path
from textwrap import dedent
from typing import Any

from unittest.mock import Mock

import pytest
from pytest_insta import SnapshotFixture
from testfixtures import replace_in_module, ShouldRaise, compare
from xero.exceptions import XeroInternalError

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
        pook.get(
            f"{XERO_API_URL}/RepeatingInvoices",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'RepeatingInvoices': [
                    {
                        'RepeatingInvoiceID': 'ri1',
                        'Type': 'ACCREC',
                        'Status': 'AUTHORISED',
                        'Total': 100.0,
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/TaxRates",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'TaxRates': [
                    {
                        'Name': 'GST',
                        'TaxType': 'OUTPUT',
                        'DisplayTaxRate': 10.0,
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/TrackingCategories",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'TrackingCategories': [
                    {
                        'TrackingCategoryID': 'tc1',
                        'Name': 'Region',
                        'Status': 'ACTIVE',
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Users",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Users': [
                    {
                        'UserID': 'u1',
                        'EmailAddress': 'user@example.com',
                        'FirstName': 'John',
                        'LastName': 'Smith',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'IsSubscriber': True,
                        'OrganisationRole': 'STANDARD',
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/BrandingThemes",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'BrandingThemes': [
                    {
                        'BrandingThemeID': 'bt1',
                        'Name': 'Default Theme',
                        'SortOrder': 1,
                        'CreatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/ContactGroups",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'ContactGroups': [
                    {
                        'ContactGroupID': 'cg1',
                        'Name': 'VIP Customers',
                        'Status': 'ACTIVE',
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/Quotes",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Quotes': [
                    {
                        'QuoteID': 'q1',
                        'QuoteNumber': 'QU-001',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'ExpiryDate': '/Date(1675209600000+0000)/',  # 2023-02-01
                        'Status': 'DRAFT',
                        'Total': 500.0,
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )
        pook.get(
            f"{XERO_API_URL}/BatchPayments",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'BatchPayments': [
                    {
                        'BatchPaymentID': 'bp1',
                        'Reference': 'BP-001',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'Amount': 1000.0,
                        'Type': 'PAYBATCH',
                        'Status': 'AUTHORISED',
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
                'Tenant 1/repeatinginvoices.jsonl': '{"RepeatingInvoiceID": "ri1", "Type": "ACCREC", "Status": "AUTHORISED", "Total": 100.0}\n',
                'Tenant 1/taxrates.jsonl': '{"Name": "GST", "TaxType": "OUTPUT", "DisplayTaxRate": 10.0}\n',
                'Tenant 1/trackingcategories.jsonl': '{"TrackingCategoryID": "tc1", "Name": "Region", "Status": "ACTIVE"}\n',
                'Tenant 1/users.jsonl': '{"UserID": "u1", "EmailAddress": "user@example.com", "FirstName": "John", "LastName": "Smith", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00", "IsSubscriber": true, "OrganisationRole": "STANDARD"}\n',
                'Tenant 1/brandingthemes.jsonl': '{"BrandingThemeID": "bt1", "Name": "Default Theme", "SortOrder": 1, "CreatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/contactgroups.jsonl': '{"ContactGroupID": "cg1", "Name": "VIP Customers", "Status": "ACTIVE"}\n',
                'Tenant 1/quotes.jsonl': '{"QuoteID": "q1", "QuoteNumber": "QU-001", "Date": "2023-01-01T00:00:00+00:00", "ExpiryDate": "2023-02-01T00:00:00+00:00", "Status": "DRAFT", "Total": 500.0, "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/batchpayments.jsonl': '{"BatchPaymentID": "bp1", "Reference": "BP-001", "Date": "2023-01-01T00:00:00+00:00", "Amount": 1000.0, "Type": "PAYBATCH", "Status": "AUTHORISED", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_banktransfers(self, tmp_path: Path, pook: Any, check_files: FileChecker) -> None:
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
                'Tenant 1/latest.json': '{\n  "BankTransfers": {\n    "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"\n  }\n}\n',
            }
        )

    def test_invoices(self, tmp_path: Path, pook: Any, check_files: FileChecker) -> None:
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
                'Tenant 1/latest.json': '{\n  "Invoices": {\n    "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"\n  }\n}\n',
            }
        )

    def test_creditnotes(self, tmp_path: Path, pook: Any, check_files: FileChecker) -> None:
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
                'Tenant 1/latest.json': '{\n  "CreditNotes": {\n    "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"\n  }\n}\n',
            }
        )

    def test_currencies(self, tmp_path: Path, pook: Any, check_files: FileChecker) -> None:
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
                'Tenant 1/latest.json': '{}\n',
            }
        )

    def test_employees(self, tmp_path: Path, pook: Any, check_files: FileChecker) -> None:
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
                'Tenant 1/latest.json': '{\n  "Employees": {\n    "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"\n  }\n}\n',
            }
        )

    def test_items(self, tmp_path: Path, pook: Any, check_files: FileChecker) -> None:
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
                'Tenant 1/latest.json': '{\n  "Items": {\n    "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"\n  }\n}\n',
            }
        )

    def test_manualjournals(self, tmp_path: Path, pook: Any, check_files: FileChecker) -> None:
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
                'Tenant 1/latest.json': '{\n  "ManualJournals": {\n    "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"\n  }\n}\n',
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

    def test_accounts_with_rate_limit(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        # First request hits rate limit
        pook.get(
            f"{XERO_API_URL}/Accounts",
            headers={'Xero-Tenant-Id': 't1'},
            reply=429,  # Rate limit exceeded
            response_headers={'retry-after': '2'},  # Server responds with retry-after header
        )

        # Second request (after retry) succeeds
        pook.get(
            f"{XERO_API_URL}/Accounts",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Accounts': [
                    {
                        'AccountID': 'a1',
                        'Name': 'Test Account',
                        'Code': '200',
                        'Type': 'BANK',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        # Mock the sleep function to avoid actually waiting
        mock_sleep = Mock()

        with replace_in_module(time.sleep, mock_sleep, module=export):
            # Run the export command for accounts only
            run_cli(tmp_path, 'export', 'accounts', '--path', str(tmp_path))

        # Verify sleep was called with retry-after value
        mock_sleep.assert_called_once_with(2)

        # Verify the account was exported after retrying
        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/accounts.jsonl': '{"AccountID": "a1", "Name": "Test Account", "Code": "200", "Type": "BANK", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
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

    def test_repeatinginvoices(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/RepeatingInvoices",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'RepeatingInvoices': [
                    {
                        'RepeatingInvoiceID': 'ri1',
                        'Type': 'ACCREC',
                        'Status': 'AUTHORISED',
                        'Total': 100.0,
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'repeatinginvoices')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/repeatinginvoices.jsonl': '{"RepeatingInvoiceID": "ri1", "Type": "ACCREC", "Status": "AUTHORISED", "Total": 100.0}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_taxrates(self, tmp_path: Path, pook: Any, check_files: FileChecker) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/TaxRates",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'TaxRates': [
                    {
                        'Name': 'GST',
                        'TaxType': 'OUTPUT',
                        'DisplayTaxRate': 10.0,
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'taxrates')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/taxrates.jsonl': '{"Name": "GST", "TaxType": "OUTPUT", "DisplayTaxRate": 10.0}\n',
                'Tenant 1/latest.json': '{}\n',
            }
        )

    def test_trackingcategories(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/TrackingCategories",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'TrackingCategories': [
                    {
                        'TrackingCategoryID': 'tc1',
                        'Name': 'Region',
                        'Status': 'ACTIVE',
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'trackingcategories')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/trackingcategories.jsonl': '{"TrackingCategoryID": "tc1", "Name": "Region", "Status": "ACTIVE"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_users(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Users",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Users': [
                    {
                        'UserID': 'u1',
                        'EmailAddress': 'user@example.com',
                        'FirstName': 'John',
                        'LastName': 'Smith',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'IsSubscriber': True,
                        'OrganisationRole': 'STANDARD',
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'users')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/users.jsonl': '{"UserID": "u1", "EmailAddress": "user@example.com", "FirstName": "John", "LastName": "Smith", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00", "IsSubscriber": true, "OrganisationRole": "STANDARD"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_brandingthemes(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/BrandingThemes",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'BrandingThemes': [
                    {
                        'BrandingThemeID': 'bt1',
                        'Name': 'Default Theme',
                        'SortOrder': 1,
                        'CreatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'brandingthemes')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/brandingthemes.jsonl': '{"BrandingThemeID": "bt1", "Name": "Default Theme", "SortOrder": 1, "CreatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_contactgroups(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/ContactGroups",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'ContactGroups': [
                    {
                        'ContactGroupID': 'cg1',
                        'Name': 'VIP Customers',
                        'Status': 'ACTIVE',
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'contactgroups')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/contactgroups.jsonl': '{"ContactGroupID": "cg1", "Name": "VIP Customers", "Status": "ACTIVE"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_quotes(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Quotes",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Quotes': [
                    {
                        'QuoteID': 'q1',
                        'QuoteNumber': 'QU-001',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'ExpiryDate': '/Date(1675209600000+0000)/',  # 2023-02-01
                        'Status': 'DRAFT',
                        'Total': 500.0,
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'quotes')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/quotes.jsonl': '{"QuoteID": "q1", "QuoteNumber": "QU-001", "Date": "2023-01-01T00:00:00+00:00", "ExpiryDate": "2023-02-01T00:00:00+00:00", "Status": "DRAFT", "Total": 500.0, "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_batchpayments(
        self, tmp_path: Path, pook: Any, check_files: FileChecker, snapshot: SnapshotFixture
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/BatchPayments",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'BatchPayments': [
                    {
                        'BatchPaymentID': 'bp1',
                        'Reference': 'BP-001',
                        'Date': '/Date(1672531200000+0000)/',  # 2023-01-01
                        'Amount': 1000.0,
                        'Type': 'PAYBATCH',
                        'Status': 'AUTHORISED',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--tenant', 't1', 'batchpayments')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/batchpayments.jsonl': '{"BatchPaymentID": "bp1", "Reference": "BP-001", "Date": "2023-01-01T00:00:00+00:00", "Amount": 1000.0, "Type": "PAYBATCH", "Status": "AUTHORISED", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                'Tenant 1/latest.json': snapshot,
            }
        )

    def test_currencies_with_update(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        """Test that currencies endpoint works with --update despite having no tracking fields."""
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Currencies",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Currencies': [{'Code': 'USD', 'Description': 'United States Dollar'}],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'currencies')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/currencies.jsonl': '{"Code": "USD", "Description": "United States Dollar"}\n',
                'Tenant 1/latest.json': '{}\n',
            }
        )

    def test_taxrates_with_update(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        """Test that taxrates endpoint works with --update despite having no tracking fields."""
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/TaxRates",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'TaxRates': [
                    {
                        'Name': 'GST',
                        'TaxType': 'OUTPUT',
                        'DisplayTaxRate': 10.0,
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'taxrates')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/taxrates.jsonl': '{"Name": "GST", "TaxType": "OUTPUT", "DisplayTaxRate": 10.0}\n',
                'Tenant 1/latest.json': '{}\n',
            }
        )

    def test_trackingcategories_with_update(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        """Test that trackingcategories endpoint works with --update despite having no tracking fields."""
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/TrackingCategories",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'TrackingCategories': [
                    {
                        'Name': 'Region',
                        'Status': 'ACTIVE',
                        'TrackingCategoryID': 'tc1',
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'trackingcategories')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/trackingcategories.jsonl': '{"Name": "Region", "Status": "ACTIVE", "TrackingCategoryID": "tc1"}\n',
                'Tenant 1/latest.json': '{}\n',
            }
        )

    def test_contactgroups_with_update(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        """Test that contactgroups endpoint works with --update despite having no tracking fields."""
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/ContactGroups",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'ContactGroups': [
                    {
                        'Name': 'Suppliers',
                        'Status': 'ACTIVE',
                        'ContactGroupID': 'cg1',
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'contactgroups')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/contactgroups.jsonl': '{"Name": "Suppliers", "Status": "ACTIVE", "ContactGroupID": "cg1"}\n',
                'Tenant 1/latest.json': '{}\n',
            }
        )

    def test_repeatinginvoices_with_update(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        """Test that repeatinginvoices endpoint works with --update despite having no tracking fields."""
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/RepeatingInvoices",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'RepeatingInvoices': [
                    {
                        'Type': 'ACCREC',
                        'Status': 'AUTHORISED',
                        'RepeatingInvoiceID': 'ri1',
                        'Total': 100.0,
                    }
                ],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'repeatinginvoices')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/repeatinginvoices.jsonl': '{"Type": "ACCREC", "Status": "AUTHORISED", "RepeatingInvoiceID": "ri1", "Total": 100.0}\n',
                'Tenant 1/latest.json': '{}\n',
            }
        )

    def test_update_from_latest_json_with_nulls(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        """Ensure that latest.json can be parsed when it has null and {} values"""
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Currencies",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={'Status': 'OK', 'Currencies': []},
        )

        pook.get(
            f"{XERO_API_URL}/TaxRates",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={'Status': 'OK', 'TaxRates': []},
        )

        self.write_json(
            tmp_path / "Tenant 1" / 'latest.json',
            {"Currencies": None, "TaxRates": {}},
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), '--update', 'currencies', 'taxrates')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/latest.json': '{}\n',
            }
        )

    def test_endpoint_with_no_results(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        pook.get(
            f"{XERO_API_URL}/Employees",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Employees': [],
            },
        )

        run_cli(tmp_path, 'export', '--path', str(tmp_path), 'employees')

        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/latest.json': '{}\n',
            }
        )

    def test_export_error_handling_with_endpoint_context(
        self, tmp_path: Path, pook: Any, check_files: FileChecker
    ) -> None:
        """Test that export errors include context about which endpoint failed."""
        add_tenants_response(pook, [{'tenantId': 't1', 'tenantName': 'Tenant 1'}])

        # First endpoint succeeds
        pook.get(
            f"{XERO_API_URL}/Accounts",
            headers={'Xero-Tenant-Id': 't1'},
            reply=200,
            response_json={
                'Status': 'OK',
                'Accounts': [
                    {
                        'AccountID': 'a1',
                        'Name': 'Test Account',
                        'UpdatedDateUTC': '/Date(1672531200000+0000)/',  # 2023-01-01
                    }
                ],
            },
        )

        # Second endpoint fails with 500 error
        pook.get(
            f"{XERO_API_URL}/Contacts",
            headers={'Xero-Tenant-Id': 't1'},
            reply=500,
            response_json={'Status': 'ERROR', 'Message': 'Internal Server Error'},
        )

        # Third endpoint would succeed but won't be reached due to error
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

        with ShouldRaise(XeroInternalError) as s:
            run_cli(
                tmp_path,
                'export',
                '--path',
                str(tmp_path),
                '--tenant',
                't1',
                'accounts',
                'contacts',
                'currencies',
            )
        # Verify the error includes context about which endpoint failed
        # The error context should be in the exception notes
        compare(s.raised.__notes__, expected=["while exporting 'Contacts'"])

        # Verify that only the first endpoint was successfully exported before the error
        check_files(
            {
                'Tenant 1/tenant.json': '{"tenantId": "t1", "tenantName": "Tenant 1"}\n',
                'Tenant 1/accounts.jsonl': '{"AccountID": "a1", "Name": "Test Account", "UpdatedDateUTC": "2023-01-01T00:00:00+00:00"}\n',
                # Note: latest.json should NOT exist because the export failed before completion
            }
        )
