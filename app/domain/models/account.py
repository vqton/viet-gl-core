# app/domain/models/account.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional


class LoaiTaiKhoan(str, Enum):
    TAI_SAN = "TAI_SAN"
    NO_PHAI_TRA = "NO_PHAI_TRA"
    VON_CHU_SO_HUU = "VON_CHU_SO_HUU"
    DOANH_THU = "DOANH_THU"
    CHI_PHI = "CHI_PHI"
    GIA_VON = "GIA_VON"
    THU_NHAP_KHAC = "THU_NHAP_KHAC"
    KHAC = "KHAC"


@dataclass
class TaiKhoan:
    so_tai_khoan: str
    ten_tai_khoan: str
    loai_tai_khoan: LoaiTaiKhoan
    cap_tai_khoan: int = 1
    so_tai_khoan_cha: Optional[str] = None
    la_tai_khoan_tong_hop: bool = True

    def __post_init__(self):
        # 1. Kiểm tra số tài khoản không trống
        if not self.so_tai_khoan or not self.so_tai_khoan.strip():
            raise ValueError("Số tài khoản không được để trống.")

        # 2. Kiểm tra tên tài khoản không trống
        if not self.ten_tai_khoan or not self.ten_tai_khoan.strip():
            raise ValueError("Tên tài khoản không được để trống.")

        # 3. Kiểm tra cấp tài khoản hợp lệ
        if self.cap_tai_khoan < 1 or self.cap_tai_khoan > 3:
            raise ValueError("Cấp tài khoản phải từ 1 đến 3.")

        # ✅ [TT99-PL2] Không cho phép tài khoản nhóm 9xx (ví dụ: 911)
        if self.so_tai_khoan.startswith("9"):
            raise ValueError(
                "TT99/2025/TT-BTC không có tài khoản nhóm 9xx. Không được tạo tài khoản bắt đầu bằng '9'."
            )

        # 4. Tài khoản cấp con phải có tài khoản cha
        if self.cap_tai_khoan > 1:
            if not self.so_tai_khoan_cha or not self.so_tai_khoan_cha.strip():
                raise ValueError(
                    f"Tài khoản cấp con (Cấp {self.cap_tai_khoan}) phải có tài khoản cha."
                )

    def __post_init__(self):
        self.kiem_tra_hop_le()

    def kiem_tra_hop_le(self):
        """
        [TT99-PL2] Kiểm tra tính hợp lệ của tài khoản theo Phụ lục II.
        """
        if not self.so_tai_khoan or not self.so_tai_khoan.strip():
            raise ValueError("Số tài khoản không được để trống.")
        if not self.ten_tai_khoan or not self.ten_tai_khoan.strip():
            raise ValueError("Tên tài khoản không được để trống.")
        if len(self.so_tai_khoan) > 20:
            raise ValueError("Số tài khoản không được vượt quá 20 ký tự.")
        if len(self.ten_tai_khoan) > 256:
            raise ValueError("Tên tài khoản không được vượt quá 256 ký tự.")
        if self.cap_tai_khoan < 1 or self.cap_tai_khoan > 3:
            raise ValueError(
                "Cấp tài khoản phải từ 1 đến 3 theo TT99/2025/TT-BTC Phụ lục II."
            )
        if self.cap_tai_khoan > 1:
            if not self.so_tai_khoan_cha or not self.so_tai_khoan_cha.strip():
                raise ValueError(
                    f"Tài khoản cấp con (Cấp {self.cap_tai_khoan}) phải có số tài khoản cha."
                )

        # ✅ [TT99-PL2] Cấm tài khoản nhóm 9xx
        if self.so_tai_khoan.startswith("9"):
            raise ValueError(
                "TT99/2025/TT-BTC không có tài khoản nhóm 9xx. Không được phép tạo tài khoản bắt đầu bằng '9'."
            )
