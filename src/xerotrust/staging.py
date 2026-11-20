"""Stage each endpoint so API failures cannot leave its data ahead of its checkpoint."""

from contextlib import contextmanager
from pathlib import Path
from shutil import copy2, copymode, rmtree
import sys
from tempfile import mkdtemp, NamedTemporaryFile
from typing import Iterator


class ExportTransaction:
    def __init__(self, destination: Path, directory: Path) -> None:
        self.destination = destination
        self.directory = directory
        self.paths: dict[Path, Path] = {}

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
            staged = self.directory / relative
            staged.parent.mkdir(parents=True, exist_ok=True)
            if append and target.exists():
                copy2(target, staged)
            self.paths[relative] = staged
        return self.paths[relative]

    def commit(self) -> None:
        # Keep the staged originals for diagnostics, including files already published.
        # Copy through the destination filesystem so each replacement is atomic even
        # when the system temporary directory is on another filesystem.
        for relative in sorted(self.paths, key=lambda path: path.name == 'latest.json'):
            target = self.destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with NamedTemporaryFile(dir=target.parent, prefix='.xerotrust-', delete=False) as file:
                temporary = Path(file.name)
            try:
                copy2(self.paths[relative], temporary)
                if target.exists():
                    copymode(target, temporary)
                temporary.replace(target)
            finally:
                temporary.unlink(missing_ok=True)


@contextmanager
def staged_export(destination: Path) -> Iterator[ExportTransaction]:
    """Publish a completed endpoint; keep failed exports in private system temp storage.

    Publication replaces files individually, with the checkpoint last. A publication
    failure may leave some files updated: inspect the retained output before rerunning.
    Exclusive destination access is required.
    """
    directory = Path(mkdtemp(prefix='xerotrust-'))
    transaction = ExportTransaction(destination, directory)
    try:
        yield transaction
        transaction.commit()
    except BaseException:
        print(f'Export incomplete; staged files retained at {directory}', file=sys.stderr)
        raise
    else:
        rmtree(directory)
