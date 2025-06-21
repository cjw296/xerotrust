from collections import defaultdict
from typing import Iterable, Any


def _journal_totals(journals: Iterable[dict[str, Any]]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for journal in journals:
        for line in journal.get("JournalLines", []):
            account = line.get("AccountName")
            if account is None:
                continue
            amount = line.get("NetAmount", 0)
            totals[account] += float(amount)
    return dict(totals)


def _transaction_totals(transactions: Iterable[dict[str, Any]]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for transaction in transactions:
        account = (transaction.get("BankAccount") or {}).get("Name")
        if account is None:
            continue
        amount = transaction.get("Total", 0)
        totals[account] += float(amount)
    return dict(totals)


def reconcile_journals_transactions(
    journals: Iterable[dict[str, Any]], transactions: Iterable[dict[str, Any]]
) -> None:
    journal_totals = _journal_totals(journals)
    transaction_totals = _transaction_totals(transactions)

    mismatches = []
    for account in sorted(set(journal_totals) | set(transaction_totals)):
        j_total = journal_totals.get(account, 0.0)
        t_total = transaction_totals.get(account, 0.0)
        print(f"{account}: {j_total} -> {t_total}")
        if j_total != t_total:
            mismatches.append(ValueError(f"{account}: {j_total} != {t_total}"))

    if mismatches:
        raise ExceptionGroup("Reconciliation errors", mismatches)


RECONCILERS = {"journals-transactions": reconcile_journals_transactions}
