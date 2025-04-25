import json
from datetime import datetime, timezone, date
from pprint import pformat
from typing import Any, Callable


def itemgetter(key: str, default: Any = None) -> Callable[[dict[str, Any]], Any]:
    def getter(obj: dict[str, Any]) -> Any:
        return obj.get(key, default)

    return getter


TRANSFORMERS: dict[str, Callable[[Any], Any]] = {
    'json': json.dumps,
    'tenant': itemgetter('tenantName'),
    'pretty': pformat,
}
