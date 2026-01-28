"""
Module: Inventory Valuation Strategy

Hỗ trợ lựa chọn phương pháp tính giá vốn theo chính sách doanh nghiệp.
"""

from enum import Enum
from typing import List, Optional
from decimal import Decimal
from src.domain.value_objects.inventory_transaction import InventoryTransaction
from src.domain.rules.inventory_valuation_rules import (
    calculate_cogs_fifo,
    calculate_cogs_weighted_average,
    calculate_cogs_specific_identification,
)


class ValuationMethod(Enum):
    """Các phương pháp tính giá vốn theo TT 99."""

    FIFO = "fifo"
    WEIGHTED_AVERAGE = "weighted_average"
    SPECIFIC_IDENTIFICATION = "specific_identification"


def calculate_cogs(
    method: ValuationMethod,
    inventory_layers: List[InventoryTransaction],
    quantity_to_sell: Decimal,
    lot_ids: Optional[List[str]] = None,
) -> Decimal:
    """
    Tính giá vốn theo phương pháp được chọn.

    Args:
        method: Phương pháp tính giá vốn
        inventory_layers: Danh sách giao dịch tồn kho
        quantity_to_sell: Số lượng cần bán
        lot_ids: Danh sách lô hàng (chỉ dùng cho đích danh)

    Returns:
        Decimal: Tổng giá vốn thực tế
    """
    if method == ValuationMethod.FIFO:
        return calculate_cogs_fifo(inventory_layers, quantity_to_sell)
    elif method == ValuationMethod.WEIGHTED_AVERAGE:
        return calculate_cogs_weighted_average(inventory_layers, quantity_to_sell)
    elif method == ValuationMethod.SPECIFIC_IDENTIFICATION:
        if lot_ids is None:
            raise ValueError("Phải cung cấp lot_ids cho phương pháp đích danh")
        return calculate_cogs_specific_identification(
            inventory_layers, quantity_to_sell, lot_ids
        )
    else:
        raise ValueError(f"Phương pháp không được hỗ trợ: {method}")
