from collections import defaultdict
from typing import Iterable, Any


def _journal_totals(
    journals: Iterable[dict[str, Any]],
) -> tuple[dict[str, float], dict[str, float]]:
    net_totals: dict[str, float] = defaultdict(float)
    gross_totals: dict[str, float] = defaultdict(float)
    for journal in journals:
        for line in journal.get("JournalLines", []):
            account = line.get("AccountName")
            if account is None:
                continue
            net = line.get("NetAmount", 0)
            gross = line.get("GrossAmount", 0)
            net_totals[account] += float(net)
            gross_totals[account] += float(gross)
    return dict(net_totals), dict(gross_totals)


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
    journal_net_totals, journal_gross_totals = _journal_totals(journals)
    transaction_totals = _transaction_totals(transactions)

    mismatches = []
    all_accounts = set(journal_net_totals) | set(journal_gross_totals) | set(transaction_totals)
    for account in sorted(all_accounts):
        j_net = journal_net_totals.get(account, 0.0)
        j_gross = journal_gross_totals.get(account, 0.0)
        t_total = transaction_totals.get(account, 0.0)
        print(f"{account}: net {j_net} -> {t_total}, gross {j_gross} -> {t_total}")
        if j_net != t_total:
            mismatches.append(ValueError(f"net {account}: {j_net} != {t_total}"))
        if j_gross != t_total:
            mismatches.append(ValueError(f"gross {account}: {j_gross} != {t_total}"))

    if mismatches:
        raise ExceptionGroup("Reconciliation errors", mismatches)


RECONCILERS = {"journals-transactions": reconcile_journals_transactions}
