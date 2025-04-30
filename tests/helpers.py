from dataclasses import dataclass
from pathlib import Path

from testfixtures import compare


@dataclass
class FileChecker:
    tmp_path: Path

    def __call__(self, expected: dict[str, str]) -> None:
        actual_files = {}
        for path in self.tmp_path.rglob('*'):
            if path.is_file():
                relative_path = str(path.relative_to(self.tmp_path))
                actual_files[relative_path] = path.read_text()
        compare(expected=expected, actual=actual_files)
