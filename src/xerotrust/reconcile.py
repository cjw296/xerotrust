from collections import defaultdict
from decimal import Decimal
from typing import Any, Iterable

from rich.console import Console
from rich.table import Table


def _journal_totals(
    journals: Iterable[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    totals: dict[str, dict[str, Any]] = {}
    for journal in journals:
        for line in journal.get("JournalLines", []):
            account_name = line.get("AccountName")
            if account_name is None:
                continue
            account_code = line.get("AccountCode") or ""
            net = Decimal(str(line.get("NetAmount", 0)))
            gross = Decimal(str(line.get("GrossAmount", 0)))

            account_data = totals.setdefault(
                account_name,
                {"code": account_code, "net": Decimal(), "gross": Decimal()},
            )
            # Preserve the first code encountered
            if not account_data.get("code") and account_code:
                account_data["code"] = account_code
            account_data["net"] += net
            account_data["gross"] += gross
    return totals


def _transaction_totals(transactions: Iterable[dict[str, Any]]) -> dict[str, Decimal]:
    totals: dict[str, Decimal] = defaultdict(Decimal)
    for transaction in transactions:
        account = (transaction.get("BankAccount") or {}).get("Name")
        if account is None:
            continue
        amount = Decimal(str(transaction.get("Total", 0)))
        totals[account] += amount
    return totals


def reconcile_journals_transactions(
    journals: Iterable[dict[str, Any]], transactions: Iterable[dict[str, Any]]
) -> None:
    journal_totals = _journal_totals(journals)
    transaction_totals = _transaction_totals(transactions)

    all_accounts = set(journal_totals) | set(transaction_totals)

    table = Table(
        "AccountName",
        "AccountCode",
        "Gross",
        "Net",
        "Transaction",
        "Difference",
        box=None,
    )

    for account in sorted(all_accounts):
        j_data = journal_totals.get(account, {"code": "", "net": Decimal(), "gross": Decimal()})
        t_total = transaction_totals.get(account, Decimal())
        diff = t_total - j_data["net"]

        table.add_row(
            account,
            str(j_data.get("code", "")),
            str(j_data["gross"]),
            str(j_data["net"]),
            str(t_total),
            str(diff),
        )

    Console().print(table)


RECONCILERS = {"journals-transactions": reconcile_journals_transactions}
