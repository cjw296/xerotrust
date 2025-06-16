import json
from pathlib import Path
from typing import Any, Sequence

from textwrap import dedent
from testfixtures import compare, Replacer
from unittest.mock import Mock
import logging

from xerotrust.flatten import ALL_JOURNAL_KEYS
from .helpers import run_cli


class TestFlatten:
    def write_journal_file(self, path: Path, journals: list[dict[str, Any]]) -> None:
        """Helper to write a JSON Lines file."""
        path.write_text('\n'.join(json.dumps(j) for j in journals) + '\n')

    def check_output(self, output: str, *, expected: Sequence[dict[str, Any]]) -> None:
        expected_lines = [','.join(ALL_JOURNAL_KEYS)]
        for row in expected:
            expected_lines.append(','.join(str(row.get(k, '')) for k in ALL_JOURNAL_KEYS))
        compare(output, expected='\n'.join(expected_lines) + '\n')

    def check_output_with_extras(self, output: str, *, expected: Sequence[dict[str, Any]]) -> None:
        fieldnames = list(ALL_JOURNAL_KEYS)
        extra_keys: set[str] = set()
        for row in expected:
            extra_keys.update(row.keys())
        extra_keys.difference_update(fieldnames)
        fieldnames.extend(sorted(extra_keys))

        expected_lines = [','.join(fieldnames)]
        for row in expected:
            expected_lines.append(','.join(str(row.get(k, '')) for k in fieldnames))
        compare(output, expected='\n'.join(expected_lines) + '\n')

    def test_flatten_single_file(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals.jsonl"
        journals_data = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalDate": "2025-01-15T00:00:00",
                "JournalLines": [
                    {"JournalLineID": "jl1a", "AccountCode": "100", "NetAmount": 10.0},
                    {"JournalLineID": "jl1b", "AccountCode": "200", "NetAmount": -10.0},
                ],
            },
            {
                "JournalID": "j2",
                "JournalNumber": 2,
                "JournalDate": "2025-01-16T00:00:00",
                "JournalLines": [
                    {"JournalLineID": "jl2a", "AccountCode": "300", "NetAmount": 20.0}
                ],
            },
        ]
        self.write_journal_file(journal_file, journals_data)

        result = run_cli(tmp_path, 'flatten', str(journal_file))

        # We don't use check_output here so we can see what the raw csv looks like,
        header = ','.join(ALL_JOURNAL_KEYS)
        expected_csv = dedent(f"""\
            {header}
            j1,2025-01-15T00:00:00,1,,jl1a,,100,,,,10.0,,,,,,,,
            j1,2025-01-15T00:00:00,1,,jl1b,,200,,,,-10.0,,,,,,,,
            j2,2025-01-16T00:00:00,2,,jl2a,,300,,,,20.0,,,,,,,,
        """)
        compare(result.output, expected=expected_csv)

    def test_flatten_multiple_files(self, tmp_path: Path) -> None:
        file1 = tmp_path / "journals1.jsonl"
        file2 = tmp_path / "journals2.jsonl"
        journals_data1 = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalLines": [{"JournalLineID": "jl1a"}],
            }
        ]
        journals_data2 = [
            {
                "JournalID": "j2",
                "JournalNumber": 2,
                "JournalLines": [{"JournalLineID": "jl2a"}],
            }
        ]
        self.write_journal_file(file1, journals_data1)
        self.write_journal_file(file2, journals_data2)

        result = run_cli(tmp_path, 'flatten', str(file1), str(file2))

        expected_rows = [
            {'JournalID': 'j1', 'JournalNumber': 1, 'JournalLineID': 'jl1a'},
            {'JournalID': 'j2', 'JournalNumber': 2, 'JournalLineID': 'jl2a'},
        ]
        self.check_output(result.output, expected=expected_rows)

    def test_flatten_empty_file(self, tmp_path: Path) -> None:
        empty_file = tmp_path / "empty.jsonl"
        empty_file.touch()

        result = run_cli(tmp_path, 'flatten', str(empty_file))

        self.check_output(result.output, expected=[])

    def test_flatten_file_with_no_journal_lines(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "no_lines.jsonl"
        journals_data = [
            {"JournalID": "j1", "JournalNumber": 1, "JournalLines": []},
            {"JournalID": "j2", "JournalNumber": 2},  # JournalLines key missing
        ]
        self.write_journal_file(journal_file, journals_data)

        result = run_cli(tmp_path, 'flatten', str(journal_file))

        self.check_output(result.output, expected=[])

    def test_flatten_file_with_some_journal_lines_empty(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "some_lines_empty.jsonl"
        journals_data = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalLines": [{"JournalLineID": "jl1a", "AccountCode": "100"}],
            },
            {"JournalID": "j2", "JournalNumber": 2, "JournalLines": []},  # Empty JournalLines
            {
                "JournalID": "j3",
                "JournalNumber": 3,
                # JournalLines key missing
            },
            {
                "JournalID": "j4",
                "JournalNumber": 4,
                "JournalLines": [{"JournalLineID": "jl4a", "AccountCode": "400"}],
            },
        ]
        self.write_journal_file(journal_file, journals_data)

        result = run_cli(tmp_path, 'flatten', str(journal_file))

        expected_rows = [
            {
                'JournalID': 'j1',
                'JournalNumber': 1,
                'JournalLineID': 'jl1a',
                'AccountCode': '100',
            },
            {
                'JournalID': 'j4',
                'JournalNumber': 4,
                'JournalLineID': 'jl4a',
                'AccountCode': '400',
            },
        ]
        self.check_output(result.output, expected=expected_rows)

    def test_flatten_to_output_file(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals.jsonl"
        output_csv_file = tmp_path / "output.csv"
        journals_data = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalLines": [{"JournalLineID": "jl1a", "AccountCode": "100"}],
            }
        ]
        self.write_journal_file(journal_file, journals_data)

        run_cli(
            tmp_path,
            'flatten',
            str(journal_file),
            '--output',
            str(output_csv_file),
        )

        expected_rows = [
            {'JournalID': 'j1', 'JournalNumber': 1, 'JournalLineID': 'jl1a', 'AccountCode': '100'}
        ]
        self.check_output(output_csv_file.read_text(), expected=expected_rows)

    def test_flatten_with_tracking_categories(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals_with_tracking.jsonl"
        journals_data = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalDate": "2025-01-15T00:00:00",
                "JournalLines": [
                    {
                        "JournalLineID": "jl1a",
                        "AccountCode": "100",
                        "NetAmount": 10.0,
                        "TrackingCategories": ["Region A", "Project X"],
                        "Reference": {'one': 1, 'aye': 'A'},
                    }
                ],
            }
        ]
        self.write_journal_file(journal_file, journals_data)

        result = run_cli(tmp_path, 'flatten', str(journal_file))

        expected_rows = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalDate": "2025-01-15T00:00:00",
                "JournalLineID": "jl1a",
                "AccountCode": "100",
                "NetAmount": 10.0,
                "TrackingCategories": '"[""Region A"", ""Project X""]"',
                "Reference": '"{""one"": 1, ""aye"": ""A""}"',
            }
        ]
        self.check_output(result.output, expected=expected_rows)

    def test_flatten_with_transactions(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals.jsonl"
        tx_file = tmp_path / "transactions.jsonl"
        journals_data = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalLines": [
                    {
                        "JournalLineID": "jl1",
                        "SourceID": "bt1",
                        "SourceType": "BANKTRANSACTION",
                    }
                ],
            }
        ]
        self.write_journal_file(journal_file, journals_data)
        tx_file.write_text(
            json.dumps(
                {
                    "BankTransactionID": "bt1",
                    "Date": "2023-03-15T00:00:00+00:00",
                    "DateString": "2023-03-15T00:00:00",
                    "UpdatedDateUTC": "2023-03-15T00:00:00+00:00",
                    "Total": 100.0,
                    "Type": "SPEND",
                    "BankAccount": {"Name": "Test Account"},
                }
            )
            + "\n"
        )

        result = run_cli(
            tmp_path,
            "flatten",
            str(journal_file),
            "--transactions",
            str(tx_file),
        )

        expected_rows = [
            {
                "JournalID": "j1",
                "JournalNumber": 1,
                "JournalLineID": "jl1",
                "SourceID": "bt1",
                "SourceType": "BANKTRANSACTION",
                "BankAccount": '"{""Name"": ""Test Account""}"',
                "BankTransactionID": "bt1",
                "Date": "2023-03-15T00:00:00+00:00",
                "DateString": "2023-03-15T00:00:00",
                "Total": 100.0,
                "Type": "SPEND",
                "UpdatedDateUTC": "2023-03-15T00:00:00+00:00",
            }
        ]
        self.check_output_with_extras(result.output, expected=expected_rows)

    def test_flatten_missing_transaction_logs_warning(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals.jsonl"
        self.write_journal_file(
            journal_file,
            [
                {
                    "JournalID": "j1",
                    "JournalNumber": 1,
                    "JournalLines": [
                        {
                            "JournalLineID": "jl1",
                            "SourceID": "bt-missing",
                            "SourceType": "BANKTRANSACTION",
                        }
                    ],
                }
            ],
        )
        tx_file = tmp_path / "transactions.jsonl"
        tx_file.write_text("")

        with Replacer() as replace:
            mock_warning = Mock()
            replace.in_module(logging.warning, mock_warning, module=logging)
            run_cli(
                tmp_path,
                "flatten",
                str(journal_file),
                "--transactions",
                str(tx_file),
            )
            mock_warning.assert_called_once()
            compare(mock_warning.call_args.args[1], expected="bt-missing")
            compare(mock_warning.call_args.args[2], expected="BANKTRANSACTION")
