from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class KyKeToan:
    """
    Entity đại diện cho một kỳ kế toán (Accounting Period).
    Chứa các thuộc tính cơ bản và quy tắc hợp lệ của một kỳ kế toán.
    """
    id: Optional[int] = None
    ten_ky: str = "" # Tên định danh kỳ (Ví dụ: "Q1-2025", "Năm 2025")
    ngay_bat_dau: date = date.today() # Ngày bắt đầu của kỳ kế toán
    ngay_ket_thuc: date = date.today() # Ngày kết thúc của kỳ kế toán
    trang_thai: str = "Open" # Trạng thái của kỳ: "Open" (Mở), "Locked" (Đã khóa)
    ghi_chu: str = ""

    def kiem_tra_hop_le(self):
        """
        [Nghiệp vụ] Kiểm tra các ràng buộc cơ bản của Entity KyKeToan.
        1. Đảm bảo tên kỳ không trống.
        2. Đảm bảo ngày bắt đầu không được sau ngày kết thúc.
        3. Đảm bảo trạng thái kỳ chỉ là 'Open' hoặc 'Locked'.
        """
        if not self.ten_ky or not self.ten_ky.strip():
            raise ValueError("Tên kỳ không được để trống.")
        if self.ngay_bat_dau > self.ngay_ket_thuc:
            raise ValueError("Ngày bắt đầu không thể sau ngày kết thúc.")
        if self.trang_thai not in ["Open", "Locked"]:
            raise ValueError("Trạng thái kỳ phải là 'Open' hoặc 'Locked'.")

    def __post_init__(self):
        """
        Hàm được gọi sau khi khởi tạo để tự động thực hiện kiểm tra hợp lệ
        ngay khi đối tượng KyKeToan được tạo ra.
        """
        self.kiem_tra_hop_le()