"""
Module: InventoryValuationService

Dịch vụ tính giá vốn hàng bán theo phương pháp FIFO, tuân thủ Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Giá vốn phải phản ánh giá thực tế xuất kho (Hướng dẫn TK 156 TT 99)
- Áp dụng nhất quán trong kỳ kế toán
"""

from typing import List
from decimal import Decimal, ROUND_HALF_UP
from domain.value_objects.inventory_transaction import InventoryTransaction


class InventoryValuationService:
    """Dịch vụ tính giá vốn hàng bán."""

    @staticmethod
    def calculate_cogs_fifo(
        inventory_layers: List[InventoryTransaction], quantity_to_sell: Decimal
    ) -> Decimal:
        """
        Tính giá vốn hàng bán theo phương pháp FIFO.

        Args:
            inventory_layers (List[InventoryTransaction]):
                Danh sách giao dịch tồn kho (theo thứ tự thời gian).
            quantity_to_sell (Decimal): Số lượng cần bán.

        Returns:
            Decimal: Tổng giá vốn thực tế (làm tròn 0 chữ số).

        Raises:
            ValueError: Nếu tồn kho không đủ để xuất.
        """
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
