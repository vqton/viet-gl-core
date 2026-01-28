"""
Test cases for Return Purchase Use Case.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from src.application.dtos.purchase_return_dto import PurchaseReturnDTO
from src.domain.value_objects.purchase_invoice import PurchaseLineItem
from src.application.use_cases.return_purchase_use_case import ReturnPurchaseUseCase


def test_import_return_purchase_use_case():
    """Kiểm tra không có ImportError."""
    assert ReturnPurchaseUseCase is not None


def test_return_purchase_use_case_initialization():
    """Kiểm tra khởi tạo Use Case thành công."""
    journal_repo = Mock()
    use_case = ReturnPurchaseUseCase(journal_repo)
    assert use_case.journal_entry_repo == journal_repo


def test_return_purchase_use_case_executes_successfully():
    """Test toàn bộ luồng trả hàng mua."""
    journal_repo = Mock()

    # Tạo DTO đầu vào
    dto = PurchaseReturnDTO(
        return_number="RTN-P-001",
        return_date=date(2026, 4, 21),
        original_invoice_number="PO-001",
        supplier_name="NCC XYZ",
        supplier_tax_code="9876543210",
        line_items=[
            PurchaseLineItem("SKU01", "Điện thoại", Decimal("1"), Decimal("8000000"))
        ],
        freight_cost=Decimal("100000"),
        reason="Hàng lỗi",
    )

    # Thực thi
    use_case = ReturnPurchaseUseCase(journal_repo)
    entries = use_case.execute(dto, created_by="NV001")

    # Kiểm tra kết quả
    assert len(entries) == 4  # 1561, 1562, 13311, 331
    assert any(e.account == "1561" and e.credit == Decimal("8000000") for e in entries)
    assert any(e.account == "1562" and e.credit == Decimal("100000") for e in entries)
    assert any(e.account == "331" and e.debit > Decimal("0") for e in entries)

    # Kiểm tra đã gọi save()
    assert journal_repo.save.call_count == 4

    # Kiểm tra metadata điều chỉnh
    assert entries[0].is_reversal
    assert entries[0].original_entry_id == "PO-001"
    assert entries[0].adjustment_reason == "Hàng lỗi"
