"""
Test cases for Return Sales Use Case.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from src.application.dtos.sales_return_dto import SalesReturnDTO
from src.domain.value_objects.sales_invoice import SalesLineItem
from src.application.use_cases.return_sales_use_case import ReturnSalesUseCase


def test_import_return_sales_use_case():
    """Kiểm tra không có ImportError."""
    assert ReturnSalesUseCase is not None


def test_return_sales_use_case_initialization():
    """Kiểm tra khởi tạo Use Case thành công."""
    journal_repo = Mock()
    use_case = ReturnSalesUseCase(journal_repo)
    assert use_case.journal_entry_repo == journal_repo


def test_return_sales_use_case_executes_successfully():
    """Test toàn bộ luồng trả hàng."""
    journal_repo = Mock()

    # Tạo DTO đầu vào
    dto = SalesReturnDTO(
        return_number="RTN-001",
        return_date=date(2026, 4, 20),
        original_invoice_number="INV-001",
        buyer_name="Cty ABC",
        buyer_tax_code="9876543210",
        line_items=[
            SalesLineItem("SKU01", "Điện thoại", Decimal("1"), Decimal("10000000"))
        ],
        reason="Hàng lỗi",
    )

    # Thực thi
    use_case = ReturnSalesUseCase(journal_repo)
    entries = use_case.execute(dto, created_by="NV001")

    # Kiểm tra kết quả
    assert len(entries) == 5
    assert entries[1].debit == Decimal("10000000")  # Giảm doanh thu (5212)
    assert entries[3].debit == Decimal("10000000")  # Nhập lại kho (156)

    # Kiểm tra đã gọi save()
    assert journal_repo.save.call_count == 5

    # Kiểm tra metadata điều chỉnh
    assert entries[0].is_reversal
    assert entries[0].original_entry_id == "INV-001"
    assert entries[0].adjustment_reason == "Hàng lỗi"
