import json
import logging
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from time import sleep
from typing import Callable, Any, IO, Self, TypeAlias, Iterable, ClassVar, cast

from xero.exceptions import XeroRateLimitExceeded

from xerotrust.transform import DateTimeEncoder

Serializer: TypeAlias = Callable[[dict[str, Any]], str]


class Split(StrEnum):
    NONE = 'none'
    YEARS = 'years'
    MONTHS = 'months'
    DAYS = 'days'


SplitSuffix = {
    Split.NONE: '',
    Split.YEARS: '-%Y',
    Split.MONTHS: '-%Y-%m',
    Split.DAYS: '-%Y-%m-%d',
}


class FileManager:
    """
    Manages writing lines to files based on their path.
    Keeps a pool of files open for efficient writing.
    """

    def __init__(self, max_open_files: int = 10, serializer: Serializer = str) -> None:
        self.max_open_files = max_open_files
        self.serializer = serializer
        self._open_files: "OrderedDict[Path, IO[str]]" = OrderedDict()
        self._seen_paths: set[Path] = set()

    def write(self, item: dict[str, Any], path: Path, append: bool = False) -> None:
        if path not in self._open_files:
            logging.info(f'opening {path}')
            if len(self._open_files) >= self.max_open_files:
                oldest_path, oldest_file = self._open_files.popitem(last=False)
                oldest_file.close()
            path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
            mode = 'a' if append or path in self._seen_paths else 'w'
            self._open_files[path] = path.open(mode, encoding='utf-8')
        else:
            self._open_files.move_to_end(path)
        self._seen_paths.add(path)
        print(self.serializer(item), file=self._open_files[path])

    def close(self) -> None:
        """Close all open files."""
        for f in self._open_files.values():
            f.close()
        self._open_files.clear()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any | None,
    ) -> None:
        self.close()


class LatestData(dict[str, dict[str, datetime | int] | None]):
    @classmethod
    def load(cls, path: Path) -> Self:
        instance = cls()
        if path.exists():
            for endpoint, data in json.loads(path.read_text()).items():
                if data:
                    for key in data:
                        if 'Date' in key:
                            data[key] = datetime.fromisoformat(data[key])
                instance[endpoint] = data
        return instance

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self, cls=DateTimeEncoder, indent=2))


Namer: TypeAlias = Callable[[dict[str, Any]], str]


def retry_on_rate_limit[T, **P](
    manager_method: Callable[P, T], *args: P.args, **kwargs: P.kwargs
) -> T:
    while True:
        try:
            return manager_method(*args, **kwargs)
        except XeroRateLimitExceeded as e:
            seconds = int(e.response.headers['retry-after'])
            logging.warning(f'Rate limit exceeded, waiting {seconds} seconds')
            sleep(seconds)


@dataclass
class Export:
    latest_fields: ClassVar[tuple[str, ...]] = 'CreatedDateUTC', 'UpdatedDateUTC'
    supports_update: ClassVar[bool] = False

    file_name: str | None = None
    latest: dict[str, int | datetime] | None = None

    def name(self, item: dict[str, Any], split: Split) -> str:
        assert self.file_name is not None
        return self.file_name

    def _raw_items(
        self, manager: Any, latest: dict[str, int | datetime] | None
    ) -> Iterable[dict[str, Any]]:
        return retry_on_rate_limit(manager.all)

    def items(
        self, manager: Any, latest: dict[str, int | datetime] | None
    ) -> Iterable[dict[str, Any]]:
        self.latest = latest
        for item in self._raw_items(manager, latest):
            if self.latest is None:
                self.latest = {}
                for f in self.latest_fields:
                    latest_value = item.get(f)
                    if latest_value is not None:
                        self.latest[f] = latest_value
            else:
                for latest_field in self.latest_fields:
                    latest_value = item.get(latest_field)
                    if latest_value is not None:
                        self.latest[latest_field] = max(latest_value, self.latest[latest_field])
            yield item


