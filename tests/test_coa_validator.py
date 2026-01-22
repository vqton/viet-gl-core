"""Test cases for purchase accounting rule."""

from unittest.mock import patch
import pytest
from datetime import datetime, date
from decimal import Decimal
from src.domain.value_objects.purchase_invoice import PurchaseInvoice, PurchaseLineItem
from src.domain.rules.purchase_accounting_rule import apply_purchase_rule


def test_purchase_with_freight_cost():
    """
    Test mua hàng có chi phí vận chuyển.

    Yêu cầu TT 99:
    - Hướng dẫn TK 156: Chi phí thu mua (vận chuyển) được ghi nhận vào TK 1562
    - TK 13311: Thuế GTGT được khấu trừ
    - TK 331: Phải trả người bán

    Expected:
        - Sinh 4 bút toán
        - Chi phí vận chuyển ghi vào TK 1562
    """
    invoice = PurchaseInvoice(
        invoice_number="PO-001",
        invoice_date=date(2026, 4, 15),
        supplier_tax_code="9876543210",
        supplier_name="NCC XYZ",
        line_items=[
            PurchaseLineItem("SKU01", "Điện thoại", Decimal("10"), Decimal("8000000"))
        ],
        freight_cost=Decimal("1000000"),
    )

    entries = apply_purchase_rule(
        invoice=invoice,
        document_id="PO-001",
        accounting_date=date(2026, 4, 15),
        accounting_period_code="2026-Q2",
        created_by="NV001",
        created_at=datetime.now(),
        approved_by="KT_TRUONG",
        approved_at=datetime.now(),
    )

    # Phải có 4 bút toán: 1561, 1562, 13311, 331
    assert len(entries) == 4

    # Kiểm tra chi phí vận chuyển vào TK 1562
    freight_entry = next(e for e in entries if e.account == "1562")
    assert freight_entry.debit == Decimal("1000000")
    assert freight_entry.description == "Chi phí vận chuyển hàng mua"


def test_purchase_without_freight_cost():
    """
    Test mua hàng không có chi phí vận chuyển.

    Yêu cầu TT 99:
    - Không phát sinh bút toán cho TK 1562 nếu không có chi phí thu mua

    Expected:
        - Chỉ sinh 3 bút toán (1561, 13311, 331)
    """
    invoice = PurchaseInvoice(
        invoice_number="PO-002",
        invoice_date=date(2026, 4, 16),
        supplier_tax_code="9876543210",
        supplier_name="NCC ABC",
        line_items=[
            PurchaseLineItem("SKU02", "Máy tính", Decimal("5"), Decimal("15000000"))
        ],
        # freight_cost = 0 (mặc định)
    )

    entries = apply_purchase_rule(
        invoice=invoice,
        document_id="PO-002",
        accounting_date=date(2026, 4, 16),
        accounting_period_code="2026-Q2",
        created_by="NV001",
        created_at=datetime.now(),
        approved_by="KT_TRUONG",
        approved_at=datetime.now(),
    )

    # Chỉ có 3 bút toán
    assert len(entries) == 3

    # Không có bút toán nào cho TK 1562
    account_codes = [e.account for e in entries]
    assert "1562" not in account_codes


def test_purchase_invalid_account():
    """
    Test lỗi khi tài khoản không hợp lệ.

    Yêu cầu TT 99:
    - Điều 11: Phải sử dụng đúng hệ thống tài khoản

    Expected:
        - Ném ValueError khi có tài khoản không tồn tại trong COA
    """
    invoice = PurchaseInvoice(
        invoice_number="PO-003",
        invoice_date=date(2026, 4, 17),
        supplier_tax_code="9876543210",
        supplier_name="NCC DEF",
        line_items=[
            PurchaseLineItem("SKU03", "Phụ kiện", Decimal("100"), Decimal("100000"))
        ],
    )

    # Mock hàm is_valid_account TRONG MODULE ĐƯỢC SỬ DỤNG BỞI purchase_accounting_rule
    with patch(
        "src.domain.rules.purchase_accounting_rule.is_valid_account"
    ) as mock_func:
        mock_func.return_value = False  # Giả lập tất cả tài khoản đều không hợp lệ

        with pytest.raises(ValueError, match="Tài khoản không hợp lệ"):
            apply_purchase_rule(
                invoice=invoice,
                document_id="PO-003",
                accounting_date=date(2026, 4, 17),
                accounting_period_code="2026-Q2",
                created_by="NV001",
                created_at=datetime.now(),
                approved_by="KT_TRUONG",
                approved_at=datetime.now(),
            )


def test_missing_supplier_module():
    """
    Test phát hiện thiếu module quản lý nhà cung cấp.

    Mục đích:
        - Nếu không có dữ liệu nhà cung cấp hợp lệ, hệ thống nên cảnh báo

    Expected:
        - Test này giả lập việc thiếu thông tin NCC → cần triển khai Party module
    """
    # Invoice hợp lệ nhưng thiếu thông tin NCC chi tiết
    invoice = PurchaseInvoice(
        invoice_number="PO-004",
        invoice_date=date(2026, 4, 18),
        supplier_tax_code="",  # Thiếu MST
        supplier_name="",
        line_items=[
            PurchaseLineItem("SKU04", "Hàng mẫu", Decimal("1"), Decimal("1000000"))
        ],
    )

    # Validate ở layer trên sẽ bắt lỗi, nhưng core logic vẫn chạy
    # → Phát hiện: cần tích hợp Party validation ở application layer
    entries = apply_purchase_rule(
        invoice=invoice,
        document_id="PO-004",
        accounting_date=date(2026, 4, 18),
        accounting_period_code="2026-Q2",
        created_by="NV001",
        created_at=datetime.now(),
        approved_by="KT_TRUONG",
        approved_at=datetime.now(),
    )

    assert len(entries) == 3
    # Ghi chú: Đây là điểm cần cải thiện → thêm validation ở application layer
