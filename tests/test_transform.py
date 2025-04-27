from datetime import date

from testfixtures import ShouldAssert

from xerotrust.transform import TRANSFORMERS


def test_json_with_unsupported_type() -> None:
    with ShouldAssert("Unexpected type: <class 'datetime.date'>, datetime.date(2021, 1, 1)"):
        TRANSFORMERS['json'](date(2021, 1, 1))
