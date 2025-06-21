from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any, Protocol, Hashable, Iterable

from dateutil.parser import parse


@dataclass
class AccountTotal:
    name: str
    type: str
    code: str | None
    total: Decimal = Decimal(0)


@dataclass
class AccountChange:
    name: str
    type: str
    code: str | None
    amount: Decimal


class AccountTotals(dict[str, AccountTotal]):
    def add(self, change: AccountChange) -> None:
        key = change.code or change.name
        if key not in self:
            self[key] = AccountTotal(
                name=change.name,
                type=change.type,
                code=change.code,
            )
        account_total = self[key]
        assert account_total.name == change.name
        assert account_total.type == change.type
        assert account_total.code == change.code
        account_total.total += change.amount

    def get(self, key: str) -> AccountTotal:  # type: ignore[override]
        item = super().get(key)
        if item is None:
            item = AccountTotal("", "", None)
        return item


class Reconciler(Protocol):
    """Protocol for reconciler implementations."""

    date_key: str

    @classmethod
    def date(cls, item: dict[str, Any]) -> date:
        return parse(item[cls.date_key]).date()

    @staticmethod
    def parse(item: dict[str, Any]) -> Iterable[AccountChange]:
        """Parse items and add them into account totals."""
        ...


class JournalReconciler(Reconciler):
    """Reconciler for journal data."""

    date_key = "JournalDate"

    @staticmethod
    def parse(item: dict[str, Any]) -> Iterable[AccountChange]:
        lines = item["JournalLines"]
        types = set(line["AccountType"] for line in lines)
        if 'CURRLIAB' not in types:
            for line in lines:
                yield AccountChange(
                    line["AccountName"],
                    line["AccountType"],
                    line.get("AccountCode"),
                    line["GrossAmount"],
                )


class TransactionReconciler(Reconciler):
    """Reconciler for transaction data."""

    date_key = "Date"

    @staticmethod
    def parse(item: dict[str, Any]) -> Iterable[AccountChange]:
        transaction = item
        if transaction["Status"] != "DELETED":
            total = transaction["Total"]
            # Seen SPEND and SPEND-TRANSFER in the wild, ensure there's test coverage.
            if transaction["Type"].startswith("SPEND"):
                total = -total
            yield AccountChange(
                transaction["BankAccount"]["Name"],
                "BANK",
                None,
                total,
            )

            for line in transaction["LineItems"]:
                code = line.get("AccountCode")
                amount = line["LineAmount"]
                if code is not None:
                    if transaction["Type"] == "RECEIVE":
                        amount = -amount
                    yield AccountChange(
                        "",
                        "",
                        code.lower(),
                        amount,
                    )


RECONCILERS: dict[str, Reconciler] = {
    "journals": JournalReconciler,
    "transactions": TransactionReconciler,
}
