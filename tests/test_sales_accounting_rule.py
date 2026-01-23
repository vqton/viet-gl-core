"""
Test cases for sales accounting rule.

Yêu cầu pháp lý:
- Thông tư 99/2025/TT-BTC:
  - Điều 19: Ghi nhận doanh thu tại thời điểm giao hàng
  - Hướng dẫn TK 511: Xử lý hàng khuyến mãi

Mục tiêu test:
- Xác minh sinh bút toán bán hàng đúng theo TT 99
- Kiểm tra tính giá vốn thực tế (FIFO)
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from src.domain.value_objects.sales_invoice import SalesInvoice, SalesLineItem
from src.domain.value_objects.inventory_transaction import InventoryTransaction
from src.domain.rules.sales_accounting_rule import apply_sales_rule


def test_sales_rule_generates_correct_entries():
    """
    Test sinh bút toán bán hàng đúng theo TT 99.

    Yêu cầu TT 99:
    - Điều 19: Ghi nhận doanh thu tại thời điểm giao hàng
    - TK 5111: Doanh thu bán hàng hóa
    - TK 33311: Thuế GTGT đầu ra
    - TK 632/156: Giá vốn thực tế

    Expected:
        - Sinh 5 bút toán hợp lệ
        - Giá trị doanh thu = 20M, giá vốn = 14M
    """
    invoice = SalesInvoice(
        invoice_number="001",
        invoice_date=date(2026, 4, 15),
        seller_tax_code="0123456789",
        buyer_name="Cty ABC",
        buyer_tax_code="9876543210",
        line_items=[
            SalesLineItem("SKU01", "Điện thoại", Decimal("2"), Decimal("10000000"))
        ],
    )
    inventory = [
        InventoryTransaction(
            "SKU01", Decimal("5"), Decimal("7000000"), date(2026, 4, 1), "IN"
        )
    ]
    entries = apply_sales_rule(
        invoice=invoice,
        inventory_transactions=inventory,
        document_id="INV-001",
        accounting_date=date(2026, 4, 15),
        accounting_period_code="2026-Q2",
        created_by="NV001",
        created_at=datetime.now(),
        approved_by="KT_TRUONG",
        approved_at=datetime.now(),
    )
    assert len(entries) == 5
    assert entries[1].credit == Decimal("20000000")
    assert entries[3].debit == Decimal("14000000")