@dataclass
class StaticExport(Export):
    """Export class for endpoints that don't support incremental updates."""

    latest_fields: ClassVar[tuple[str, ...]] = ()
    supports_update: ClassVar[bool] = False


@dataclass
class JournalsExport(Export):
    latest_fields: ClassVar[tuple[str, ...]] = ('JournalDate', 'JournalNumber')
    supports_update: ClassVar[bool] = True

    def name(self, item: dict[str, Any], split: Split) -> str:
        pattern = f'journals{SplitSuffix[split]}.jsonl'
        return item['JournalDate'].strftime(pattern)  # type: ignore[no-any-return]

    def _raw_items(
        self, manager: Any, latest: dict[str, int | datetime] | None
    ) -> Iterable[dict[str, Any]]:
        offset = 0 if latest is None else latest.get('JournalNumber', 0)
        while entries := retry_on_rate_limit(manager.filter, offset=offset):
            yield from entries
            offset = entries[-1]['JournalNumber']


@dataclass
class BankTransactionsExport(Export):
    latest_fields: ClassVar[tuple[str, ...]] = ('UpdatedDateUTC',)
    supports_update: ClassVar[bool] = True

    page_size: int = 1000

    def name(self, item: dict[str, Any], split: Split) -> str:
        pattern = f'transactions{SplitSuffix[split]}.jsonl'
        return item['Date'].strftime(pattern)  # type: ignore[no-any-return]

    def _raw_items(
        self, manager: Any, latest: dict[str, int | datetime] | None
    ) -> Iterable[dict[str, Any]]:
        page = 1
        while True:
            kwargs: dict[str, Any] = {'page': page, 'pageSize': self.page_size}
            if latest is not None:
                kwargs['since'] = cast(datetime, latest['UpdatedDateUTC'])
            entries = retry_on_rate_limit(manager.filter, **kwargs)
            if not entries:
                break
            yield from entries
            page += 1

    def items(
        self, manager: Any, latest: dict[str, int | datetime] | None
    ) -> Iterable[dict[str, Any]]:
        self.latest = latest
        original_latest = cast(datetime, latest['UpdatedDateUTC']) if latest is not None else None
        for item in self._raw_items(manager, latest):
            if original_latest is not None and item['UpdatedDateUTC'] <= original_latest:
                continue

            if self.latest is None:
                self.latest = {'UpdatedDateUTC': item['UpdatedDateUTC']}
            else:
                updated = item['UpdatedDateUTC']
                self.latest['UpdatedDateUTC'] = max(updated, self.latest['UpdatedDateUTC'])

            yield item


EXPORTS = {
    'Accounts': Export("accounts.jsonl"),
    'Contacts': Export("contacts.jsonl"),
    'Journals': JournalsExport(),
    'BankTransactions': BankTransactionsExport(),
    'BankTransfers': Export("banktransfers.jsonl"),
    'Invoices': Export("invoices.jsonl"),
    'CreditNotes': Export("creditnotes.jsonl"),
    'Currencies': StaticExport("currencies.jsonl"),
    'Employees': Export("employees.jsonl"),
    'Items': Export("items.jsonl"),
    'ManualJournals': Export("manualjournals.jsonl"),
    'Organisations': Export("organisations.jsonl"),
    'Overpayments': Export("overpayments.jsonl"),
    'Payments': Export("payments.jsonl"),
    'Prepayments': Export("prepayments.jsonl"),
    'PurchaseOrders': Export("purchaseorders.jsonl"),
    'RepeatingInvoices': StaticExport("repeatinginvoices.jsonl"),
    'TaxRates': StaticExport("taxrates.jsonl"),
    'TrackingCategories': StaticExport("trackingcategories.jsonl"),
    'Users': Export("users.jsonl"),
    'BrandingThemes': Export("brandingthemes.jsonl"),
    'ContactGroups': StaticExport("contactgroups.jsonl"),
    'Quotes': Export("quotes.jsonl"),
    'BatchPayments': Export("batchpayments.jsonl"),
}
