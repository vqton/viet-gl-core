# File: app/domain/models/journal_entry.py

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List, Optional
from app.domain.models.account import TaiKhoan, LoaiTaiKhoan # Import TaiKhoan để kiểm tra

@dataclass
class JournalEntryLine:
    """
    Value Object đại diện cho một dòng bút toán kế toán.
    """
    so_tai_khoan: str          # Số tài khoản ghi Nợ hoặc Có
    no: Decimal = Decimal(0)   # Số tiền ghi Nợ
    co: Decimal = Decimal(0)   # Số tiền ghi Có
    mo_ta: str = ""            # Mô tả cho dòng này (nếu cần chi tiết hơn)

    def __post_init__(self):
        """
        Kiểm tra hợp lệ cho dòng bút toán.
        """
        if self.no < 0 or self.co < 0:
            raise ValueError("Số tiền ghi Nợ và Có không thể âm.")
        if self.no > 0 and self.co > 0:
            raise ValueError("Một dòng bút toán chỉ được ghi Nợ hoặc Có, không đồng thời cả hai.")
        if self.no == 0 and self.co == 0:
             # Có thể cho phép dòng có số tiền = 0 nếu cần thiết, nhưng thường không nên
             # raise ValueError("Một dòng bút toán phải có số tiền ghi Nợ hoặc Có lớn hơn 0.")
             pass # Tạm thời bỏ qua nếu cả hai đều 0, nhưng khuyến khích không có dòng trống


@dataclass
class JournalEntry:
    """
    Entity đại diện cho một Bút toán kế toán.
    """
    id: Optional[int] = None          # ID tự sinh trong DB, có thể là None khi tạo mới
    ngay_ct: date = date.today()      # Ngày chứng từ
    so_phieu: str = ""                # Số hiệu chứng từ
    mo_ta: str = ""                   # Mô tả chung cho bút toán
    lines: List[JournalEntryLine] = None # Danh sách các dòng bút toán
    trang_thai: str = "Draft"         # Trạng thái: Draft, Posted, Locked

    def __post_init__(self):
        """
        Kiểm tra hợp lệ cho toàn bộ bút toán.
        """
        if self.lines is None:
            self.lines = []

        # Kiểm tra số lượng dòng
        if len(self.lines) == 0:
            raise ValueError("Bút toán phải có ít nhất một dòng.")

        # Kiểm tra số phiếu không trống
        if not self.so_phieu or not self.so_phieu.strip():
            raise ValueError("Số phiếu không được để trống.")

        # Kiểm tra cân bằng Nợ = Có
        self.kiem_tra_can_bang()

        # Kiểm tra tài khoản hợp lệ (có thể được thực hiện ở Service Layer sau)
        # self.kiem_tra_tai_khoan_ton_tai(tai_khoan_service) # Gọi từ service

    def kiem_tra_can_bang(self):
        """
        Kiểm tra nguyên tắc ghi sổ kép: Tổng Nợ = Tổng Có.
        """
        tong_no = sum(line.no for line in self.lines)
        tong_co = sum(line.co for line in self.lines)
        if not (tong_no == tong_co):
            raise ValueError(f"Bút toán không cân bằng: Tổng Nợ ({tong_no}) != Tổng Có ({tong_co})")

    # (Các phương thức khác như hach_toan(), ket_chuyen_tu_dong() sẽ được thêm sau)