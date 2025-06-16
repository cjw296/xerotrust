import json
from typing import Any, Iterable

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


def flatten(rows: Iterable[dict[str, Any]]) -> Iterable[dict[str, Any]]:
    for journal in rows:
        journal_lines = journal.pop('JournalLines', [])
        for journal_line in journal_lines:
            full_journal_row = journal.copy()
            for key, value in journal_line.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                full_journal_row[key] = value
            yield full_journal_row
