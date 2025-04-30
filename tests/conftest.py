from pathlib import Path

import pytest

from .helpers import FileChecker


@pytest.fixture()
def check_files(tmp_path: Path) -> FileChecker:
    return FileChecker(tmp_path)
