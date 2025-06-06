import logging
from pathlib import Path
from typing import Iterator
from unittest.mock import Mock

import pytest
from testfixtures import Replacer

from xerotrust import main
from xerotrust.authentication import credentials_from_file
from xerotrust.transform import show

from .helpers import run_cli


class TestLogLevel:
    @pytest.fixture(autouse=True)
    def mocks(self) -> Iterator[Mock]:
        mocks_ = Mock()
        mocks_.basicConfig = Mock(spec=logging.basicConfig)
        mocks_.credentials_from_file = Mock(spec=credentials_from_file)
        mocks_.show = Mock(spec=show)
        with Replacer() as replace:
            replace.in_module(logging.basicConfig, mocks_.basicConfig)
            replace.in_module(credentials_from_file, mocks_.credentials_from_file, module=main)
            replace.in_module(show, mocks_.show, module=main)
            yield mocks_

    def test_log_level_option(self, tmp_path: Path, mocks: Mock) -> None:
        run_cli(tmp_path, "--log-level", "DEBUG", "tenants")
        mocks.basicConfig.assert_called_once_with(level=logging.DEBUG)

    def test_log_level_shorthand(self, tmp_path: Path, mocks: Mock) -> None:
        run_cli(tmp_path, "-l", "WARNING", "tenants")
        mocks.basicConfig.assert_called_once_with(level=logging.WARNING)

