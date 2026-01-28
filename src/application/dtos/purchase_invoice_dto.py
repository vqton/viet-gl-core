"""
Module: Purchase Invoice DTO

DTO cho hóa đơn mua hàng từ UI/API.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List
from src.domain.value_objects.purchase_invoice import PurchaseLineItem


@dataclass
class PurchaseInvoiceDTO:
    """
    Dữ liệu hóa đơn mua hàng từ giao diện người dùng.

    Attributes:
        invoice_number (str): Số hóa đơn.
        invoice_date (date): Ngày hóa đơn.
        supplier_tax_code (str): MST nhà cung cấp.
        supplier_name (str): Tên nhà cung cấp.
        line_items (List[PurchaseLineItem]): Danh sách hàng hóa.
        freight_cost (Decimal): Chi phí vận chuyển.
        vat_rate (Decimal): Thuế suất GTGT.
    """

    invoice_number: str
    invoice_date: date
    supplier_tax_code: str
    supplier_name: str
    line_items: List[PurchaseLineItem]
    freight_cost: Decimal = Decimal("0")
    vat_rate: Decimal = Decimal("0.1")
