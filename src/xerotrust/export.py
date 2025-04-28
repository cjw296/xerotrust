import json
from collections import OrderedDict
from pathlib import Path
from typing import Callable, Dict, Any, IO, Self, TypeAlias, Iterable
Serializer: TypeAlias = Callable[[dict[str, Any]], str]


class FileManager:
    """
    Manages writing lines to files based on their path.
    Keeps a pool of files open for efficient writing.
    """

    def __init__(self, max_open_files: int = 10, serializer: Serializer = str) -> None:
        self.max_open_files = max_open_files
        self.serializer = serializer
        self._open_files: "OrderedDict[Path, IO[str]]" = OrderedDict()

    def write(self, item: dict[str, Any], path: Path) -> None:
        if path not in self._open_files:
            if len(self._open_files) >= self.max_open_files:
                oldest_path, oldest_file = self._open_files.popitem(last=False)
                oldest_file.close()
            path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
            self._open_files[path] = path.open('a', encoding='utf-8')
        else:
            self._open_files.move_to_end(path)

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
