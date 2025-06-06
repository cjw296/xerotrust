import json
from pathlib import Path
from textwrap import dedent
from typing import Any

import pytest
from testfixtures import ShouldRaise, compare

from .helpers import run_cli


class TestJournalsCheck:
    def write_journal_file(self, path: Path, journals: list[dict[str, Any]]) -> None:
        """Helper to write a JSON Lines file."""
        path.write_text('\n'.join(json.dumps(j) for j in journals) + '\n')

    def test_check_success_single_file(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals.jsonl"
        journals_data = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalDate": "2025-01-15T10:00:00",
                "CreatedDateUTC": "2025-01-15T10:00:00Z",
            },
            {
                "JournalID": "j2",
                "JournalNumber": 2,
                "JournalDate": "2025-01-16T11:00:00",
                "CreatedDateUTC": "2025-01-16T11:00:00Z",
            },
            {
                "JournalID": "j3",
                "JournalNumber": 3,
                "JournalDate": "2025-01-17T12:00:00",
                "CreatedDateUTC": "2025-01-17T12:00:00Z",
            },
        ]
        self.write_journal_file(journal_file, journals_data)

        result = run_cli(tmp_path, 'journals', 'check', str(journal_file))

        compare(
            result.output,
            expected=dedent("""\
                 entries: 3
           JournalNumber: 1 -> 3
             JournalDate: 2025-01-15T10:00:00 -> 2025-01-17T12:00:00
          CreatedDateUTC: 2025-01-15T10:00:00Z -> 2025-01-17T12:00:00Z
        """),
        )

    def test_check_success_multiple_files(self, tmp_path: Path) -> None:
        file1 = tmp_path / "journals-1.jsonl"
        file2 = tmp_path / "journals-2.jsonl"
        journals1 = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalDate": "2025-01-15T10:00:00",
                "CreatedDateUTC": "2025-01-15T10:00:00Z",
            },
            {
                "JournalID": "j3",
                "JournalNumber": 3,
                "JournalDate": "2025-01-17T10:00:00",
                "CreatedDateUTC": "2025-01-17T10:00:00Z",
            },
        ]
        journals2 = [
            {
                "JournalID": "j2",
                "JournalNumber": 2,
                "JournalDate": "2025-01-16T11:00:00",
                "CreatedDateUTC": "2025-01-16T11:00:00Z",
            }
        ]
        self.write_journal_file(file1, journals1)
        self.write_journal_file(file2, journals2)

        result = run_cli(tmp_path, 'journals', 'check', str(file1), str(file2))

        compare(
            result.output,
            expected=dedent("""\
                 entries: 3
           JournalNumber: 1 -> 3
             JournalDate: 2025-01-15T10:00:00 -> 2025-01-17T10:00:00
          CreatedDateUTC: 2025-01-15T10:00:00Z -> 2025-01-17T10:00:00Z
        """),
        )

    def test_check_duplicate_id(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals_dup_id.jsonl"
        journals_data = [
            {"JournalID": "j1", "JournalNumber": 1},
            {"JournalID": "j1", "JournalNumber": 2},
        ]
        self.write_journal_file(journal_file, journals_data)

        with ShouldRaise(
            ExceptionGroup(
                "Journal validation errors",
                (ValueError("Duplicate JournalID found: j1"),),
            )
        ):
            run_cli(tmp_path, 'journals', 'check', str(journal_file), expected_return_code=1)

    def test_check_duplicate_number(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals_dup_num.jsonl"
        journals_data = [
            {"JournalID": "j1", "JournalNumber": 1},
            {"JournalID": "j2", "JournalNumber": 1},
        ]
        self.write_journal_file(journal_file, journals_data)

        with ShouldRaise(
            ExceptionGroup(
                "Journal validation errors",
                (ValueError("Duplicate JournalNumber found: 1"),),
            )
        ):
            run_cli(tmp_path, 'journals', 'check', str(journal_file), expected_return_code=1)

    def test_check_missing_number(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals_missing_num.jsonl"
        journals_data = [
            {"JournalID": "j1", "JournalNumber": 1},
            {"JournalID": "j3", "JournalNumber": 3},
        ]
        self.write_journal_file(journal_file, journals_data)

        with ShouldRaise(
            ExceptionGroup(
                "Journal validation errors",
                (ValueError("Missing JournalNumbers: 2"),),
            )
        ):
            run_cli(tmp_path, 'journals', 'check', str(journal_file), expected_return_code=1)

    def test_check_missing_number_range(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals_missing_range.jsonl"
        journals_data = [
            {"JournalID": "j1", "JournalNumber": 1},
            {"JournalID": "j5", "JournalNumber": 5},
        ]
        self.write_journal_file(journal_file, journals_data)

        with ShouldRaise(
            ExceptionGroup(
                "Journal validation errors",
                (ValueError("Missing JournalNumbers: 2-4"),),
            )
        ):
            run_cli(tmp_path, 'journals', 'check', str(journal_file), expected_return_code=1)

    def test_check_combined_errors(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals_combined_errors.jsonl"
        journals_data = [
            {"JournalID": "j1", "JournalNumber": 1},
            {"JournalID": "j1", "JournalNumber": 2},  # Duplicate ID
            {"JournalID": "j3", "JournalNumber": 2},  # Duplicate Number
            {"JournalID": "j5", "JournalNumber": 5},  # Missing 4
        ]
        self.write_journal_file(journal_file, journals_data)

        # Errors are sorted alphabetically by message in check_journals before raising
        with ShouldRaise(
            ExceptionGroup(
                "Journal validation errors",
                (
                    ValueError("Duplicate JournalID found: j1"),
                    ValueError("Duplicate JournalNumber found: 2"),
                    ValueError("Missing JournalNumbers: 3-4"),
                ),
            )
        ):
            run_cli(tmp_path, 'journals', 'check', str(journal_file), expected_return_code=1)

    def test_check_empty_file(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "empty.jsonl"
        journal_file.touch()

        result = run_cli(tmp_path, 'journals', 'check', str(journal_file))
        compare(
            result.output,
            expected=dedent("""\
                 entries: 0
           JournalNumber: None -> None
             JournalDate: None -> None
          CreatedDateUTC: None -> None
        """),
        )

    def test_check_single_entry(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "single.jsonl"
        journals_data = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalDate": "2025-01-15T10:00:00",
                "CreatedDateUTC": "2025-01-15T10:00:00Z",
            }
        ]
        self.write_journal_file(journal_file, journals_data)

        result = run_cli(tmp_path, 'journals', 'check', str(journal_file))
        compare(
            result.output,
            expected=dedent("""\
                 entries: 1
           JournalNumber: 1 -> 1
             JournalDate: 2025-01-15T10:00:00 -> 2025-01-15T10:00:00
          CreatedDateUTC: 2025-01-15T10:00:00Z -> 2025-01-15T10:00:00Z
        """),
        )
