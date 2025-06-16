import json
from pathlib import Path
from typing import Iterator, Any, Iterable

ALL_JOURNAL_KEYS = [
    'JournalID',
    'JournalDate',
    'JournalNumber',
    'CreatedDateUTC',
    'JournalLineID',
    'AccountID',
    'AccountCode',
    'AccountType',
    'AccountName',
    'Description',
    'NetAmount',
    'GrossAmount',
    'TaxAmount',
    'TaxType',
    'TaxName',
    'TrackingCategories',
    'Reference',
    'SourceType',
    'SourceID',
]


def flatten(rows: Iterator[dict[str, Any]]) -> Iterator[dict[str, Any]]:
    for journal in rows:
        journal_lines = journal.pop('JournalLines', [])
        for journal_line in journal_lines:
            full_journal_row = journal.copy()
            for key, value in journal_line.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                full_journal_row[key] = value
            yield full_journal_row


def load_transactions(paths: Iterable[Path]) -> dict[str, dict[str, Any]]:
    transactions: dict[str, dict[str, Any]] = {}
    for path in paths:
        with path.open() as source:
            for line in source:
                row = json.loads(line)
                transactions[row['BankTransactionID']] = row
    return transactions
