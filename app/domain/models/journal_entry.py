from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List, Optional

# Value Object cho dòng bút toán
@dataclass
class JournalEntryLine:
    """
    [Nghiệp vụ] Value Object đại diện cho một dòng bút toán kế toán (Debit/Credit Line).
    Đây là đơn vị ghi nhận giao dịch vào một tài khoản cụ thể.
    """
    so_tai_khoan: str          # Số tài khoản bị ảnh hưởng (ghi Nợ hoặc Có)
    no: Decimal = Decimal(0)   # Số tiền ghi Nợ (Debit)
    co: Decimal = Decimal(0)   # Số tiền ghi Có (Credit)
    mo_ta: str = ""            # Mô tả chi tiết cho dòng này

    def __post_init__(self):
        """
        [Nghiệp vụ] Kiểm tra hợp lệ cho dòng bút toán.
        1. Số tiền không thể âm.
        2. Đảm bảo một dòng chỉ ghi Nợ HOẶC Có (nguyên tắc ghi sổ kép ở cấp độ dòng).
        """
        if self.no < 0 or self.co < 0:
            raise ValueError("Số tiền ghi Nợ và Có không thể âm.")
        if self.no > 0 and self.co > 0:
            raise ValueError("Một dòng bút toán chỉ được ghi Nợ hoặc Có, không đồng thời cả hai.")
        # Rule: Nếu cả hai đều bằng 0, tạm thời cho qua, nhưng thường nghiệp vụ sẽ yêu cầu > 0
        if self.no == 0 and self.co == 0:
             pass 

# Entity cho bút toán
@dataclass
class JournalEntry:
    """
    [Nghiệp vụ] Entity đại diện cho một Bút toán kế toán (Journal Entry).
    Đây là một chứng từ ghi nhận nghiệp vụ kinh tế phát sinh, tuân thủ nguyên tắc ghi sổ kép.
    """
    id: Optional[int] = None           # ID trong DB (khi tạo mới là None)
    ngay_ct: date = date.today()      # Ngày chứng từ (quan trọng để xác định kỳ kế toán)
    so_phieu: str = ""                # Số hiệu chứng từ (Duy nhất)
    mo_ta: str = ""                   # Mô tả chung cho bút toán
    lines: List[JournalEntryLine] = None # Danh sách các dòng bút toán (Value Object)
    trang_thai: str = "Draft"         # Trạng thái: Draft (Nháp), Posted (Đã ghi sổ), Locked (Khóa sổ)

    def kiem_tra_can_bang(self):
        """
        [Nghiệp vụ] Kiểm tra nguyên tắc ghi sổ kép (Double-entry principle): Tổng Nợ = Tổng Có.
        Đây là quy tắc quan trọng nhất của mọi bút toán kế toán.
        """
        tong_no = sum(line.no for line in self.lines)
        tong_co = sum(line.co for line in self.lines)
        
        # Sử dụng Decimal để so sánh chính xác tuyệt đối
        if tong_no != tong_co:
            raise ValueError(f"Bút toán không cân bằng. Tổng Nợ: {tong_no}, Tổng Có: {tong_co}.")
        
        # Kiểm tra chi tiết từng dòng
        for line in self.lines:
            line.__post_init__() # Đảm bảo từng dòng đã qua kiểm tra hợp lệ

    def __post_init__(self):
        """
        [Nghiệp vụ] Thực hiện kiểm tra hợp lệ cho toàn bộ bút toán khi khởi tạo.
        1. Đảm bảo danh sách dòng bút toán (lines) không rỗng.
        2. Đảm bảo số phiếu không trống.
        3. Yêu cầu bút toán phải cân bằng Nợ = Có (kiem_tra_can_bang).
        """
        if self.lines is None:
            self.lines = []

        # 1. Kiểm tra số lượng dòng
        if len(self.lines) == 0:
            raise ValueError("Bút toán phải có ít nhất một dòng.")

        # 2. Kiểm tra số phiếu không trống
        if not self.so_phieu or not self.so_phieu.strip():
            raise ValueError("Số phiếu không được để trống.")

        # 3. Kiểm tra cân bằng Nợ = Có
        self.kiem_tra_can_bang()

    def set_trang_thai(self, trang_thai_moi: str):
        """
        [Nghiệp vụ] Thiết lập trạng thái mới cho bút toán.
        Chỉ cho phép chuyển đổi giữa các trạng thái hợp lệ.
        """
        if trang_thai_moi not in ["Draft", "Posted", "Locked"]:
            raise ValueError(f"Trạng thái '{trang_thai_moi}' không hợp lệ.")
        self.trang_thai = trang_thai_moi