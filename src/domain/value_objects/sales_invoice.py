"""
Module: SalesInvoice

Đại diện cho hóa đơn bán hàng hợp lệ theo Thông tư 78/2021/TT-BTC và Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Phải có MST người bán/mua (Luật Quản lý Thuế)
- Ngày hóa đơn là căn cứ ghi nhận doanh thu (Điều 19 TT 99)
- Hàng khuyến mãi phải được phân bổ doanh thu (Hướng dẫn TK 511 TT 99)
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List


@dataclass(frozen=True)
class SalesLineItem:
    """
    Chi tiết dòng hàng trên hóa đơn.

    Attributes:
        sku (str): Mã hàng.
        name (str): Tên hàng.
        quantity (Decimal): Số lượng.
        unit_price (Decimal): Đơn giá.
        is_promotion (bool): Có phải hàng khuyến mãi không.
    """

    sku: str
    name: str
    quantity: Decimal
    unit_price: Decimal
    is_promotion: bool = False


@dataclass(frozen=True)
class SalesInvoice:
    """
    Hóa đơn bán hàng GTGT hợp lệ.

    Attributes:
        invoice_number (str): Số hóa đơn.
        invoice_date (date): Ngày lập hóa đơn.
        seller_tax_code (str): MST người bán.
        buyer_name (str): Tên khách hàng.
        buyer_tax_code (str): MST người mua.
        line_items (List[SalesLineItem]): Danh sách hàng hóa.
        vat_rate (Decimal): Tỷ lệ thuế GTGT.
    """

    invoice_number: str
    invoice_date: date
    seller_tax_code: str
    buyer_name: str
    buyer_tax_code: str
    line_items: List[SalesLineItem]
    vat_rate: Decimal = Decimal("0.1")

    @property
    def total_amount(self) -> Decimal:
        """Tổng thanh toán (chưa gồm VAT)."""
        return sum(item.quantity * item.unit_price for item in self.line_items)

    @property
    def revenue(self) -> Decimal:
        """Doanh thu chưa bao gồm VAT."""
        return self.total_amount

    @property
    def vat_amount(self) -> Decimal:
        """Số thuế GTGT phải nộp."""
        return self.total_amount * self.vat_rate
