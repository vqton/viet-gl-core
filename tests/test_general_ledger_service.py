"""
Test cases for General Ledger Service.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from src.domain.entities.journal_entry import JournalEntry
from src.application.services.general_ledger_service import GeneralLedgerService
from tests.test_helpers import create_journal_entry


def test_get_account_balance():
    """Test tính số dư tài khoản."""
    journal_repo = Mock()

    # Mock bút toán cho TK 111
    entries = [
        JournalEntry(
            account="111",
            debit=Decimal("10000000"),
            credit=Decimal("0"),
            description="Thu tiền bán hàng",
            source_document_id="CT-001",
            accounting_date=date(2026, 4, 15),
            accounting_period_code="2026-Q2",
            created_by="NV001",
            created_at=date(2026, 4, 15),
            approved_by="KT_TRUONG",
            approved_at=date(2026, 4, 15),
            status="approved",
        ),
        JournalEntry(
            account="111",
            debit=Decimal("0"),
            credit=Decimal("3000000"),
            description="Chi mua văn phòng phẩm",
            source_document_id="PC-001",
            accounting_date=date(2026, 4, 20),
            accounting_period_code="2026-Q2",
            created_by="NV001",
            created_at=date(2026, 4, 20),
            approved_by="KT_TRUONG",
            approved_at=date(2026, 4, 20),
            status="approved",
        ),
    ]

    journal_repo.find_by_account.return_value = entries

    service = GeneralLedgerService(journal_repo)
    balance = service.get_account_balance("111", "2026-Q2")

    assert balance.debit_turnover == Decimal("10000000")
    assert balance.credit_turnover == Decimal("3000000")
    assert balance.closing_balance == Decimal("7000000")  # Dư Nợ


def test_verify_accounting_equation():
    """Test kiểm tra cân đối kế toán."""
    journal_repo = Mock()

    entries = [
        create_journal_entry(
            account="111", debit=Decimal("10000000"), source_document_id="CT-001"
        ),
        create_journal_entry(
            account="5111", credit=Decimal("10000000"), source_document_id="INV-001"
        ),
    ]

    # Mock get_all_entries → trả về toàn bộ bút toán
    journal_repo.get_all_entries.return_value = entries
    
    # Mock find_by_account → trả về bút toán theo tài khoản
    def mock_find_by_account(account, period):
        return [e for e in entries if e.account == account]
    
    journal_repo.find_by_account.side_effect = mock_find_by_account
    
    service = GeneralLedgerService(journal_repo)
    assert service.verify_accounting_equation("2026-Q2")
