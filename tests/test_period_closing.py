# tests/test_period_closing.py
import pytest
from datetime import date
from decimal import Decimal

from gl_core.models import AccountChart, Ledger, JournalEntry, JournalLine
from gl_core.models.period import AccountingPeriod


@pytest.fixture
def sample_coa():
    # Load COA như trước
    from pathlib import Path
    from gl_core.models import AccountChart
    coa_path = Path(__file__).parent.parent / "gl_core" / "config" / "tt133_coa.yaml"
    return AccountChart.from_yaml(str(coa_path))


@pytest.fixture
def locked_period():
    period = AccountingPeriod(date(2025, 1, 1), date(2025, 3, 31), 2025, 1)
    period.lock("admin_user")
    return period


@pytest.fixture
def unlocked_period():
    return AccountingPeriod(date(2025, 4, 1), date(2025, 6, 30), 2025, 2)


@pytest.fixture
def ledger_with_periods(sample_coa, locked_period, unlocked_period):
    periods = {
        "2025-Q1": locked_period,
        "2025-Q2": unlocked_period,
    }
    return Ledger(sample_coa, periods)


def test_post_to_locked_period_fails(ledger_with_periods):
    """
    Test that posting to a locked period raises an error
    """
    entry = JournalEntry(
        date="2025-02-15",  # Belongs to locked period 2025-Q1
        lines=[
            JournalLine("1111", debit=Decimal("1000000")),
            JournalLine("5111", credit=Decimal("1000000")),
        ]
    )

    with pytest.raises(ValueError, match="Cannot post to a locked period"):
        ledger_with_periods.post(entry)


def test_post_to_unlocked_period_succeeds(ledger_with_periods):
    """
    Test that posting to an unlocked period succeeds
    """
    entry = JournalEntry(
        date="2025-05-15",  # Belongs to unlocked period 2025-Q2
        lines=[
            JournalLine("1111", debit=Decimal("1000000")),
            JournalLine("5111", credit=Decimal("1000000")),
        ]
    )

    # Should not raise
    ledger_with_periods.post(entry)

    # Check that entry was added
    assert len(ledger_with_periods.entries) == 1
    assert ledger_with_periods.get_balance("1111")["debit"] == Decimal("1000000")