"""Stage export writes so API failures cannot leave data ahead of its checkpoint."""

from contextlib import contextmanager
from pathlib import Path
from shutil import copy2, copymode, rmtree
from tempfile import mkdtemp
from typing import Iterator


class ExportTransaction:
    def __init__(self, destination: Path, directory: Path) -> None:
        self.destination = destination
        self.directory = directory
        self.paths: dict[Path, Path] = {}
        self.recovery_required = False

    def path(self, relative: Path, append: bool = False) -> Path:
        target = self.destination / relative
        if (
            relative.is_absolute()
            or '..' in relative.parts
            or target.is_symlink()
            or not target.resolve().is_relative_to(self.destination.resolve())
        ):
            raise ValueError('Export paths must stay within the destination without file symlinks')
        if relative not in self.paths:
            staged = self.directory / 'staged' / relative
            staged.parent.mkdir(parents=True, exist_ok=True)
            if append and target.exists():
                copy2(target, staged)
            self.paths[relative] = staged
        return self.paths[relative]

    def commit(self) -> None:
        # Checkpoints are published after all their data files.
        ordered = sorted(self.paths, key=lambda path: path.name == 'latest.json')
        originals: dict[Path, Path | None] = {}
        for relative in ordered:
            target = self.destination / relative
            backup = None
            if target.exists():
                backup = self.directory / 'previous' / relative
                backup.parent.mkdir(parents=True, exist_ok=True)
                copy2(target, backup)
                copymode(target, self.paths[relative])
            originals[relative] = backup
        published = []
        try:
            for relative in ordered:
                target = self.destination / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                self.paths[relative].replace(target)
                published.append(relative)
        except BaseException as error:
            try:
                for relative in reversed(published):
                    target = self.destination / relative
                    backup = originals[relative]
                    if backup is None:
                        target.unlink()
                    else:
                        backup.replace(target)
            except BaseException as rollback_error:
                self.recovery_required = True
                rollback_error.add_note(f'Export recovery files retained at {self.directory}')
                raise rollback_error from error
            raise


@contextmanager
def staged_export(destination: Path) -> Iterator[ExportTransaction]:
    """Publish only a successful export; restore prior files on caught publication errors.

    This requires exclusive access to the destination. It is not a crash-atomic
    transaction across files. Failed rollback keeps the private recovery directory.
    """
    destination.mkdir(parents=True, exist_ok=True)
    directory = Path(mkdtemp(prefix='.xerotrust-', dir=destination))
    transaction = ExportTransaction(destination, directory)
    try:
        yield transaction
        transaction.commit()
    finally:
        if not transaction.recovery_required:
            rmtree(directory)
