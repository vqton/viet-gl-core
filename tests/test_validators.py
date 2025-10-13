# tests/test_validators.py
import pytest
from decimal import Decimal

from gl_core.models import Account, AccountChart, JournalEntry, JournalLine
from gl_core.rules import validate_journal_entry
from gl_core.models.account import AccountType

@pytest.fixture
def sample_coa():
    accounts = {
        "1111": Account("1111", "Tiền mặt", AccountType.ASSET, "debit"),
        "5111": Account("5111", "Doanh thu bán hàng", AccountType.REVENUE, "credit"),
        "3331": Account("3331", "Thuế GTGT phải nộp", AccountType.LIABILITY, "credit"),
    }
    return accounts

def test_valid_journal_passes(sample_coa):
    entry = JournalEntry(
        date="2025-04-01",
        lines=[
            JournalLine("1111", debit=Decimal("11000000")),
            JournalLine("3331", credit=Decimal("1000000")),
            JournalLine("5111", credit=Decimal("10000000")),
        ]
    )
    # Should not raise
    validate_journal_entry(entry, sample_coa)

def test_unbalanced_journal_raises(sample_coa):
    entry = JournalEntry(
        date="2025-04-01",
        lines=[
            JournalLine("1111", debit=Decimal("10000000")),
            JournalLine("5111", credit=Decimal("9000000")),  # thiếu 1tr
        ]
    )
    with pytest.raises(ValueError, match="unbalanced"):
        validate_journal_entry(entry, sample_coa)

def test_unknown_account_raises(sample_coa):
    entry = JournalEntry(
        date="2025-04-01",
        lines=[
            JournalLine("9999", debit=Decimal("10000000")),  # không tồn tại
            JournalLine("5111", credit=Decimal("10000000")),
        ]
    )
    with pytest.raises(ValueError, match="not defined"):
        validate_journal_entry(entry, sample_coa)