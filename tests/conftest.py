from functools import partial
from tempfile import mkdtemp
from pathlib import Path
from typing import Iterator
from unittest.mock import Mock

import pytest
from testfixtures import replace_in_module

from xerotrust import main, staging
from xerotrust.authentication import credentials_from_file

from .helpers import FileChecker, SAMPLE_CREDENTIALS


@pytest.fixture()
def check_files(tmp_path: Path) -> FileChecker:
    return FileChecker(tmp_path)


@pytest.fixture()
def mock_credentials_from_file() -> Iterator[Mock]:
    mock = Mock(spec=credentials_from_file)
    mock.return_value = SAMPLE_CREDENTIALS
    with replace_in_module(credentials_from_file, mock, module=main):
        yield mock


@pytest.fixture(autouse=True)
def staging_root(tmp_path_factory: pytest.TempPathFactory) -> Iterator[Path]:
    # Keep retained diagnostic output in pytest-managed storage, outside export roots.
    root = tmp_path_factory.mktemp('staging')
    with replace_in_module(mkdtemp, partial(mkdtemp, dir=root), module=staging):
        yield root
