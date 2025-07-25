"""Tests for utility functions and classes."""

import json
from pathlib import Path

from testfixtures import ShouldRaise, compare

from xerotrust.check import minimal_repr
from xerotrust.export import FileManager
from xerotrust.transform import TRANSFORMERS

from .helpers import FileChecker


def test_minimal_repr() -> None:
    """Directly test the minimal_repr helper."""
    compare(minimal_repr([]), expected="")
    compare(minimal_repr([1]), expected="1")
    compare(minimal_repr([1, 2]), expected="1-2")
    compare(minimal_repr([1, 3]), expected="1, 3")
    compare(minimal_repr([1, 2, 4, 5, 7]), expected="1-2, 4-5, 7")
    compare(minimal_repr([5, 1, 3, 2, 4]), expected="1-5")


def test_json_with_unsupported_type() -> None:
    with ShouldRaise(TypeError("Unexpected type: <class 'type'>, <class 'object'>")):
        TRANSFORMERS['json'](object)


class TestFileManager:
    def test_basic_write_and_close(self, tmp_path: Path, check_files: FileChecker) -> None:
        with FileManager() as fm:
            fm.write({"name": "file1", "data": 123}, tmp_path / "file1.jsonl")
            fm.write({"name": "file2", "data": 456}, tmp_path / "file2.jsonl")
        check_files(
            {
                'file1.jsonl': "{'name': 'file1', 'data': 123}\n",
                'file2.jsonl': "{'name': 'file2', 'data': 456}\n",
            },
        )

    def test_explicit_serializer(self, tmp_path: Path, check_files: FileChecker) -> None:
        with FileManager(max_open_files=1, serializer=json.dumps) as fm:
            fm.write({'data': 42}, tmp_path / f"file.json")
        check_files(
            {
                'file.json': '{"data": 42}\n',
            },
        )

    def test_file_eviction(self, tmp_path: Path, check_files: FileChecker) -> None:
        fm = FileManager(max_open_files=1, serializer=json.dumps)
        for i in range(1, 4):
            fm.write({"file_id": f"file{i}", "data": i}, tmp_path / f"file{i}.jsonl")
        assert len(fm._open_files) == 1
        fm.close()
        check_files(
            {
                'file1.jsonl': '{"file_id": "file1", "data": 1}\n',
                'file2.jsonl': '{"file_id": "file2", "data": 2}\n',
                'file3.jsonl': '{"file_id": "file3", "data": 3}\n',
            },
        )

    def test_multiple_writes_same_file(self, tmp_path: Path, check_files: FileChecker) -> None:
        path = tmp_path / "shared.dump"

        with FileManager() as fm:
            fm.write({'foo': 1}, path)
            fm.write({'foo': 2}, path)
            fm.write({'foo': 3}, path)

        check_files(
            {
                'shared.dump': "{'foo': 1}\n{'foo': 2}\n{'foo': 3}\n",
            },
        )

    def test_auto_close_on_exit(self, tmp_path: Path, check_files: FileChecker) -> None:
        with FileManager() as fm:
            fm.write({'name': 'testfile', 'value': 42}, tmp_path / "testfile.dump")

        assert fm._open_files == {}

        check_files(
            {
                'testfile.dump': "{'name': 'testfile', 'value': 42}\n",
            },
        )

    def test_error_handling_does_not_leave_files_open(
        self, tmp_path: Path, check_files: FileChecker
    ) -> None:
        fm = FileManager()
        exception = RuntimeError('simulated error')
        with ShouldRaise(exception):
            with fm:
                fm.write({'name': 'testfile', 'value': 99}, tmp_path / "testfile.dump")
                raise exception
        assert fm._open_files == {}
        check_files(
            {
                'testfile.dump': "{'name': 'testfile', 'value': 99}\n",
            },
        )

    def test_overwrite_existing_files(self, tmp_path: Path, check_files: FileChecker) -> None:
        (tmp_path / "file1.jsonl").write_text('THIS SHOULD BE OVERWRITTEN')
        with FileManager(max_open_files=1, serializer=json.dumps) as fm:
            fm.write({"data": 1}, tmp_path / f"file1.jsonl")
            fm.write({"data": 2}, tmp_path / f"file2.jsonl")
            fm.write({"data": 3}, tmp_path / f"file1.jsonl")
            fm.write({"data": 4}, tmp_path / f"file2.jsonl")
            assert len(fm._open_files) == 1
        check_files(
            {
                'file1.jsonl': '{"data": 1}\n{"data": 3}\n',
                'file2.jsonl': '{"data": 2}\n{"data": 4}\n',
            },
        )

    def test_append_existing_files(self, tmp_path: Path, check_files: FileChecker) -> None:
        (tmp_path / "file1.jsonl").write_text('THIS SHOULD REMAIN\n')
        with FileManager(max_open_files=1, serializer=json.dumps) as fm:
            fm.write({"data": 1}, tmp_path / f"file1.jsonl", append=True)
        check_files(
            {
                'file1.jsonl': 'THIS SHOULD REMAIN\n{"data": 1}\n',
            },
        )
