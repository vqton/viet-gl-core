"""
Module: Sales Return DTO

DTO cho nghiệp vụ hàng bán bị trả lại.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List
from src.domain.value_objects.sales_invoice import SalesLineItem


@dataclass
class SalesReturnDTO:
    """
    Dữ liệu hàng bán bị trả lại từ UI/API.

    Attributes:
        return_number (str): Số phiếu trả hàng.
        return_date (date): Ngày trả hàng.
        original_invoice_number (str): Số hóa đơn gốc.
        buyer_name (str): Tên khách hàng.
        buyer_tax_code (str): MST khách hàng.
        line_items (List[SalesLineItem]): Danh sách hàng trả lại.
        reason (str): Lý do trả hàng.
    """

    return_number: str
    return_date: date
    original_invoice_number: str
    buyer_name: str
    buyer_tax_code: str
    line_items: List[SalesLineItem]
    reason: str = ""
