"""
Test cases for Record Purchase Use Case.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from src.application.dtos.purchase_invoice_dto import PurchaseInvoiceDTO
from src.domain.value_objects.purchase_invoice import PurchaseLineItem
from src.application.use_cases.record_purchase_use_case import RecordPurchaseUseCase


def test_import_record_purchase_use_case():
    """Kiểm tra không có ImportError."""
    assert RecordPurchaseUseCase is not None


def test_record_purchase_use_case_initialization():
    """Kiểm tra khởi tạo Use Case thành công."""
    journal_repo = Mock()
    use_case = RecordPurchaseUseCase(journal_repo)
    assert use_case.journal_entry_repo == journal_repo


def test_record_purchase_use_case_executes_successfully():
    """Test toàn bộ luồng ghi nhận mua hàng."""
    journal_repo = Mock()

    # Tạo DTO đầu vào
    dto = PurchaseInvoiceDTO(
        invoice_number="PO-001",
        invoice_date=date(2026, 4, 15),
        supplier_tax_code="9876543210",
        supplier_name="NCC XYZ",
        line_items=[
            PurchaseLineItem("SKU01", "Điện thoại", Decimal("10"), Decimal("8000000"))
        ],
        freight_cost=Decimal("1000000"),
    )

    # Thực thi
    use_case = RecordPurchaseUseCase(journal_repo)
    entries = use_case.execute(dto, created_by="NV_MUAHANG")

    # Kiểm tra kết quả
    assert len(entries) == 4  # 1561, 1562, 13311, 331
    assert any(e.account == "1562" for e in entries)  # Có chi phí vận chuyển

    # Kiểm tra đã gọi save()
    assert journal_repo.save.call_count == 4
