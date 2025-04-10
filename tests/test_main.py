import pytest
from click.testing import CliRunner
from pathlib import Path

from xerotrust.main import cli

# TODO: Remove this once tests are implemented
pytestmark = pytest.mark.skip(reason="Tests not yet implemented")


def test_login_default_config() -> None:
    """Test the login command with the default config path."""
    runner = CliRunner()
    result = runner.invoke(cli, ['login'])
    assert result.exit_code == 0
    assert "Login command called. Config path: .xerotrust.yml" in result.output


def test_login_custom_config(tmp_path: Path) -> None:
    """Test the login command with a custom config path."""
    config_file = tmp_path / "custom_config.yml"
    runner = CliRunner()
    result = runner.invoke(cli, ['--config', str(config_file), 'login'])
    assert result.exit_code == 0
    assert f"Login command called. Config path: {config_file}" in result.output


def test_dump_default_config() -> None:
    """Test the dump command with the default config path."""
    runner = CliRunner()
    result = runner.invoke(cli, ['dump'])
    assert result.exit_code == 0
    assert "Dump command called. Config path: .xerotrust.yml" in result.output


def test_dump_custom_config(tmp_path: Path) -> None:
    """Test the dump command with a custom config path."""
    config_file = tmp_path / "custom_config.yml"
    runner = CliRunner()
    result = runner.invoke(cli, ['--config', str(config_file), 'dump'])
    assert result.exit_code == 0
    assert f"Dump command called. Config path: {config_file}" in result.output
