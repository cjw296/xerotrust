import json
from datetime import datetime, timezone, date
from pprint import pformat
from typing import Any, Callable, TypeAlias, Sequence, Iterable

Transformer: TypeAlias = Callable[[Any], Any]

def itemgetter(key: str, default: Any = None) -> Callable[[dict[str, Any]], Any]:
    def getter(obj: dict[str, Any]) -> Any:
        return obj.get(key, default)

    return getter


TRANSFORMERS: dict[str, Callable[[Any], Any]] = {
    'json': json.dumps,
    'tenant': itemgetter('tenantName'),
    'pretty': pformat,
}


def show(
    items: Iterable[dict[str, Any]], transforms: Sequence[str], fields: Sequence[str], newline: bool
) -> Any:
    if not (transforms or fields):
        transforms = ('json',)
    transformers = [TRANSFORMERS[t] for t in transforms]
    transformers.extend(itemgetter(f) for f in fields)
    sep = '\n' if newline else ' '
    for item in items:
        print(*(t(item) for t in transformers), sep=sep)
