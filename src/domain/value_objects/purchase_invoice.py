"""
Module: PurchaseInvoice

Đại diện cho hóa đơn mua hàng hợp lệ theo Thông tư 78/2021/TT-BTC và Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Phải có MST nhà cung cấp (Luật Quản lý Thuế)
- Ngày hóa đơn là căn cứ ghi nhận hàng hóa (Điều 19 TT 99)
- Chi phí thu mua (vận chuyển) được tính vào giá trị hàng hóa (Hướng dẫn TK 156 TT 99)
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List


@dataclass(frozen=True)
class PurchaseLineItem:
    """
    Dòng hàng trên hóa đơn mua hàng.

    Attributes:
        sku (str): Mã hàng hóa.
        name (str): Tên hàng hóa.
        quantity (Decimal): Số lượng.
        unit_price (Decimal): Đơn giá (chưa bao gồm VAT).
    """

    sku: str
    name: str
    quantity: Decimal
    unit_price: Decimal


@dataclass(frozen=True)
class PurchaseInvoice:
    """
    Hóa đơn mua hàng hợp lệ.

    Attributes:
        invoice_number (str): Số hóa đơn theo quy định Bộ Tài chính.
        invoice_date (date): Ngày lập hóa đơn.
        supplier_tax_code (str): Mã số thuế nhà cung cấp (10 hoặc 14 số).
        supplier_name (str): Tên đầy đủ của nhà cung cấp.
        line_items (List[PurchaseLineItem]): Danh sách hàng hóa mua.
        freight_cost (Decimal): Chi phí vận chuyển, bốc dỡ (nếu có).
        vat_rate (Decimal): Tỷ lệ thuế GTGT (mặc định 10% = 0.1).
    """

    invoice_number: str
    invoice_date: date
    supplier_tax_code: str
    supplier_name: str
    line_items: List[PurchaseLineItem]
    freight_cost: Decimal = Decimal("0")
    vat_rate: Decimal = Decimal("0.1")

    @property
    def goods_value(self) -> Decimal:
        """
        Giá trị hàng hóa (chưa bao gồm VAT và chi phí thu mua).

        Công thức: Σ (số lượng × đơn giá)
        """
        return sum(item.quantity * item.unit_price for item in self.line_items)

    @property
    def vat_amount(self) -> Decimal:
        """
        Số thuế GTGT được khấu trừ.

        Công thức: (Giá trị hàng hóa + Chi phí thu mua) × Thuế suất
        """
        taxable_base = self.goods_value + self.freight_cost
        return taxable_base * self.vat_rate
