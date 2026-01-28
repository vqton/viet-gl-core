"""
Module: Inventory Transaction

Giao dịch tồn kho theo Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Hướng dẫn TK 156: Phải theo dõi hàng hóa theo lô (nếu áp dụng đích danh)
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class InventoryTransaction:
    """
    Giao dịch tồn kho.

    Attributes:
        item_sku (str): Mã hàng hóa.
        quantity (Decimal): Số lượng.
        unit_cost (Decimal): Giá vốn đơn vị.
        transaction_date (date): Ngày giao dịch.
        type (str): Loại giao dịch ("IN" hoặc "OUT").
        lot_id (str): Mã lô hàng (bắt buộc nếu dùng đích danh, mặc định "").
    """

    item_sku: str
    quantity: Decimal
    unit_cost: Decimal
    transaction_date: date
    type: str  # "IN" or "OUT"
    lot_id: str = ""  # ← Thêm trường này
