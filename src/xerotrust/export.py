import json
import logging
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from time import sleep
from typing import Callable, Any, IO, Self, TypeAlias, Iterable, Iterator, ClassVar

from xero.exceptions import XeroRateLimitExceeded

from xerotrust.transform import DateTimeEncoder

Serializer: TypeAlias = Callable[[dict[str, Any]], str]


def normalize_datetime(dt: datetime) -> datetime:
    """Normalize datetime to be timezone-aware in UTC for consistent comparisons."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


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
    latest_fields: ClassVar[tuple[str, ...]] = ('UpdatedDateUTC',)
    supports_update: ClassVar[bool] = False

    file_name: str | None = None
    latest: dict[str, int | datetime] | None = None

    def name(self, item: dict[str, Any], split: Split) -> str:
        assert self.file_name is not None
        return self.file_name

    def _raw_items(
        self, manager: Any, latest: dict[str, int | datetime] | None
    ) -> Iterable[dict[str, Any]]:
        return manager.all()  # type: ignore[no-any-return]

    def items(
        self, manager: Any, latest: dict[str, int | datetime] | None
    ) -> Iterable[dict[str, Any]]:
        self.latest = latest
        for item in self._raw_items(manager, latest):
            if self.latest is None:
                self.latest = {f: item[f] for f in self.latest_fields}
            else:
                for latest_field in self.latest_fields:
                    latest_value = item[latest_field]
                    if isinstance(latest_value, datetime):
                        latest_value = normalize_datetime(latest_value)
                        existing_value = self.latest[latest_field]
                        if isinstance(existing_value, datetime):
                            existing_value = normalize_datetime(existing_value)
                            self.latest[latest_field] = max(latest_value, existing_value)
                        else:
                            self.latest[latest_field] = latest_value
                    else:
                        self.latest[latest_field] = max(latest_value, self.latest[latest_field])
            yield item


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


class LatestData(dict[str, dict[str, datetime | int] | None]):
    @classmethod
    def load(cls, path: Path) -> Self:
        instance = cls()
        if path.exists():
            for endpoint, data in json.loads(path.read_text()).items():
                for key in data:
                    if 'Date' in key:
                        # Normalize to timezone-aware datetime in UTC for consistent comparisons
                        dt = datetime.fromisoformat(data[key])
                        data[key] = normalize_datetime(dt)
                instance[endpoint] = data
        return instance

    def save(self, path: Path) -> None:
        path.write_text(json.dumps(self, cls=DateTimeEncoder, indent=2))


EXPORTS = {
    'Accounts': Export("accounts.jsonl"),
    'Contacts': Export("contacts.jsonl"),
    'Journals': JournalsExport(),
}

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
