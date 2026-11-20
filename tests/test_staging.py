from pathlib import Path
from shutil import copy2
from typing import Any

import pytest
from testfixtures import compare, replace_in_module, replace_on_class, ShouldRaise

from xerotrust.export import FileManager
from xerotrust import staging
from xerotrust.staging import staged_export

from .helpers import FileChecker, retained_notice


def assert_owner_only(path: Path, directory: bool = False) -> None:
    """Check that publication preserves private files and diagnostics stay private."""
    compare(actual=path.stat().st_mode & 0o777, expected=0o700 if directory else 0o600)


def test_append_overwrite_and_file_eviction(tmp_path: Path, check_files: FileChecker) -> None:
    (tmp_path / 'a').write_text('original\n')
    (tmp_path / 'a').chmod(0o600)
    (tmp_path / 'b').write_text('replaced\n')
    (tmp_path / 'b').chmod(0o600)
    with staged_export(tmp_path) as transaction, FileManager(max_open_files=1) as files:
        files.write({'a': 1}, transaction.path(Path('a'), append=True), append=True)
        files.write({'b': 2}, transaction.path(Path('b')))
        files.write({'a': 3}, transaction.path(Path('a'), append=True), append=True)
        check_files({'a': 'original\n', 'b': 'replaced\n'})
        assert_owner_only(transaction.directory, directory=True)
    check_files({'a': "original\n{'a': 1}\n{'a': 3}\n", 'b': "{'b': 2}\n"})
    assert_owner_only(tmp_path / 'a')
    assert_owner_only(tmp_path / 'b')
    assert not transaction.directory.exists()


@pytest.mark.parametrize('failure_index', [0, 1, 2])
def test_publication_failure_retains_complete_staged_output(
    tmp_path: Path,
    check_files: FileChecker,
    failure_index: int,
    staging_root: Path,
    capsys: Any,
) -> None:
    (tmp_path / 'a').write_text('original')
    (tmp_path / 'latest.json').write_text('old checkpoint')
    original_replace = Path.replace
    calls = []

    def replace(path: Path, target: Path) -> Path:
        calls.append(target.name)
        if len(calls) == failure_index + 1:
            raise OSError('publication failed')
        # Publication uses a sibling temporary file, not a cross-filesystem rename.
        compare(actual=path.parent, expected=target.parent)
        return original_replace(path, target)

    with replace_on_class(Path.replace, replace), ShouldRaise(OSError('publication failed')):
        with staged_export(tmp_path) as transaction:
            transaction.path(Path('latest.json')).write_text('new checkpoint')
            transaction.path(Path('a')).write_text('replacement')
            transaction.path(Path('b')).write_text('new file')
    compare(actual=calls, expected=['a', 'b', 'latest.json'][: failure_index + 1])
    expected = {
        'a': 'replacement' if failure_index else 'original',
        'latest.json': 'old checkpoint',
    }
    if failure_index == 2:
        expected['b'] = 'new file'
    check_files(expected)
    FileChecker(transaction.directory)(
        {'a': 'replacement', 'b': 'new file', 'latest.json': 'new checkpoint'}
    )
    assert_owner_only(transaction.directory, directory=True)
    compare(actual=capsys.readouterr().err, expected=retained_notice(staging_root))


def test_copy_failure_keeps_destination_and_diagnostics(
    tmp_path: Path, check_files: FileChecker, staging_root: Path, capsys: Any
) -> None:
    (tmp_path / 'a').write_text('original')

    def fail(source: Path, target: Path) -> None:
        target.write_text('partial copy')
        raise OSError('copy failed')

    with replace_in_module(copy2, fail, module=staging), ShouldRaise(OSError('copy failed')):
        with staged_export(tmp_path) as transaction:
            transaction.path(Path('a')).write_text('replacement')
    check_files({'a': 'original'})
    FileChecker(transaction.directory)({'a': 'replacement'})
    compare(actual=capsys.readouterr().err, expected=retained_notice(staging_root))


def test_api_failure_keeps_private_diagnostics(
    tmp_path: Path, check_files: FileChecker, staging_root: Path, capsys: Any
) -> None:
    failure = RuntimeError('API failed')
    with ShouldRaise(failure):
        with staged_export(tmp_path) as transaction:
            transaction.path(Path('data')).write_text('downloaded page')
            raise failure
    check_files({})
    FileChecker(transaction.directory)({'data': 'downloaded page'})
    assert_owner_only(transaction.directory, directory=True)
    compare(actual=capsys.readouterr().err, expected=retained_notice(staging_root))


@pytest.mark.parametrize('kind', ['absolute', 'parent', 'file_symlink', 'directory_symlink'])
def test_unsafe_export_paths_are_rejected(tmp_path: Path, kind: str) -> None:
    outside = tmp_path / 'outside'
    outside.mkdir()
    (outside / 'data').write_text('preserved')
    destination = tmp_path / 'export'
    destination.mkdir()
    if kind == 'absolute':
        relative = outside / 'data'
    elif kind == 'parent':
        relative = Path('../outside/data')
    elif kind == 'file_symlink':
        (destination / 'link').symlink_to(outside / 'data')
        relative = Path('link')
    else:
        (destination / 'link').symlink_to(outside, target_is_directory=True)
        relative = Path('link/data')
    with ShouldRaise(
        ValueError('Export paths must stay within the destination without file symlinks')
    ):
        with staged_export(destination) as transaction:
            transaction.path(relative)
    compare(actual=(outside / 'data').read_text(), expected='preserved')
