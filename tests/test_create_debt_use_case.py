"""
Test cases for Create Debt Use Case.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from src.application.dtos.debt_creation_dto import DebtCreationDTO
from src.application.use_cases.create_debt_use_case import CreateDebtUseCase


def test_import_create_debt_use_case():
    """Kiểm tra không có ImportError."""
    assert CreateDebtUseCase is not None

def test_create_debt_use_case_initialization():
    """Kiểm tra khởi tạo Use Case thành công."""
    debt_repo = Mock()
    use_case = CreateDebtUseCase(debt_repo)
    assert use_case.debt_repo == debt_repo

def test_create_debt_successfully():
    """Test tạo công nợ thành công."""
    debt_repo = Mock()
    debt_repo.save.return_value = "DEBT-001"
    
    dto = DebtCreationDTO(
        party_id="CUST-001",
        party_name="Cty ABC",
        party_tax_code="9876543210",
        document_id="INV-001",
        document_type="SALES",
        amount=Decimal('11000000'),  # 10M + 1M GTGT
        due_date=date(2026, 5, 15)
    )
    
    use_case = CreateDebtUseCase(debt_repo)
    debt_id = use_case.execute(dto)
    
    assert debt_id == "DEBT-001"
    debt_repo.save.assert_called_once_with(dto)

def test_create_debt_with_invalid_amount():
    """Test lỗi khi số tiền <= 0."""
    debt_repo = Mock()
    use_case = CreateDebtUseCase(debt_repo)
    
    dto = DebtCreationDTO(
        party_id="CUST-001",
        party_name="Cty ABC",
        party_tax_code="9876543210",
        document_id="INV-001",
        document_type="SALES",
        amount=Decimal('0'),
        due_date=date(2026, 5, 15)
    )
    
    try:
        use_case.execute(dto)
        assert False, "Phải ném ValueError"
    except ValueError as e:
        assert "Số tiền công nợ phải lớn hơn 0" in str(e)