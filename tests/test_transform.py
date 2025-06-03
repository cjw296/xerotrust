from testfixtures import ShouldRaise

from xerotrust.transform import TRANSFORMERS


def test_json_with_unsupported_type() -> None:
    with ShouldRaise(TypeError("Unexpected type: <class 'type'>, <class 'object'>")):
        TRANSFORMERS['json'](object)
