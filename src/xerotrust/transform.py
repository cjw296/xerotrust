import json
from datetime import datetime, timezone
from functools import partial
from pprint import pformat
from typing import Any, Callable, TypeAlias, Sequence, Iterable

Transformer: TypeAlias = Callable[[Any], Any]


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj: Any) -> Any:
        assert isinstance(obj, datetime), f'Unexpected type: {type(obj)}, {obj!r}'
        return obj.astimezone(timezone.utc).isoformat()


def itemgetter(key: str, default: Any = None) -> Callable[[dict[str, Any]], Any]:
    def getter(obj: dict[str, Any]) -> Any:
        return obj.get(key, default)

    return getter


TRANSFORMERS: dict[str, Transformer] = {
    'json': partial(json.dumps, cls=DateTimeEncoder),
    'pretty': pformat,
}


def show(
    items: Iterable[dict[str, Any]], transforms: Sequence[str], fields: Sequence[str], newline: bool
) -> Any:
    if not (transforms or fields):
        transforms = ('json',)
    transformers = [itemgetter(f) for f in fields] + [TRANSFORMERS[t] for t in transforms]
    sep = '\n' if newline else ' '
    for item in items:
        print(*(t(item) for t in transformers), sep=sep)
