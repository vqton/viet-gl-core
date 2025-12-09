# path: app/domain/models/account.py
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional

# Import DetailObjectType từ file journal_entry để xác định loại đối tượng chi tiết cần theo dõi
from app.domain.models.journal_entry import DetailObjectType


class LoaiTaiKhoan(Enum):
    """
    Định nghĩa loại tài khoản theo TT99 (Tài sản, Nguồn vốn, Doanh thu, Chi phí, Khác).
    Đây là phân loại căn cứ để xác định bản chất dư nợ/dư có.
    """

    TAI_SAN = auto()  # Loại 1, 2
    NGUON_VON = auto()  # Loại 3, 4
    DOANH_THU = auto()  # Loại 5, 7
    CHI_PHI = auto()  # Loại 6, 8
    KHAC = auto()  # Loại 0 (Tài khoản ngoài bảng)


@dataclass(frozen=True)
class TaiKhoan:
    """
    Mô hình Domain cho Tài Khoản Kế Toán, tuân thủ TT99/2025/TT-BTC.
    Dùng tiếng Việt không dấu cho thuộc tính, PascalCase cho tên Class.

    Thuộc tính 'required_detail_type' được thêm để thực thi Vấn đề 2 PM:
    Kiểm tra bắt buộc phải hạch toán kèm đối tượng chi tiết (VD: Khách hàng, Nhà cung cấp).
    """

    so_tai_khoan: str  # Ví dụ: '111', '1111', '11111'
    ten_tai_khoan: str
    loai_tai_khoan: LoaiTaiKhoan
    cap_tai_khoan: int = field(default=1)  # Cấp 1, 2, 3, 4, 5...
    so_tai_khoan_cha: Optional[str] = field(default=None)
    # la_tai_khoan_tong_hop giữ lại theo cấu trúc cũ, nhưng ưu tiên dùng has_children() của Repo cho nghiệp vụ
    la_tai_khoan_tong_hop: bool = field(default=True)

    # Danh sách các loại đối tượng chi tiết bắt buộc phải theo dõi khi hạch toán
    required_detail_type: List[DetailObjectType] = field(default_factory=list)

    def kiem_tra_hop_le(self):
        """
        Kiểm tra các ràng buộc cơ bản của Domain Model Tài Khoản (ví dụ: cấp tài khoản, quan hệ cha con).

        Raises:
            ValueError: Nếu tài khoản vi phạm các quy tắc ràng buộc cấp/cha con.
        """
        if not (1 <= self.cap_tai_khoan <= 5):
            raise ValueError("Cấp tài khoản phải nằm trong phạm vi 1 đến 5.")

        # Cảnh báo cho tài khoản 9xx (Kế toán quản trị)
        if self.so_tai_khoan.startswith("9"):
            print(
                f"Cảnh báo: Tài khoản {self.so_tai_khoan} thuộc nhóm 9xx (Kế toán quản trị) - không theo chuẩn Phụ lục II TT99."
            )

        # Tài khoản cấp 1 phải không có cha
        if self.cap_tai_khoan == 1 and self.so_tai_khoan_cha is not None:
            raise ValueError("Tài khoản cấp 1 không được có tài khoản cha.")

        # Tài khoản con phải bắt đầu bằng số tài khoản cha
        if self.so_tai_khoan_cha and not self.so_tai_khoan.startswith(
            self.so_tai_khoan_cha
        ):
            raise ValueError("Số tài khoản con phải bắt đầu bằng số tài khoản cha.")
