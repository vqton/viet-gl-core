# tests/test_closing.py
import pytest
from decimal import Decimal
from pathlib import Path

from gl_core.models import AccountChart, Ledger, JournalEntry, JournalLine
from gl_core.services import close_year


@pytest.fixture
def ledger_with_revenue_expense():
    coa = AccountChart.from_yaml(
        str(Path(__file__).parent.parent / "gl_core" / "config" / "tt133_coa.yaml")
    )
    ledger = Ledger(coa)

    # Ghi doanh thu
    entry1 = JournalEntry(
        date="2025-04-01",
        lines=[
            JournalLine("1111", debit=Decimal("10000000")),
            JournalLine("5111", credit=Decimal("10000000")),
        ]
    )
    # Ghi chi phí
    entry2 = JournalEntry(
        date="2025-04-02",
        lines=[
            JournalLine("632", debit=Decimal("3000000")),
            JournalLine("156", credit=Decimal("3000000")),
        ]
    )
    ledger.post(entry1)
    ledger.post(entry2)
    return ledger


def test_close_year(ledger_with_revenue_expense):
    ledger = ledger_with_revenue_expense

    # Trước khi kết chuyển
    revenue_before = ledger.get_balance("5111")
    expense_before = ledger.get_balance("632")
    equity_before = ledger.get_balance("421")

    assert revenue_before["credit"] == Decimal("10000000")
    assert expense_before["debit"] == Decimal("3000000")
    assert equity_before["credit"] == Decimal("0")

    # Kết chuyển
    closing_entry = close_year(ledger, 2025)

    # Sau khi kết chuyển
    revenue_after = ledger.get_balance("5111")
    expense_after = ledger.get_balance("632")
    equity_after = ledger.get_balance("421")

    # Kiểm tra tài khoản doanh thu đã về 0 (số dư ròng = 0)
    assert ledger.get_net_balance("5111") == Decimal("0")
    # Tức là: Có 10tr, Nợ 10tr → số dư ròng = 0
    assert revenue_after["debit"] == Decimal("10000000")
    assert revenue_after["credit"] == Decimal("10000000")

    # Kiểm tra tài khoản chi phí đã về 0 (số dư ròng = 0)
    assert ledger.get_net_balance("632") == Decimal("0")
    assert expense_after["debit"] == Decimal("3000000")
    assert expense_after["credit"] == Decimal("3000000")

    # Kiểm tra lợi nhuận sau thuế (doanh thu - chi phí) đã chuyển vào 421
    profit = revenue_before["credit"] - expense_before["debit"]  # 10tr - 3tr = 7tr
    assert equity_after["credit"] - equity_before["credit"] == profit
    assert equity_after["credit"] == Decimal("7000000")