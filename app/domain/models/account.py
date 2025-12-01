# app/domain/models/account.py

from dataclasses import dataclass
from enum import Enum
from typing import Optional

# 1. Định nghĩa Enum LoaiTaiKhoan theo TT99/2025/TT-BTC và Phụ lục II
class LoaiTaiKhoan(Enum):
    """
    Enum đại diện cho các loại tài khoản kế toán theo TT99/2025/TT-BTC Phụ lục II.
    """
    TAI_SAN = "Tai_San"               # Tài sản (1xx, 2xx)
    NO_PHAI_TRA = "No_Phai_Tra"       # Nợ phải trả (3xx)
    VON_CHU_SO_HUU = "Von_Chu_So_Huu" # Vốn chủ sở hữu (4xx)
    DOANH_THU = "Doanh_Thu"           # Doanh thu (511, 512, 515)
    THU_NHAP_KHAC = "Thu_Nhap_Khac"   # Thu nhập khác (711)
    CHI_PHI = "Chi_Phi"               # Chi phí (632, 641, 642, 635, 811)
    GIA_VON = "Gia_Von"               # Giá vốn hàng bán (632)
    KHAC = "Khac"                     # Dành cho tài khoản đặc biệt (nếu cần)

# 2. Định nghĩa Entity TaiKhoan sử dụng dataclass
@dataclass
class TaiKhoan:
    """
    Entity đại diện cho Tài khoản Kế toán theo TT99/2025/TT-BTC Phụ lục II.
    """
    so_tai_khoan: str
    ten_tai_khoan: str
    loai_tai_khoan: LoaiTaiKhoan
    cap_tai_khoan: int = 1
    so_tai_khoan_cha: Optional[str] = None
    la_tai_khoan_tong_hop: bool = True

    def kiem_tra_hop_le(self):
        """
        Kiểm tra hợp lệ dựa trên các quy tắc từ TT99/2025/TT-BTC.
        """
        # Kiểm tra không trống
        if not self.so_tai_khoan or not self.so_tai_khoan.strip():
            raise ValueError("Số tài khoản không được để trống hoặc chỉ có khoảng trắng.")
        if not self.ten_tai_khoan or not self.ten_tai_khoan.strip():
            raise ValueError("Tên tài khoản không được để trống hoặc chỉ có khoảng trắng.")

        # Kiểm tra độ dài
        if len(self.so_tai_khoan) > 20:
            raise ValueError("Số tài khoản không được vượt quá 20 ký tự.")
        if len(self.ten_tai_khoan) > 256:
            raise ValueError("Tên tài khoản không được vượt quá 256 ký tự.")

        # Kiểm tra cấp tài khoản (1-3 theo Phụ lục II)
        if self.cap_tai_khoan < 1 or self.cap_tai_khoan > 3:
            raise ValueError("Cấp tài khoản phải từ 1 đến 3 theo TT99/2025/TT-BTC Phụ lục II.")

        # Kiểm tra tài khoản cha nếu là cấp con
        if self.cap_tai_khoan > 1:
            if not self.so_tai_khoan_cha or not self.so_tai_khoan_cha.strip():
                raise ValueError(f"Tài khoản cấp con (Cấp {self.cap_tai_khoan}) phải có số tài khoản cha.")

    def __post_init__(self):
        """
        Hàm được gọi tự động sau khi __init__ để thực hiện kiểm tra hợp lệ.
        """
        self.kiem_tra_hop_le()