from testfixtures import compare

from xerotrust.check import minimal_repr


def test_minimal_repr() -> None:
    """Directly test the minimal_repr helper."""
    compare(minimal_repr([]), expected="")
    compare(minimal_repr([1]), expected="1")
    compare(minimal_repr([1, 2]), expected="1-2")
    compare(minimal_repr([1, 3]), expected="1, 3")
    compare(minimal_repr([1, 2, 4, 5, 7]), expected="1-2, 4-5, 7")
    compare(minimal_repr([5, 1, 3, 2, 4]), expected="1-5")
