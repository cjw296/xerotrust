from pathlib import Path
from unittest.mock import patch

import pytest
from testfixtures import compare

from xerotrust.export import FileManager
from xerotrust.staging import staged_export

from .helpers import FileChecker


def test_append_overwrite_and_file_eviction(tmp_path: Path, check_files: FileChecker) -> None:
    (tmp_path / 'a').write_text('original\n')
    (tmp_path / 'a').chmod(0o600)
    (tmp_path / 'b').write_text('replaced\n')
    (tmp_path / 'b').chmod(0o600)
    with staged_export(tmp_path) as transaction, FileManager(max_open_files=1) as files:
        files.write({'a': 1}, transaction.path(Path('a'), append=True), append=True)
        files.write({'b': 2}, transaction.path(Path('b')))
        files.write({'a': 3}, transaction.path(Path('a'), append=True), append=True)
        compare(actual=(tmp_path / 'a').read_text(), expected='original\n')
        compare(actual=(tmp_path / 'b').read_text(), expected='replaced\n')
    check_files({'a': "original\n{'a': 1}\n{'a': 3}\n", 'b': "{'b': 2}\n"})
    compare(actual=(tmp_path / 'a').stat().st_mode & 0o777, expected=0o600)
    compare(actual=(tmp_path / 'b').stat().st_mode & 0o777, expected=0o600)


@pytest.mark.parametrize('failure_index', [0, 1, 2])
def test_publication_failure_restores_files_and_checkpoint(
    tmp_path: Path, check_files: FileChecker, failure_index: int
) -> None:
    (tmp_path / 'a').write_text('original')
    (tmp_path / 'latest.json').write_text('old checkpoint')
    original_replace = Path.replace
    calls = []

    def replace(path: Path, target: Path) -> Path:
        if 'staged' in path.parts:
            calls.append(path.name)
            if len(calls) == failure_index + 1:
                raise OSError('publication failed')
        return original_replace(path, target)

    with (
        patch.object(Path, 'replace', replace),
        pytest.raises(OSError, match='^publication failed$'),
    ):
        with staged_export(tmp_path) as transaction:
            # Deliberately prepare the checkpoint first; publication must still write it last.
            transaction.path(Path('latest.json')).write_text('new checkpoint')
            transaction.path(Path('a')).write_text('replacement')
            transaction.path(Path('b')).write_text('new file')
    compare(actual=calls, expected=['a', 'b', 'latest.json'][: failure_index + 1])
    check_files({'a': 'original', 'latest.json': 'old checkpoint'})
    assert not list(tmp_path.glob('.xerotrust-*'))


def test_backup_failure_leaves_destination_unchanged(
    tmp_path: Path, check_files: FileChecker
) -> None:
    (tmp_path / 'a').write_text('original')
    with patch('xerotrust.staging.copy2', side_effect=OSError('backup failed')):
        with pytest.raises(OSError, match='^backup failed$'):
            with staged_export(tmp_path) as transaction:
                transaction.path(Path('a')).write_text('replacement')
    check_files({'a': 'original'})
    assert not list(tmp_path.glob('.xerotrust-*'))


def test_failed_rollback_keeps_recovery_files(tmp_path: Path) -> None:
    (tmp_path / 'a').write_text('original')
    (tmp_path / 'latest.json').write_text('old checkpoint')
    original_replace = Path.replace

    def replace(path: Path, target: Path) -> Path:
        if path.name == 'latest.json':
            raise OSError('publication failed')
        if 'previous' in path.parts:
            raise OSError('rollback failed')
        return original_replace(path, target)

    with (
        patch.object(Path, 'replace', replace),
        pytest.raises(OSError) as error,
    ):
        with staged_export(tmp_path) as transaction:
            transaction.path(Path('a')).write_text('replacement')
            transaction.path(Path('latest.json')).write_text('new checkpoint')
    compare(
        actual=str(error.value),
        expected='rollback failed',
    )
    compare(
        actual=error.value.__notes__,
        expected=[f'Export recovery files retained at {transaction.directory}'],
    )
    compare(actual=(transaction.directory / 'previous/a').read_text(), expected='original')
    compare(actual=(tmp_path / 'latest.json').read_text(), expected='old checkpoint')
    compare(actual=transaction.directory.stat().st_mode & 0o777, expected=0o700)


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
    with pytest.raises(ValueError) as error:
        with staged_export(destination) as transaction:
            transaction.path(relative)
    compare(
        actual=str(error.value),
        expected='Export paths must stay within the destination without file symlinks',
    )
    compare(actual=(outside / 'data').read_text(), expected='preserved')
