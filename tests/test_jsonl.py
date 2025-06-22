from contextlib import chdir
from pathlib import Path

from testfixtures import compare, generator
from xerotrust.jsonl import jsonl_stream


def test_minimal(tmp_path: Path) -> None:
    jsonl_path = tmp_path / "test.jsonl"
    jsonl_path.write_text('{"JournalID": "j2", "JournalNumber": 2}')
    compare(jsonl_stream([jsonl_path]), expected=generator({"JournalID": "j2", "JournalNumber": 2}))


def test_path_and_glob(tmp_path: Path) -> None:
    a1 = tmp_path / "a1.jsonl"
    a2 = tmp_path / "a2.jsonl"
    b = tmp_path / "b.jsonl"
    c = tmp_path / "c.jsonl"
    a1.write_text('"A1"')
    a2.write_text('"A2"')
    b.write_text('"B"')
    c.write_text('"C"')
    with chdir(tmp_path):
        compare(jsonl_stream(['a*.jsonl', b]), expected=generator('A1', 'A2', 'B'))


def test_non_relative(tmp_path: Path) -> None:
    a1 = tmp_path / "a1.jsonl"
    a2 = tmp_path / "a2.jsonl"
    a1.write_text('"A1"')
    a2.write_text('"A2"')
    compare(jsonl_stream([str(tmp_path / 'a*.jsonl')]), expected=generator('A1', 'A2'))
