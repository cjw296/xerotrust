from pathlib import Path
from typing import Iterator
from unittest.mock import Mock

import pytest
from testfixtures import replace_in_module

from xerotrust import main
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
