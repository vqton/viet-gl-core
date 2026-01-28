"""
Module: Purchase Return DTO

DTO cho nghiệp vụ trả lại hàng mua.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List
from src.domain.value_objects.purchase_invoice import PurchaseLineItem


@dataclass
class PurchaseReturnDTO:
    """
    Dữ liệu trả lại hàng mua từ UI/API.

    Attributes:
        return_number (str): Số phiếu trả hàng.
        return_date (date): Ngày trả hàng.
        original_invoice_number (str): Số hóa đơn mua gốc.
        supplier_name (str): Tên nhà cung cấp.
        supplier_tax_code (str): MST nhà cung cấp.
        line_items (List[PurchaseLineItem]): Danh sách hàng trả lại.
        freight_cost (Decimal): Chi phí vận chuyển trả lại (nếu có).
        reason (str): Lý do trả hàng.
    """

    return_number: str
    return_date: date
    original_invoice_number: str
    supplier_name: str
    supplier_tax_code: str
    line_items: List[PurchaseLineItem]
    freight_cost: Decimal = Decimal("0")
    reason: str = ""
