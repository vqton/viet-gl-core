"""
Test cases for PurchaseInvoice value object.

Yêu cầu pháp lý:
- Luật Quản lý Thuế 2019: Hóa đơn phải có MST nhà cung cấp
- Thông tư 78/2021/TT-BTC: Định dạng hóa đơn điện tử
- Thông tư 99/2025/TT-BTC: Hướng dẫn TK 156 về chi phí thu mua

Mục tiêu test:
- Xác minh tính toán giá trị hàng hóa và thuế GTGT chính xác
- Kiểm tra xử lý chi phí vận chuyển
"""

from datetime import date
from decimal import Decimal
from src.domain.value_objects.purchase_invoice import PurchaseInvoice, PurchaseLineItem


def test_purchase_invoice_creation():
    """
    Test tạo hóa đơn mua hàng hợp lệ.

    Yêu cầu pháp lý:
    - Hóa đơn phải có thông tin nhà cung cấp đầy đủ

    Expected:
        - Tạo PurchaseInvoice thành công
        - Tính toán giá trị hàng hóa chính xác
    """
    line_items = [
        PurchaseLineItem("SKU01", "Điện thoại", Decimal("10"), Decimal("8000000")),
        PurchaseLineItem("SKU02", "Phụ kiện", Decimal("50"), Decimal("100000")),
    ]
    invoice = PurchaseInvoice(
        invoice_number="PO-001",
        invoice_date=date(2026, 4, 15),
        supplier_tax_code="9876543210",
        supplier_name="Cty ABC",
        line_items=line_items,
    )
    assert invoice.goods_value == Decimal("85000000")


def test_purchase_invoice_with_freight_cost():
    """
    Test hóa đơn mua hàng có chi phí vận chuyển.

    Yêu cầu TT 99:
    - Hướng dẫn TK 156: Chi phí thu mua được tính vào giá trị hàng hóa

    Expected:
        - freight_cost được lưu trữ đúng
        - Thuế GTGT tính trên tổng (hàng hóa + vận chuyển)
    """
    invoice = PurchaseInvoice(
        invoice_number="PO-002",
        invoice_date=date(2026, 4, 16),
        supplier_tax_code="9876543210",
        supplier_name="Cty XYZ",
        line_items=[
            PurchaseLineItem("SKU01", "Máy tính", Decimal("5"), Decimal("15000000"))
        ],
        freight_cost=Decimal("2000000"),
    )
    assert invoice.freight_cost == Decimal("2000000")
    assert invoice.vat_amount == Decimal("7700000")
