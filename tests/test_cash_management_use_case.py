"""
Test cases for Cash Management Use Case.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from src.application.dtos.cash_transaction_dto import CashTransactionDTO, CashTransactionType
from src.application.use_cases.cash_management_use_case import CashManagementUseCase


def test_import_cash_management_use_case():
    """Kiểm tra không có ImportError."""
    assert CashManagementUseCase is not None

def test_cash_management_use_case_initialization():
    """Kiểm tra khởi tạo Use Case thành công."""
    journal_repo = Mock()
    use_case = CashManagementUseCase(journal_repo)
    assert use_case.journal_entry_repo == journal_repo

def test_cash_in_transaction():
    """Test thu tiền mặt."""
    journal_repo = Mock()
    
    dto = CashTransactionDTO(
        transaction_number="CT-001",
        transaction_date=date(2026, 4, 22),
        transaction_type=CashTransactionType.CASH_IN,
        amount=Decimal('10000000'),
        description="Thu tiền bán hàng",
        related_document_id="INV-001"
    )
    
    use_case = CashManagementUseCase(journal_repo)
    entry = use_case.execute(dto, created_by="NV001")
    
    assert entry.account == "111"
    assert entry.debit == Decimal('10000000')
    assert entry.credit == Decimal('0')
    assert entry.source_document_id == "CT-001"
    assert entry.original_entry_id == "INV-001"
    journal_repo.save.assert_called_once()

def test_cash_out_transaction():
    """Test chi tiền mặt."""
    journal_repo = Mock()
    
    dto = CashTransactionDTO(
        transaction_number="PC-001",
        transaction_date=date(2026, 4, 22),
        transaction_type=CashTransactionType.CASH_OUT,
        amount=Decimal('5000000'),
        description="Chi mua văn phòng phẩm",
        related_document_id="PO-001"
    )
    
    use_case = CashManagementUseCase(journal_repo)
    entry = use_case.execute(dto, created_by="NV001")
    
    assert entry.account == "111"
    assert entry.debit == Decimal('0')
    assert entry.credit == Decimal('5000000')
    journal_repo.save.assert_called_once()

def test_bank_in_transaction():
    """Test thu tiền gửi ngân hàng."""
    journal_repo = Mock()
    
    dto = CashTransactionDTO(
        transaction_number="CTB-001",
        transaction_date=date(2026, 4, 22),
        transaction_type=CashTransactionType.BANK_IN,
        amount=Decimal('20000000'),
        description="Khách hàng chuyển khoản",
        related_document_id="INV-002"
    )
    
    use_case = CashManagementUseCase(journal_repo)
    entry = use_case.execute(dto, created_by="NV001")
    
    assert entry.account == "112"
    assert entry.debit == Decimal('20000000')
    journal_repo.save.assert_called_once()

def test_bank_out_transaction():
    """Test chi tiền gửi ngân hàng."""
    journal_repo = Mock()
    
    dto = CashTransactionDTO(
        transaction_number="PTB-001",
        transaction_date=date(2026, 4, 22),
        transaction_type=CashTransactionType.BANK_OUT,
        amount=Decimal('15000000'),
        description="Thanh toán NCC qua chuyển khoản",
        related_document_id="PO-002"
    )
    
    use_case = CashManagementUseCase(journal_repo)
    entry = use_case.execute(dto, created_by="NV001")
    
    assert entry.account == "112"
    assert entry.credit == Decimal('15000000')
    journal_repo.save.assert_called_once()

def test_invalid_amount():
    """Test lỗi khi số tiền <= 0."""
    journal_repo = Mock()
    use_case = CashManagementUseCase(journal_repo)
    
    dto = CashTransactionDTO(
        transaction_number="CT-001",
        transaction_date=date(2026, 4, 22),
        transaction_type=CashTransactionType.CASH_IN,
        amount=Decimal('0'),
        description="Sai số tiền"
    )
    
    try:
        use_case.execute(dto, "NV001")
        assert False, "Phải ném ValueError"
    except ValueError as e:
        assert "Số tiền phải lớn hơn 0" in str(e)