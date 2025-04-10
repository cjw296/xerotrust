from testfixtures import compare

from xerotrust import hello


def test_hello() -> None:
    compare(hello(), expected='Hello from xerotrust!')
