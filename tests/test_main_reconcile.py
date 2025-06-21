import json
from pathlib import Path
from typing import Any

import click
from testfixtures import ShouldRaise, compare

from .helpers import run_cli


class TestReconcile:
    def write_file(self, path: Path, rows: list[dict[str, Any]]) -> None:
        path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")

    def test_reconcile_success(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals.jsonl"
        transaction_file = tmp_path / "transactions.jsonl"

        journals: list[dict[str, Any]] = [
            {
                "JournalLines": [
                    {"AccountName": "Bank", "NetAmount": 100.0, "GrossAmount": 100.0},
                    {"AccountName": "Cash", "NetAmount": 50.0, "GrossAmount": 50.0},
                    {"NetAmount": 10.0, "GrossAmount": 10.0},
                ]
            },
            {"JournalLines": [{"AccountName": "Bank", "NetAmount": 50.0, "GrossAmount": 50.0}]},
        ]
        transactions: list[dict[str, Any]] = [
            {"BankAccount": {"Name": "Bank"}, "Total": 150.0},
            {"BankAccount": {"Name": "Cash"}, "Total": 50.0},
            {"Total": 1.0},
        ]

        self.write_file(journal_file, journals)
        self.write_file(transaction_file, transactions)

        result = run_cli(
            tmp_path,
            "reconcile",
            "journals-transactions",
            str(journal_file),
            "--transactions",
            str(transaction_file),
        )

        assert "AccountName" in result.output
        assert "Bank" in result.output
        assert "Cash" in result.output

    def test_reconcile_mismatch(self, tmp_path: Path) -> None:
        journal_file = tmp_path / "journals.jsonl"
        transaction_file = tmp_path / "transactions.jsonl"

        journals = [
            {"JournalLines": [{"AccountName": "Bank", "NetAmount": 100.0, "GrossAmount": 100.0}]}
        ]
        transactions = [{"BankAccount": {"Name": "Bank"}, "Total": 50.0}]

        self.write_file(journal_file, journals)
        self.write_file(transaction_file, transactions)

        result = run_cli(
            tmp_path,
            "reconcile",
            "journals-transactions",
            str(journal_file),
            "--transactions",
            str(transaction_file),
        )

        assert "-50" in result.output

    def test_reconcile_unknown(self, tmp_path: Path) -> None:
        file_path = tmp_path / "data.jsonl"
        file_path.touch()

        result = run_cli(
            tmp_path,
            "reconcile",
            "foo",
            str(file_path),
            "--transactions",
            str(file_path),
            expected_return_code=2,
        )

        expected = (
            "Usage: cli reconcile [OPTIONS] {journals-transactions} PATHS...\n"
            "Try 'cli reconcile --help' for help.\n\n"
            "Error: Invalid value for '{journals-transactions}': 'foo' is not 'journals-transactions'.\n"
        )
        compare(result.output, expected=expected)

    def test_function_unknown(self) -> None:
        from xerotrust.main import reconcile as reconcile_cmd

        with ShouldRaise(click.ClickException("Unsupported reconciliation: foo")):
            reconcile_cmd.callback("foo", tuple(), tuple())  # type: ignore[misc]
