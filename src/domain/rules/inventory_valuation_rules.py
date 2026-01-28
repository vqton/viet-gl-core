"""
Module: Inventory Valuation Rules

Các quy tắc tính giá vốn hàng bán theo Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Hướng dẫn tại Tài khoản 156 TT 99:
  - Giá vốn phải phản ánh giá thực tế xuất kho
  - Phải áp dụng nhất quán một trong các phương pháp: FIFO, bình quân, thực tế đích danh

Phương pháp được hỗ trợ:
1. FIFO (First In, First Out)
2. Bình quân gia quyền cuối kỳ
3. Thực tế đích danh
"""

from typing import List, Optional
from decimal import Decimal, ROUND_HALF_UP
from src.domain.value_objects.inventory_transaction import InventoryTransaction


def calculate_cogs_fifo(
    inventory_layers: List[InventoryTransaction], quantity_to_sell: Decimal
) -> Decimal:
    """
    Tính giá vốn theo phương pháp FIFO (Nhập trước, xuất trước).

    Yêu cầu pháp lý:
    - Áp dụng cho hàng hóa có hạn sử dụng, công nghệ...

    Args:
        inventory_layers: Danh sách giao dịch tồn kho (từ cũ đến mới)
        quantity_to_sell: Số lượng cần bán

    Returns:
        Decimal: Tổng giá vốn thực tế
    """
    if quantity_to_sell <= 0:
        raise ValueError("Số lượng bán phải lớn hơn 0")

    total_available = sum(t.quantity for t in inventory_layers if t.type == "IN")
    if total_available < quantity_to_sell:
        raise ValueError("Tồn kho không đủ để xuất")

    cogs = Decimal("0")
    remaining = quantity_to_sell

    for layer in inventory_layers:
        if layer.type != "IN" or layer.quantity <= 0:
            continue
        if remaining <= 0:
            break

        take = min(remaining, layer.quantity)
        cogs += take * layer.unit_cost
        remaining -= take

    return cogs.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def calculate_cogs_weighted_average(
    inventory_layers: List[InventoryTransaction], quantity_to_sell: Decimal
) -> Decimal:
    """
    Tính giá vốn theo phương pháp bình quân gia quyền cuối kỳ.

    Yêu cầu pháp lý:
    - Áp dụng phổ biến cho DN thương mại, sản xuất

    Args:
        inventory_layers: Danh sách giao dịch tồn kho
        quantity_to_sell: Số lượng cần bán

    Returns:
        Decimal: Tổng giá vốn thực tế
    """
    if quantity_to_sell <= 0:
        raise ValueError("Số lượng bán phải lớn hơn 0")

    total_qty = sum(t.quantity for t in inventory_layers if t.type == "IN")
    total_value = sum(
        t.quantity * t.unit_cost for t in inventory_layers if t.type == "IN"
    )

    if total_qty <= 0:
        raise ValueError("Không có tồn kho để tính giá bình quân")

    avg_cost = total_value / total_qty
    cogs = avg_cost * quantity_to_sell

    return cogs.quantize(Decimal("1"), rounding=ROUND_HALF_UP)


def calculate_cogs_specific_identification(
    inventory_layers: List[InventoryTransaction],
    quantity_to_sell: Decimal,
    lot_ids: List[str],
) -> Decimal:
    """
    Tính giá vốn theo phương pháp thực tế đích danh.

    Yêu cầu pháp lý:
    - Áp dụng cho hàng hóa có giá trị cao, dễ nhận biết (ô tô, bất động sản...)
    - Phải theo dõi theo lô hàng cụ thể

    Args:
        inventory_layers: Danh sách giao dịch tồn kho
        quantity_to_sell: Số lượng cần bán
        lot_ids: Danh sách mã lô hàng cụ thể cần xuất

    Returns:
        Decimal: Tổng giá vốn thực tế

    Raises:
        ValueError: Nếu lô hàng không tồn tại hoặc số lượng không khớp
    """
    if quantity_to_sell <= 0:
        raise ValueError("Số lượng bán phải lớn hơn 0")

    if not lot_ids:
        raise ValueError("Phải cung cấp danh sách lô hàng cho phương pháp đích danh")

    # Lọc các giao dịch thuộc các lô được chọn
    selected_layers = [
        layer
        for layer in inventory_layers
        if layer.type == "IN" and layer.lot_id in lot_ids
    ]

    if not selected_layers:
        raise ValueError(f"Không tìm thấy lô hàng: {lot_ids}")

    total_selected_qty = sum(layer.quantity for layer in selected_layers)
    if total_selected_qty != quantity_to_sell:
        raise ValueError(
            f"Số lượng lô hàng ({total_selected_qty}) không khớp với số lượng bán ({quantity_to_sell})"
        )

    cogs = sum(layer.quantity * layer.unit_cost for layer in selected_layers)
    return cogs.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
