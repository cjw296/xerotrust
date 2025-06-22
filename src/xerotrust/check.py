from typing import Iterable, Any, Sequence


def minimal_repr(seq: Sequence[int]) -> str:
    ranges: list[list[int]] = []
    for n in sorted(set(seq)):
        if not ranges or n != ranges[-1][1] + 1:
            ranges.append([n, n])
        else:
            ranges[-1][1] = n
    return ", ".join(f"{a}-{b}" if a != b else str(a) for a, b in ranges)


def check_journals(journals: Iterable[dict[str, Any]]) -> Iterable[dict[str, Any]]:
    seen_ids = set()
    seen_numbers = set()
    journal_numbers = []

    errors = []

    for journal in journals:
        jid = journal.get("JournalID")
        jnum = journal.get("JournalNumber")

        if jid in seen_ids:
            errors.append(ValueError(f"Duplicate JournalID found: {jid}"))
        elif jid is not None:
            seen_ids.add(jid)

        if jnum in seen_numbers:
            errors.append(ValueError(f"Duplicate JournalNumber found: {jnum}"))
        elif jnum is not None:
            seen_numbers.add(jnum)
            journal_numbers.append(jnum)
        yield journal

    # Filter out None before processing numbers for gaps
    valid_journal_numbers = [num for num in journal_numbers if isinstance(num, int)]

    if valid_journal_numbers:
        journal_numbers_sorted = sorted(valid_journal_numbers)
        # Check for gaps only if we have a valid range
        if journal_numbers_sorted:
            expected_sequence = list(
                range(journal_numbers_sorted[0], journal_numbers_sorted[-1] + 1)
            )
            if journal_numbers_sorted != expected_sequence:
                missing_set = set(expected_sequence) - set(journal_numbers_sorted)
                # minimal_repr expects a Sequence[int]
                missing_list = sorted(list(missing_set))
                errors.append(ValueError(f"Missing JournalNumbers: {minimal_repr(missing_list)}"))

    if errors:
        # Ensure consistent order for testing
        errors.sort(key=lambda e: str(e))
        raise ExceptionGroup("Journal validation errors", errors)


def show_summary(journals: Iterable[dict[str, Any]]) -> Iterable[dict[str, Any]]:
    fields = 'JournalNumber', 'JournalDate', 'CreatedDateUTC'
    count = 0
    data = {field: {"min": None, "max": None} for field in fields}

    for count, journal in enumerate(journals, start=1):
        for field in fields:
            value = journal.get(field)
            current_min = data[field]["min"]
            current_max = data[field]["max"]

            # Check for None before comparison
            if value is not None:
                if current_min is None or value < current_min:
                    data[field]["min"] = value
                if current_max is None or value > current_max:
                    data[field]["max"] = value
        yield journal

    padding = max(len(field) for field in fields)
    print(f"{'entries':>{padding}}: {count}")
    for field in fields:
        min_value = data[field]["min"]
        max_value = data[field]["max"]
        print(f"{field:>{padding}}: {min_value} -> {max_value}")


def check_transactions(transactions: Iterable[dict[str, Any]]) -> Iterable[dict[str, Any]]:
    seen_ids = set()
    errors = []

    for transaction in transactions:
        transaction_id = transaction.get("BankTransactionID")

        if transaction_id in seen_ids:
            errors.append(ValueError(f"Duplicate BankTransactionID found: {transaction_id}"))
        elif transaction_id is not None:
            seen_ids.add(transaction_id)

        yield transaction

    if errors:
        # Ensure consistent order for testing
        errors.sort(key=lambda e: str(e))
        raise ExceptionGroup("Transaction validation errors", errors)


def show_transactions_summary(transactions: Iterable[dict[str, Any]]) -> Iterable[dict[str, Any]]:
    count = 0
    min_date = None
    max_date = None

    for transaction in transactions:
        count += 1
        date_value = transaction.get("Date")

        if date_value is not None:
            if min_date is None or date_value < min_date:
                min_date = date_value
            if max_date is None or date_value > max_date:
                max_date = date_value

        yield transaction

    print(f"transactions: {count}")
    print(f"        Date: {min_date} -> {max_date}")


CHECKERS = {
    'journals': (check_journals, show_summary),
    'transactions': (check_transactions, show_transactions_summary),
}
