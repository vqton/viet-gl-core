# File: app/domain/models/accounting_period.py

from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class KyKeToan:
    """
    Entity đại diện cho một kỳ kế toán.
    """
    id: Optional[int] = None
    ten_ky: str = "" # Ví dụ: "Q1-2025", "Năm 2025"
    ngay_bat_dau: date = date.today()
    ngay_ket_thuc: date = date.today()
    trang_thai: str = "Open" # "Open", "Locked"
    ghi_chu: str = ""

    def kiem_tra_hop_le(self):
        """
        Kiểm tra hợp lệ cho kỳ kế toán.
        """
        if not self.ten_ky or not self.ten_ky.strip():
            raise ValueError("Tên kỳ không được để trống.")
        if self.ngay_bat_dau > self.ngay_ket_thuc:
            raise ValueError("Ngày bắt đầu không thể sau ngày kết thúc.")
        if self.trang_thai not in ["Open", "Locked"]:
            raise ValueError("Trạng thái kỳ phải là 'Open' hoặc 'Locked'.")

    def __post_init__(self):
        self.kiem_tra_hop_le()