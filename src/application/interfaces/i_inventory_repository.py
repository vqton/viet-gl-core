"""
Module: Inventory Repository Interface

Định nghĩa hợp đồng truy xuất dữ liệu tồn kho.

Yêu cầu nghiệp vụ:
- Lấy lịch sử giao dịch tồn kho theo mã hàng
- Hỗ trợ tính giá vốn theo mọi phương pháp (FIFO, bình quân, đích danh)

Lưu ý:
- Đây là interface — không chứa logic triển khai
- Implementation sẽ nằm trong adapter layer (SQLAlchemy, MongoDB, v.v.)
"""

from typing import List
from src.domain.value_objects.inventory_transaction import InventoryTransaction


class IInventoryRepository:
    """
    Interface quản lý tồn kho.

    Methods:
        get_transactions_by_sku(sku: str) -> List[InventoryTransaction]:
            Lấy toàn bộ giao dịch tồn kho của một mã hàng.
    """

    def get_transactions_by_sku(self, sku: str) -> List[InventoryTransaction]:
        """
        Lấy danh sách giao dịch tồn kho theo mã hàng.

        Args:
            sku (str): Mã hàng hóa (ví dụ: "SKU01").

        Returns:
            List[InventoryTransaction]: Danh sách giao dịch theo thứ tự thời gian.

        Raises:
            NotImplementedError: Vì đây là interface.
        """
        raise NotImplementedError("Phải được triển khai trong adapter layer")
