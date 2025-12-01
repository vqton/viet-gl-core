from dataclasses import dataclass
from enum import Enum
from typing import Optional

# 1. Định nghĩa Enum LoaiTaiKhoan theo TT99/2025/TT-BTC và Phụ lục II
class LoaiTaiKhoan(str, Enum):  # 👈 PHẢI KẾ THỪA str
    """
    Enum đại diện cho các loại tài khoản kế toán theo TT99/2025/TT-BTC Phụ lục II.
    """
    TAI_SAN = "TAI_SAN"
    NO_PHAI_TRA = "NO_PHAI_TRA"
    VON_CHU_SO_HUU = "VON_CHU_SO_HUU"
    DOANH_THU = "DOANH_THU"
    THU_NHAP_KHAC = "THU_NHAP_KHAC"
    CHI_PHI = "CHI_PHI"
    GIA_VON = "GIA_VON"
    KHAC = "KHAC"

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
        if not self.so_tai_khoan or not self.so_tai_khoan.strip():
            raise ValueError("Số tài khoản không được để trống hoặc chỉ có khoảng trắng.")
        if not self.ten_tai_khoan or not self.ten_tai_khoan.strip():
            raise ValueError("Tên tài khoản không được để trống hoặc chỉ có khoảng trắng.")
        if len(self.so_tai_khoan) > 20:
            raise ValueError("Số tài khoản không được vượt quá 20 ký tự.")
        if len(self.ten_tai_khoan) > 256:
            raise ValueError("Tên tài khoản không được vượt quá 256 ký tự.")
        if self.cap_tai_khoan < 1 or self.cap_tai_khoan > 3:
            raise ValueError("Cấp tài khoản phải từ 1 đến 3 theo TT99/2025/TT-BTC Phụ lục II.")
        if self.cap_tai_khoan > 1:
            if not self.so_tai_khoan_cha or not self.so_tai_khoan_cha.strip():
                raise ValueError(f"Tài khoản cấp con (Cấp {self.cap_tai_khoan}) phải có số tài khoản cha.")

    def __post_init__(self):
        self.kiem_tra_hop_le()