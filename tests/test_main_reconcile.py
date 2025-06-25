from pathlib import Path
from typing import Any

import click
from pytest_insta import SnapshotFixture
from testfixtures import ShouldRaise, compare

from .helpers import run_cli, write_jsonl_file

SAMPLE_JOURNAL = {
    "JournalDate": "2023-03-15T00:00:00+00:00",
    "JournalNumber": 1,
    "JournalLines": [
        {
            "AccountName": "Bank",
            "AccountType": "BANK",
            "GrossAmount": -50.0,
        },
        {
            "AccountName": "Expected",
            "AccountCode": "exp",
            "AccountType": "DIRECTCOSTS",
            "GrossAmount": 50.0,
        },
    ],
}

SAMPLE_TRANSACTION = {
    "Date": "2023-03-15T00:00:00+00:00",
    "BankAccount": {"Name": "Bank"},
    "Total": 50.0,
    "Status": "AUTHORISED",
    "Type": "SPEND",
    "LineItems": [
        {
            "AccountCode": "EXP",
            "LineAmount": 50.0,
        }
    ],
}


class TestReconcile:
    def test_success_same_date(self, tmp_path: Path, snapshot: SnapshotFixture) -> None:
        """Test successful reconciliation when all data is on the same date."""
        journal_file = tmp_path / "journals.jsonl"
        transaction_file = tmp_path / "transactions.jsonl"

        journals = [SAMPLE_JOURNAL]
        transactions = [SAMPLE_TRANSACTION]

        write_jsonl_file(journal_file, journals)
        write_jsonl_file(transaction_file, transactions)

        result = run_cli(
            tmp_path,
            "reconcile",
            f"journals={journal_file}",
            f"transactions={transaction_file}",
        )

        compare(result.output, expected=snapshot())

    def write_source_with_diff(self, tmp_path: Path) -> tuple[Path, Path]:
        journal_file = tmp_path / "journals.jsonl"
        transaction_file = tmp_path / "transactions.jsonl"

        journals = [
            {
                "JournalDate": "2023-03-15T00:00:00+00:00",
                "JournalNumber": 1,
                "JournalLines": [
                    {"AccountName": "Bank", "AccountType": "BANK", "GrossAmount": 100.0},
                ],
            },
            {
                "JournalDate": "2023-03-16T00:00:00+00:00",
                "JournalNumber": 2,
                "JournalLines": [
                    {"AccountName": "Cash", "AccountType": "BANK", "GrossAmount": 201.0},
                ],
            },
        ]
        transactions = [
            {
                "Date": "2023-03-15T00:00:00+00:00",
                "BankAccount": {"Name": "Bank"},
                "Total": -50.0,  # Different amount
                "Status": "AUTHORISED",
                "Type": "SPEND",
                "LineItems": [],
            },
            {
                "Date": "2023-03-16T00:00:00+00:00",
                "BankAccount": {"Name": "Cash"},
                "Total": -200.0,
                "Status": "AUTHORISED",
                "Type": "SPEND",
                "LineItems": [],
            },
        ]

        write_jsonl_file(journal_file, journals)
        write_jsonl_file(transaction_file, transactions)

        return journal_file, transaction_file

    def test_mismatch_first_date(self, tmp_path: Path, snapshot: SnapshotFixture) -> None:
        """Test reconciliation stops at first date with differences."""
        journal_file, transaction_file = self.write_source_with_diff(tmp_path)
        result = run_cli(
            tmp_path,
            "reconcile",
            f"journals={journal_file}",
            f"transactions={transaction_file}",
            '--stop-on-diff',
        )
        compare(result.output, expected=snapshot())

    def test_mismatch_first_date_show_all(self, tmp_path: Path, snapshot: SnapshotFixture) -> None:
        """Test reconciliation stops at first date with differences."""
        journal_file, transaction_file = self.write_source_with_diff(tmp_path)
        result = run_cli(
            tmp_path,
            "reconcile",
            f"journals={journal_file}",
            f"transactions={transaction_file}",
        )
        compare(result.output, expected=snapshot())

    def test_with_currliab_filtering(self, tmp_path: Path, snapshot: SnapshotFixture) -> None:
        """Test that journals with CURRLIAB account types are filtered out."""
        journal_file = tmp_path / "journals.jsonl"
        transaction_file = tmp_path / "transactions.jsonl"

        journals = [
            {
                "JournalDate": "2023-03-15T00:00:00+00:00",
                "JournalNumber": 1,
                "JournalLines": [
                    {"AccountName": "Bank", "AccountType": "BANK", "GrossAmount": 75.0},
                    {"AccountName": "Liability", "AccountType": "CURRLIAB", "GrossAmount": -75.0},
                ],
            },
            SAMPLE_JOURNAL,
        ]
        transactions = [SAMPLE_TRANSACTION]

        write_jsonl_file(journal_file, journals)
        write_jsonl_file(transaction_file, transactions)

        result = run_cli(
            tmp_path,
            "reconcile",
            f"journals={journal_file}",
            f"transactions={transaction_file}",
        )

        compare(result.output, expected=snapshot())

    def test_with_deleted_transaction(self, tmp_path: Path, snapshot: SnapshotFixture) -> None:
        """Test that deleted transactions are filtered out."""
        journal_file = tmp_path / "journals.jsonl"
        transaction_file = tmp_path / "transactions.jsonl"

        journals = [
            {
                "JournalDate": "2023-03-15T00:00:00+00:00",
                "JournalNumber": 1,
                "JournalLines": [
                    {"AccountName": "Bank", "AccountType": "BANK", "GrossAmount": 100.0},
                ],
            },
        ]
        transactions = [
            {
                "Date": "2023-03-15T00:00:00+00:00",
                "BankAccount": {"Name": "Bank"},
                "Total": -100.0,
                "Status": "AUTHORISED",
                "Type": "SPEND",
                "LineItems": [],
            },
            {
                "Date": "2023-03-15T00:00:00+00:00",
                "BankAccount": {"Name": "Bank"},
                "Total": 50.0,
                "Status": "DELETED",  # Should be filtered out
                "Type": "SPEND",
                "LineItems": [],
            },
        ]

        write_jsonl_file(journal_file, journals)
        write_jsonl_file(transaction_file, transactions)

        result = run_cli(
            tmp_path,
            "reconcile",
            f"journals={journal_file}",
            f"transactions={transaction_file}",
        )

        compare(result.output, expected=snapshot())

    def test_with_spend_transfer_type(self, tmp_path: Path, snapshot: SnapshotFixture) -> None:
        """Test that SPEND-TRANSFER transactions are handled correctly."""
        journal_file = tmp_path / "journals.jsonl"
        transaction_file = tmp_path / "transactions.jsonl"

        journals = [
            {
                "JournalDate": "2023-03-15T00:00:00+00:00",
                "JournalNumber": 1,
                "JournalLines": [
                    {"AccountName": "Bank", "AccountType": "BANK", "GrossAmount": -100.0},
                ],
            },
        ]
        transactions = [
            {
                "Date": "2023-03-15T00:00:00+00:00",
                "BankAccount": {"Name": "Bank"},
                "Total": 100.0,
                "Status": "AUTHORISED",
                "Type": "SPEND-TRANSFER",  # Should be negated
                "LineItems": [],
            },
        ]

        write_jsonl_file(journal_file, journals)
        write_jsonl_file(transaction_file, transactions)

        result = run_cli(
            tmp_path,
            "reconcile",
            f"journals={journal_file}",
            f"transactions={transaction_file}",
        )

        compare(result.output, expected=snapshot())

    def test_with_receive_line_items(self, tmp_path: Path, snapshot: SnapshotFixture) -> None:
        """Test reconciliation with RECEIVE transaction line items."""
        journal_file = tmp_path / "journals.jsonl"
        transaction_file = tmp_path / "transactions.jsonl"

        journals = [
            {
                "JournalDate": "2023-03-15T00:00:00+00:00",
                "JournalNumber": 1,
                "JournalLines": [
                    {"AccountName": "Bank", "AccountType": "BANK", "GrossAmount": 100.0},
                    {
                        "AccountName": "",
                        "AccountType": "",
                        "AccountCode": "200",
                        "GrossAmount": -100.0,
                    },
                ],
            },
        ]
        transactions = [
            {
                "Date": "2023-03-15T00:00:00+00:00",
                "BankAccount": {"Name": "Bank"},
                "Total": 100.0,
                "Status": "AUTHORISED",
                "Type": "RECEIVE",
                "LineItems": [
                    {"AccountCode": "200", "LineAmount": 100.0},  # Should be negated for RECEIVE
                ],
            },
        ]

        write_jsonl_file(journal_file, journals)
        write_jsonl_file(transaction_file, transactions)

        result = run_cli(
            tmp_path,
            "reconcile",
            f"journals={journal_file}",
            f"transactions={transaction_file}",
        )

        compare(result.output, expected=snapshot())

    def write_sources_with_diff_and_order_matters(self, tmp_path: Path) -> tuple[Path, Path]:
        journal_file = tmp_path / "journals.jsonl"
        transaction_file = tmp_path / "transactions.jsonl"

        # Add journals out of order
        journals = [
            {
                "JournalDate": "2023-03-16T00:00:00+00:00",  # Later date first
                "JournalNumber": 2,
                "JournalLines": [
                    {"AccountName": "Bank C", "AccountType": "BANK", "GrossAmount": 200.0},
                ],
            },
            {
                "JournalDate": "2023-03-15T00:00:00+00:00",  # Earlier date second
                "JournalNumber": 1,
                "JournalLines": [
                    {"AccountName": "Bank B", "AccountType": "BANK", "GrossAmount": 100.0},
                ],
            },
            {
                "JournalDate": "2023-03-15T00:00:00+00:00",  # Earlier date, out of order name
                "JournalNumber": 1,
                "JournalLines": [
                    {"AccountName": "Bank A", "AccountType": "BANK", "GrossAmount": 50.0},
                ],
            },
        ]
        transactions = [
            {
                "Date": "2023-03-15T00:00:00+00:00",
                "BankAccount": {"Name": "Bank B"},
                "Total": -50.0,  # Mismatch on first date
                "Status": "AUTHORISED",
                "Type": "SPEND",
                "LineItems": [],
            },
            {
                "Date": "2023-03-15T00:00:00+00:00",
                "BankAccount": {"Name": "Bank A"},
                "Total": -25.0,  # Mismatch on first date
                "Status": "AUTHORISED",
                "Type": "SPEND",
                "LineItems": [],
            },
            {
                "Date": "2023-03-16T00:00:00+00:00",
                "BankAccount": {"Name": "Bank C"},
                "Total": -200.0,  # This would match but shouldn't be processed
                "Status": "AUTHORISED",
                "Type": "SPEND",
                "LineItems": [],
            },
        ]

        write_jsonl_file(journal_file, journals)
        write_jsonl_file(transaction_file, transactions)

        return journal_file, transaction_file

    def test_stop_on_diff(self, tmp_path: Path, snapshot: SnapshotFixture) -> None:
        journal_file, transaction_file = self.write_sources_with_diff_and_order_matters(tmp_path)
        result = run_cli(
            tmp_path,
            "reconcile",
            f"journals={journal_file}",
            f"transactions={transaction_file}",
            '--stop-on-diff',
        )
        compare(result.output, expected=snapshot())

    def test_no_stop_on_diff(self, tmp_path: Path, snapshot: SnapshotFixture) -> None:
        journal_file, transaction_file = self.write_sources_with_diff_and_order_matters(tmp_path)
        result = run_cli(
            tmp_path,
            "reconcile",
            f"journals={journal_file}",
            f"transactions={transaction_file}",
        )
        compare(result.output, expected=snapshot())

    def test_invalid_source_count(self, tmp_path: Path) -> None:
        """Test error when wrong number of sources provided."""
        journal_file = tmp_path / "journals.jsonl"
        write_jsonl_file(journal_file, [])

        result = run_cli(
            tmp_path,
            "reconcile",
            f"journals={journal_file}",
            expected_return_code=1,
        )

        compare(
            result.output,
            expected=(
                f"Error: Exactly two sources must be specified, "
                f"got: (['journals', '{journal_file}'],)\n"
            ),
        )

    def test_unsupported_endpoint(self, tmp_path: Path) -> None:
        """Test error when unsupported endpoint provided."""
        journal_file = tmp_path / "journals.jsonl"
        other_file = tmp_path / "other.jsonl"
        write_jsonl_file(journal_file, [])
        write_jsonl_file(other_file, [])

        result = run_cli(
            tmp_path,
            "reconcile",
            f"journals={journal_file}",
            f"other={other_file}",
            expected_return_code=1,
        )

        expected = (
            "Error: Unsupported endpoint: other. Supported endpoints: journals, transactions\n"
        )
        compare(result.output, expected=expected)

    def test_journals_with_journals(self, tmp_path: Path, snapshot: SnapshotFixture) -> None:
        journal_file = tmp_path / "journals.jsonl"
        journals = [
            {
                "JournalDate": "2023-03-15T00:00:00+00:00",
                "JournalNumber": 1,
                "JournalLines": [
                    {"AccountName": "Bank", "AccountType": "BANK", "GrossAmount": 100.0},
                ],
            },
        ]
        write_jsonl_file(journal_file, journals)

        result = run_cli(
            tmp_path,
            "reconcile",
            f"journals={journal_file}",
            f"journals={journal_file}",  # Two journals should reconcile successfully
            expected_return_code=0,
        )

        compare(result.output, expected=snapshot())

    def test_account_missing_in_transactions(
        self, tmp_path: Path, snapshot: SnapshotFixture
    ) -> None:
        """Test reconciliation where journals has an account that transactions does not."""
        journal_file = tmp_path / "journals.jsonl"
        transaction_file = tmp_path / "transactions.jsonl"

        journals = [
            {
                "JournalDate": "2023-03-15T00:00:00+00:00",
                "JournalNumber": 1,
                "JournalLines": [
                    {"AccountName": "Bank", "AccountType": "BANK", "GrossAmount": 100.0},
                    {
                        "AccountName": "Missing Account",
                        "AccountType": "EXPENSE",
                        "GrossAmount": -100.0,
                    },
                ],
            },
        ]
        transactions = [
            {
                "Date": "2023-03-15T00:00:00+00:00",
                "BankAccount": {"Name": "Bank"},
                "Total": -100.0,
                "Status": "AUTHORISED",
                "Type": "SPEND",
                "LineItems": [],
            },
        ]

        write_jsonl_file(journal_file, journals)
        write_jsonl_file(transaction_file, transactions)

        result = run_cli(
            tmp_path,
            "reconcile",
            f"journals={journal_file}",
            f"transactions={transaction_file}",
        )

        compare(result.output, expected=snapshot())

    def test_malformed_parameter(self, tmp_path: Path) -> None:
        """Test reconciliation with malformed key=value parameter."""
        journal_file = tmp_path / "journals.jsonl"
        write_jsonl_file(journal_file, [])

        result = run_cli(
            tmp_path,
            "reconcile",
            "malformed_parameter",
            expected_return_code=2,
        )

        assert "Expected key=value format" in result.output
