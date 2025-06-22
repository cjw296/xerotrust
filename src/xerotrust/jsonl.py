import json
from pathlib import Path
from typing import Iterable, Any


def jsonl_stream(paths_or_globs: Iterable[Path | str]) -> Iterable[dict[str, Any]]:
    for path_or_glob in paths_or_globs:
        paths = [path_or_glob] if isinstance(path_or_glob, Path) else Path().glob(path_or_glob)
        for path in paths:
            with path.open() as source:
                for line in source:
                    yield json.loads(line)
