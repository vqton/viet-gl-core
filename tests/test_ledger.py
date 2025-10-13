# tests/test_ledger.py
import pytest
from decimal import Decimal
from pathlib import Path

from gl_core.models import AccountChart, Ledger, JournalEntry, JournalLine
from gl_core.models.account import AccountType


@pytest.fixture
def sample_coa():
    accounts = {
        "1111": AccountChart.from_yaml(
            str(Path(__file__).parent.parent / "gl_core" / "config" / "tt133_coa.yaml")
        ).accounts,
    }
    # Lấy COA đầy đủ từ file
    coa = AccountChart.from_yaml(
        str(Path(__file__).parent.parent / "gl_core" / "config" / "tt133_coa.yaml")
    )
    return coa


def test_ledger_post_and_get_balance(sample_coa):
    ledger = Ledger(sample_coa)

    # Ghi sổ: bán hàng thu tiền mặt
    entry = JournalEntry(
        date="2025-04-01",
        lines=[
            JournalLine("1111", debit=Decimal("11000000")),
            JournalLine("3331", credit=Decimal("1000000")),
            JournalLine("5111", credit=Decimal("10000000")),
        ]
    )
    ledger.post(entry)

    # Kiểm tra số dư
    cash_balance = ledger.get_balance("1111")
    assert cash_balance["debit"] == Decimal("11000000")
    assert cash_balance["credit"] == Decimal("0")

    revenue_balance = ledger.get_balance("5111")
    assert revenue_balance["credit"] == Decimal("10000000")


def test_ledger_trial_balance(sample_coa):
    ledger = Ledger(sample_coa)

    entry = JournalEntry(
        date="2025-04-01",
        lines=[
            JournalLine("1111", debit=Decimal("10000000")),
            JournalLine("5111", credit=Decimal("10000000")),
        ]
    )
    ledger.post(entry)

    trial = ledger.get_trial_balance()
    assert "1111" in trial
    assert "5111" in trial
    assert trial["1111"]["debit"] == Decimal("10000000")
    assert trial["5111"]["credit"] == Decimal("10000000")