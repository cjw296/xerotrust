import csv
from datetime import datetime
from pathlib import Path

from testfixtures import compare

from xerotrust.csv_export import TransactionCSVWriter


def test_write_invoice_with_line_items(tmp_path: Path) -> None:
    """Test writing an invoice with multiple line items creates multiple rows."""
    csv_path = tmp_path / "test.csv"

    invoice = {
        'Type': 'ACCREC',
        'Contact': {
            'ContactID': 'contact-123',
            'Name': 'Test Customer',
            'EmailAddress': 'test@example.com',
        },
        'Date': datetime(2024, 6, 29),
        'InvoiceID': 'inv-123',
        'InvoiceNumber': 'INV-001',
        'LineAmountTypes': 'Inclusive',
        'SubTotal': 350.0,
        'TotalTax': 70.0,
        'Total': 420.0,
        'Status': 'PAID',
        'CurrencyCode': 'GBP',
        'HasAttachments': True,
        'UpdatedDateUTC': datetime(2024, 8, 27),
        'LineItems': [
            {
                'AccountCode': '200',
                'AccountName': 'Sales',
                'Description': 'Consulting services',
                'Quantity': 1.0,
                'UnitAmount': 200.0,
                'LineAmount': 200.0,
                'TaxType': '20% (VAT on Income)',
                'TaxAmount': 40.0,
                'Tracking': [{'Name': 'Region', 'Option': 'North'}],
            },
            {
                'AccountCode': '260',
                'AccountName': 'Other Revenue',
                'Description': 'Project management',
                'Quantity': 2.0,
                'UnitAmount': 110.0,
                'LineAmount': 220.0,
                'TaxType': '20% (VAT on Income)',
                'TaxAmount': 44.0,
            },
        ],
    }

    with TransactionCSVWriter(csv_path) as writer:
        writer.write_item(invoice)

    # read CSV and verify
    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # should have 2 rows (one per line item)
    compare(len(rows), expected=2)

    # verify first row
    row1 = rows[0]
    compare(row1['Type'], expected='ACCREC')
    compare(row1['Contact.Name'], expected='Test Customer')
    compare(row1['Contact.EmailAddress'], expected='test@example.com')
    compare(row1['Date'], expected='2024/06/29')
    compare(row1['InvoiceNumber'], expected='INV-001')
    compare(row1['LineAmountTypes'], expected='Inclusive')
    compare(row1['LineItem.AccountCode'], expected='200')
    compare(row1['LineItem.Description'], expected='Consulting services')
    compare(row1['LineItem.Quantity'], expected='1.0')
    compare(row1['LineItem.UnitAmount'], expected='200.0')
    compare(row1['LineItem.TaxType'], expected='20% (VAT on Income)')
    compare(row1['LineItem.Tracking.Name'], expected='Region')
    compare(row1['LineItem.Tracking.Option'], expected='North')
    compare(row1['SubTotal'], expected='350.0')
    compare(row1['Total'], expected='420.0')
    compare(row1['Status'], expected='PAID')
    compare(row1['HasAttachments'], expected='True')
    compare(row1['InvoiceID'], expected='inv-123')
    compare(row1['ContactID'], expected='contact-123')

    # verify second row (same parent fields, different line item)
    row2 = rows[1]
    compare(row2['Type'], expected='ACCREC')
    compare(row2['InvoiceNumber'], expected='INV-001')
    compare(row2['LineItem.AccountCode'], expected='260')
    compare(row2['LineItem.Description'], expected='Project management')
    compare(row2['LineItem.Quantity'], expected='2.0')
    compare(row2['LineItem.Tracking.Name'], expected='')  # no tracking on this line


def test_write_bank_transaction_without_line_items(tmp_path: Path) -> None:
    """Test writing a bank transaction without line items creates a single row."""
    csv_path = tmp_path / "test.csv"

    transaction = {
        'Type': 'SPEND',
        'Contact': {'ContactID': 'contact-456', 'Name': 'Supplier Co'},
        'Date': datetime(2024, 7, 15),
        'BankTransactionID': 'bt-456',
        'Reference': 'REF-123',
        'Total': 150.0,
        'Status': 'AUTHORISED',
        'CurrencyCode': 'USD',
        'UpdatedDateUTC': datetime(2024, 7, 20),
        'HasAttachments': False,
    }

    with TransactionCSVWriter(csv_path) as writer:
        writer.write_item(transaction)

    # read CSV and verify
    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # should have 1 row
    compare(len(rows), expected=1)

    row = rows[0]
    compare(row['Type'], expected='SPEND')
    compare(row['Contact.Name'], expected='Supplier Co')
    compare(row['Date'], expected='2024/07/15')
    compare(row['Reference'], expected='REF-123')
    compare(row['Total'], expected='150.0')
    compare(row['Status'], expected='AUTHORISED')
    compare(row['BankTransactionID'], expected='bt-456')
    compare(row['ContactID'], expected='contact-456')

    # line item fields should be empty
    compare(row['LineItem.AccountCode'], expected='')
    compare(row['LineItem.Description'], expected='')


