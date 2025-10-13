# gl_core/rules/validators.py
from decimal import Decimal
from typing import List, Dict

from gl_core.models import JournalEntry, Account


def validate_journal_entry(
    entry: JournalEntry,
    chart_of_accounts: Dict[str, Account]
) -> None:
    """
    Validate a journal entry against accounting rules (double-entry + COA compliance).
    
    Raises:
        ValueError: If any rule is violated.
    """
    _validate_no_empty_lines(entry)
    _validate_all_accounts_exist(entry, chart_of_accounts)
    _validate_double_entry_balance(entry)
    _validate_no_negative_amounts(entry)
    _validate_single_side_per_line(entry)


def _validate_no_empty_lines(entry: JournalEntry) -> None:
    if not entry.lines:
        raise ValueError("Journal entry must contain at least one line.")


def _validate_all_accounts_exist(
    entry: JournalEntry,
    chart_of_accounts: Dict[str, Account]
) -> None:
    for line in entry.lines:
        if line.account_code not in chart_of_accounts:
            raise ValueError(
                f"Account '{line.account_code}' is not defined in the chart of accounts."
            )


def _validate_double_entry_balance(entry: JournalEntry) -> None:
    total_debit = sum(line.debit for line in entry.lines)
    total_credit = sum(line.credit for line in entry.lines)
    
    # So sánh Decimal an toàn
    if total_debit != total_credit:
        raise ValueError(
            f"Journal entry is unbalanced. Total Debit: {total_debit}, Total Credit: {total_credit}"
        )


def _validate_no_negative_amounts(entry: JournalEntry) -> None:
    for line in entry.lines:
        if line.debit < 0 or line.credit < 0:
            raise ValueError(
                f"Negative amounts are not allowed. Line: {line.account_code}"
            )


def _validate_single_side_per_line(entry: JournalEntry) -> None:
    for line in entry.lines:
        if line.debit > 0 and line.credit > 0:
            raise ValueError(
                f"Journal line for account '{line.account_code}' cannot have both debit and credit."
            )