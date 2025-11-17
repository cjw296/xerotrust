import csv
import logging
from datetime import datetime
from pathlib import Path
from typing import Any


class TransactionCSVWriter:
    """
    Writes transaction entities to CSV files in a denormalized format.

    For entities with line items, creates multiple rows (one per line item).
    For entities without line items, creates a single row.
    """

    # comprehensive column set covering all transaction types
    COLUMNS = [
        'Type',
        'Contact.Name',
        'Contact.EmailAddress',
        'Contact.Persons',
        'Contact.Addresses',
        'Contact.Phones',
        'Date',
        'Account.Code',
        'Account.Name',
        'Account.Type',
        'AccountsPayableTaxType',
        'AccountsReceivableTaxType',
        'CreditNoteNumber',
        'InvoiceNumber',
        'PurchaseOrderNumber',
        'Reference',
        'LineAmountTypes',
        'LineItem.AccountCode',
        'LineItem.AccountName',
        'LineItem.Description',
        'LineItem.Quantity',
        'LineItem.UnitAmount',
        'LineItem.DiscountRate',
        'LineItem.DiscountAmount',
        'LineItem.LineAmount',
        'LineItem.TaxType',
        'LineItem.TaxAmount',
        'LineItem.Tracking.Name',
        'LineItem.Tracking.Option',
        'Narration',
        'SubTotal',
        'TotalTax',
        'Total',
        'ToBankAccount.Name',
        'CurrencyCode',
        'CurrencyRate',
        'Status',
        'FullyPaidOnDate',
        'UpdatedDateUTC',
        'IsSupplier',
        'IsCustomer',
        'Schedule.StartDate',
        'HasAttachments',
        'AttachmentFolder',
        'AttachmentFilenames',
        'AccountID',
        'ContactID',
        'BankTransactionID',
        'BankTransferID',
        'CreditNoteID',
        'InvoiceID',
        'ManualJournalID',
        'PurchaseOrderID',
        'QuoteID',
        'RepeatingInvoiceID',
    ]

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.file = output_path.open('w', encoding='utf-8', newline='')
        self.writer = csv.DictWriter(self.file, fieldnames=self.COLUMNS, extrasaction='ignore')
        self.writer.writeheader()
        logging.info(f'created CSV file: {output_path}')

    def _format_date(self, value: Any) -> str:
        """Format datetime objects as YYYY/MM/DD strings."""
        if isinstance(value, datetime):
            return value.strftime('%Y/%m/%d')
        if isinstance(value, str):
            # try to parse and reformat
            try:
                dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return dt.strftime('%Y/%m/%d')
            except (ValueError, AttributeError):
                return value
        return str(value) if value is not None else ''

    def _format_contact_field(self, contact: dict[str, Any] | None, field: str) -> str:
        """Extract and format contact sub-fields."""
        if not contact:
            return ''
        value = contact.get(field, '')
        if isinstance(value, list):
            # join list items
            return '; '.join(str(v) for v in value)
        return str(value) if value else ''

    def _format_tracking(self, tracking_categories: list[dict[str, Any]] | None) -> tuple[str, str]:
        """Extract tracking category name and option."""
        if not tracking_categories or not isinstance(tracking_categories, list):
            return '', ''
        # take first tracking category
        first = tracking_categories[0]
        name = first.get('Name', '')
        option = first.get('Option', '')
        return str(name), str(option)

    def _get_base_row(self, item: dict[str, Any]) -> dict[str, str]:
        """Extract base fields common across all line items."""
        contact = item.get('Contact') or {}
        account = item.get('BankAccount') or {}

        row: dict[str, str] = {
            'Type': str(item.get('Type', '')),
            'Contact.Name': self._format_contact_field(contact, 'Name'),
            'Contact.EmailAddress': self._format_contact_field(contact, 'EmailAddress'),
            'Contact.Persons': self._format_contact_field(contact, 'ContactPersons'),
            'Contact.Addresses': self._format_contact_field(contact, 'Addresses'),
            'Contact.Phones': self._format_contact_field(contact, 'Phones'),
            'Date': self._format_date(item.get('Date') or item.get('DateString')),
            'Account.Code': str(account.get('Code', '')),
            'Account.Name': str(account.get('Name', '')),
            'Account.Type': str(account.get('Type', '')),
            'AccountsPayableTaxType': str(item.get('AccountsPayableTaxType', '')),
            'AccountsReceivableTaxType': str(item.get('AccountsReceivableTaxType', '')),
            'CreditNoteNumber': str(item.get('CreditNoteNumber', '')),
            'InvoiceNumber': str(item.get('InvoiceNumber', '')),
            'PurchaseOrderNumber': str(item.get('PurchaseOrderNumber', '')),
            'Reference': str(item.get('Reference', '')),
            'LineAmountTypes': str(item.get('LineAmountTypes', '')),
            'Narration': str(item.get('Narration', '')),
            'SubTotal': str(item.get('SubTotal', '')),
            'TotalTax': str(item.get('TotalTax', '')),
            'Total': str(item.get('Total', '')),
            'ToBankAccount.Name': '',  # for bank transfers
            'CurrencyCode': str(item.get('CurrencyCode', '')),
            'CurrencyRate': str(item.get('CurrencyRate', '')),
            'Status': str(item.get('Status', '')),
            'FullyPaidOnDate': self._format_date(item.get('FullyPaidOnDate')),
            'UpdatedDateUTC': self._format_date(item.get('UpdatedDateUTC')),
            'IsSupplier': str(item.get('IsSupplier', '')),
            'IsCustomer': str(item.get('IsCustomer', '')),
            'Schedule.StartDate': self._format_date(
                item.get('Schedule', {}).get('StartDate') if item.get('Schedule') else None
            ),
            'HasAttachments': str(item.get('HasAttachments', False)),
            'AttachmentFolder': '',  # populated separately if needed
            'AttachmentFilenames': '',  # populated separately if needed
            # entity IDs
            'AccountID': str(item.get('AccountID', '')),
            'ContactID': str(contact.get('ContactID', '')),
            'BankTransactionID': str(item.get('BankTransactionID', '')),
            'BankTransferID': str(item.get('BankTransferID', '')),
            'CreditNoteID': str(item.get('CreditNoteID', '')),
            'InvoiceID': str(item.get('InvoiceID', '')),
            'ManualJournalID': str(item.get('ManualJournalID', '')),
            'PurchaseOrderID': str(item.get('PurchaseOrderID', '')),
            'QuoteID': str(item.get('QuoteID', '')),
            'RepeatingInvoiceID': str(item.get('RepeatingInvoiceID', '')),
        }

        return row

    def _add_line_item_fields(
        self, row: dict[str, str], line_item: dict[str, Any]
    ) -> dict[str, str]:
        """Add line item specific fields to a row."""
        row = row.copy()
        tracking_name, tracking_option = self._format_tracking(line_item.get('Tracking'))

        row.update(
            {
                'LineItem.AccountCode': str(line_item.get('AccountCode', '')),
                'LineItem.AccountName': str(line_item.get('AccountName', '')),
                'LineItem.Description': str(line_item.get('Description', '')),
                'LineItem.Quantity': str(line_item.get('Quantity', '')),
                'LineItem.UnitAmount': str(line_item.get('UnitAmount', '')),
                'LineItem.DiscountRate': str(line_item.get('DiscountRate', '')),
                'LineItem.DiscountAmount': str(line_item.get('DiscountAmount', '')),
                'LineItem.LineAmount': str(line_item.get('LineAmount', '')),
                'LineItem.TaxType': str(line_item.get('TaxType', '')),
                'LineItem.TaxAmount': str(line_item.get('TaxAmount', '')),
                'LineItem.Tracking.Name': tracking_name,
                'LineItem.Tracking.Option': tracking_option,
            }
        )
        return row

    def write_item(self, item: dict[str, Any]) -> None:
        """
        Write an item to CSV.

        If item has LineItems, creates one row per line item.
        Otherwise creates a single row.
        """
        base_row = self._get_base_row(item)

        line_items = item.get('LineItems') or item.get('LineItem')
        if line_items and isinstance(line_items, list) and len(line_items) > 0:
            # denormalize: one row per line item
            for line_item in line_items:
                row = self._add_line_item_fields(base_row, line_item)
                self.writer.writerow(row)
        else:
            # no line items, write single row
            self.writer.writerow(base_row)

    def close(self) -> None:
        """Close the CSV file."""
        self.file.close()
        logging.info(f'closed CSV file: {self.output_path}')

    def __enter__(self) -> 'TransactionCSVWriter':
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()