def test_write_credit_note_with_single_line_item(tmp_path: Path) -> None:
    """Test writing a credit note with a single line item."""
    csv_path = tmp_path / "test.csv"

    credit_note = {
        'Type': 'ACCRECCREDIT',
        'Contact': {'ContactID': 'contact-789', 'Name': 'Refund Customer'},
        'Date': datetime(2024, 8, 1),
        'CreditNoteID': 'cn-789',
        'CreditNoteNumber': 'CN-001',
        'SubTotal': 100.0,
        'TotalTax': 20.0,
        'Total': 120.0,
        'Status': 'AUTHORISED',
        'CurrencyCode': 'EUR',
        'UpdatedDateUTC': datetime(2024, 8, 5),
        'LineItems': [
            {
                'AccountCode': '310',
                'Description': 'Product return',
                'Quantity': 1.0,
                'UnitAmount': 100.0,
                'LineAmount': 100.0,
                'TaxType': '20% VAT',
                'TaxAmount': 20.0,
            }
        ],
    }

    with TransactionCSVWriter(csv_path) as writer:
        writer.write_item(credit_note)

    # read CSV and verify
    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # should have 1 row
    compare(len(rows), expected=1)

    row = rows[0]
    compare(row['Type'], expected='ACCRECCREDIT')
    compare(row['CreditNoteNumber'], expected='CN-001')
    compare(row['LineItem.Description'], expected='Product return')


def test_date_formatting(tmp_path: Path) -> None:
    """Test that dates are formatted consistently."""
    csv_path = tmp_path / "test.csv"

    item = {
        'Type': 'ACCREC',
        'Date': datetime(2024, 1, 5),
        'UpdatedDateUTC': '2024-01-10T15:30:00Z',
        'FullyPaidOnDate': datetime(2024, 1, 15),
    }

    with TransactionCSVWriter(csv_path) as writer:
        writer.write_item(item)

    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row = next(reader)

    compare(row['Date'], expected='2024/01/05')
    compare(row['UpdatedDateUTC'], expected='2024/01/10')
    compare(row['FullyPaidOnDate'], expected='2024/01/15')


def test_empty_values_handled(tmp_path: Path) -> None:
    """Test that missing/None values are handled correctly."""
    csv_path = tmp_path / "test.csv"

    item = {
        'Type': 'ACCREC',
        'Contact': None,
        'Date': None,
        'Reference': '',
        'Total': 0,
        'LineItems': [],
    }

    with TransactionCSVWriter(csv_path) as writer:
        writer.write_item(item)

    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row = next(reader)

    compare(row['Contact.Name'], expected='')
    compare(row['Date'], expected='')
    compare(row['Reference'], expected='')
    compare(row['Total'], expected='0')


def test_multiple_items_written_sequentially(tmp_path: Path) -> None:
    """Test writing multiple items to the same CSV."""
    csv_path = tmp_path / "test.csv"

    items = [
        {
            'Type': 'ACCREC',
            'InvoiceNumber': 'INV-001',
            'Total': 100.0,
            'LineItems': [{'Description': 'Item 1'}],
        },
        {
            'Type': 'ACCPAY',
            'InvoiceNumber': 'BILL-001',
            'Total': 200.0,
            'LineItems': [{'Description': 'Item 2'}],
        },
        {'Type': 'SPEND', 'Reference': 'REF-001', 'Total': 50.0},
    ]

    with TransactionCSVWriter(csv_path) as writer:
        for item in items:
            writer.write_item(item)

    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # should have 3 rows
    compare(len(rows), expected=3)
    compare(rows[0]['InvoiceNumber'], expected='INV-001')
    compare(rows[1]['InvoiceNumber'], expected='BILL-001')
    compare(rows[2]['Reference'], expected='REF-001')


def test_contact_list_fields_joined(tmp_path: Path) -> None:
    """Test that contact fields with lists are properly joined."""
    csv_path = tmp_path / "test.csv"

    item = {
        'Type': 'ACCREC',
        'Contact': {
            'Name': 'Test Co',
            'ContactPersons': ['John Doe', 'Jane Smith'],
            'Phones': ['+1-555-1234', '+1-555-5678'],
            'Addresses': ['123 Main St', '456 Oak Ave'],
        },
    }

    with TransactionCSVWriter(csv_path) as writer:
        writer.write_item(item)

    with csv_path.open('r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        row = next(reader)

    compare(row['Contact.Persons'], expected='John Doe; Jane Smith')
    compare(row['Contact.Phones'], expected='+1-555-1234; +1-555-5678')
    compare(row['Contact.Addresses'], expected='123 Main St; 456 Oak Ave')
