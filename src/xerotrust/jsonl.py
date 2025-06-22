import json
from decimal import Decimal
from pathlib import Path
from typing import Iterable, Any


def jsonl_stream(paths_or_globs: Iterable[Path | str]) -> Iterable[dict[str, Any]]:
    paths: Iterable[Path]
    for path_or_glob in paths_or_globs:
        if isinstance(path_or_glob, Path):
            paths = [path_or_glob]
        else:
            glob_path = Path(path_or_glob)
            if glob_path.is_absolute():
                paths = glob_path.parent.glob(glob_path.name)
            else:
                paths = Path().glob(path_or_glob)
        for path in sorted(paths):
            with path.open() as source:
                for line in source:
                    yield json.loads(line, parse_float=Decimal)
