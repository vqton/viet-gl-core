"""
Test cases for purchase accounting rule.

Yêu cầu pháp lý:
- Thông tư 99/2025/TT-BTC:
  - Điều 19: Ghi nhận hàng hóa tại thời điểm nhận hàng
  - Hướng dẫn TK 156: Chi phí thu mua (vận chuyển) ghi vào TK 1562

Mục tiêu test:
- Xác minh sinh bút toán đúng theo nghiệp vụ mua hàng
- Kiểm tra xử lý chi phí vận chuyển
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from src.domain.value_objects.purchase_invoice import PurchaseInvoice, PurchaseLineItem
from src.domain.rules.purchase_accounting_rule import apply_purchase_rule


def test_purchase_with_freight_cost():
    """
    Test mua hàng có chi phí vận chuyển.

    Yêu cầu TT 99:
    - TK 1562: Chi phí thu mua hàng hóa
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
    assert len(entries) == 4
    assert any(e.account == "1562" for e in entries)


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
    assert len(entries) == 3
    assert not any(e.account == "1562" for e in entries)
