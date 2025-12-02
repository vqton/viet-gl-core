from dataclasses import dataclass, field
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import List, Optional

# Hằng số làm tròn tiền tệ (2 chữ số thập phân)
SCALE = Decimal("0.01")


@dataclass(frozen=True)
class JournalEntryLine:
    """
    Value Object: Một dòng trong bút toán kế toán.
    Tuân thủ TT99/2025/TT-BTC:
    - Gắn chứng từ gốc (Điều 8, 9, 10; Phụ lục I)
    - Hỗ trợ đa tiền tệ (Điều 4–6)
    - Mã dòng tiền (cho B03-DN – Phụ lục IV)
    """

    so_tai_khoan: str

    no: Decimal = Decimal("0")
    co: Decimal = Decimal("0")

    # --- Hỗ trợ đa tiền tệ (Điều 4–6) ---
    so_tien_goc: Optional[Decimal] = None
    don_vi_tien_te_goc: Optional[str] = None
    ty_gia: Optional[Decimal] = None

    # --- Gắn với chứng từ gốc (Điều 8, 9; Phụ lục I) ---
    so_chung_tu_goc: Optional[str] = None
    ngay_chung_tu_goc: Optional[date] = None
    loai_chung_tu: Optional[str] = None  # Ví dụ: '01-TT', '01-VT', '05-LĐTL'

    # --- Mô tả & phân loại dòng tiền (Phụ lục IV – B03-DN) ---
    mo_ta: Optional[str] = None
    ma_dong_tien: Optional[str] = None  # Ví dụ: 'HĐKD', 'HĐĐT', 'HĐTC'

    def __post_init__(self):
        # 1. Kiểm tra số tiền không âm
        if self.no < 0 or self.co < 0:
            raise ValueError("Số tiền Nợ/Có không thể âm.")

        # 2. Không được ghi cả Nợ và Có
        if self.no > 0 and self.co > 0:
            raise ValueError(
                "Mỗi dòng bút toán chỉ được ghi Nợ hoặc Có, không đồng thời cả hai."
            )

        # 3. Dòng bút toán phải có giá trị phát sinh
        if self.no == 0 and self.co == 0:
            raise ValueError(
                "Dòng bút toán phải có giá trị phát sinh (Nợ hoặc Có > 0)."
            )

        # 4. Kiểm tra logic đa tiền tệ (nếu có)
        if self.so_tien_goc is not None:
            if not self.don_vi_tien_te_goc:
                raise ValueError("Thiếu đơn vị tiền tệ gốc.")
            if self.ty_gia is None:
                raise ValueError("Thiếu tỷ giá chuyển đổi.")
            if self.so_tien_goc < 0:
                raise ValueError("Số tiền gốc không thể âm.")

            # Tính số tiền quy đổi và so sánh (làm tròn nhất quán)
            expected = (self.so_tien_goc * self.ty_gia).quantize(
                SCALE, rounding=ROUND_HALF_UP
            )
            actual = max(self.no, self.co).quantize(
                SCALE, rounding=ROUND_HALF_UP
            )
            if expected != actual:
                raise ValueError(
                    f"Số tiền quy đổi ({expected}) không khớp với Nợ/Có ({actual})."
                )


@dataclass
class JournalEntry:
    """
    Entity: Bút toán kế toán — chứng từ ghi nhận nghiệp vụ kinh tế.
    Tuân thủ TT99: phải cân bằng Nợ = Có, có số phiếu, ngày chứng từ, và ít nhất 2 dòng.
    """

    id: Optional[int] = None
    ngay_ct: date = field(default_factory=date.today)
    so_phieu: str = ""
    mo_ta: str = ""
    lines: List[JournalEntryLine] = field(default_factory=list)
    trang_thai: str = "Draft"  # Draft, Posted, Locked

    def __post_init__(self):
        # 1. Bắt buộc có ít nhất 2 dòng (tuân thủ nguyên tắc bút toán kép – TT99)
        if len(self.lines) < 2:
            raise ValueError(
                "Bút toán phải có ít nhất 2 dòng (một Nợ, một Có)."
            )

        # 2. Số phiếu không được trống
        if not self.so_phieu.strip():
            raise ValueError("Số phiếu không được để trống.")

        # 3. Trạng thái phải hợp lệ
        if self.trang_thai not in ("Draft", "Posted", "Locked"):
            raise ValueError(f"Trạng thái không hợp lệ: {self.trang_thai}")

        # 4. Kiểm tra cân bằng Nợ = Có (với làm tròn nhất quán)
        tong_no = sum(line.no for line in self.lines).quantize(
            SCALE, rounding=ROUND_HALF_UP
        )
        tong_co = sum(line.co for line in self.lines).quantize(
            SCALE, rounding=ROUND_HALF_UP
        )
        if tong_no != tong_co:
            raise ValueError(
                f"Bút toán không cân bằng. Tổng Nợ: {tong_no}, Tổng Có: {tong_co}."
            )

        if self.tong_no != self.tong_co:
            raise ValueError(
                f"Bút toán không cân bằng. Tổng Nợ: {self.tong_no}, Tổng Có: {self.tong_co}."
            )

    @property
    def tong_no(self) -> Decimal:
        return sum(line.no for line in self.lines).quantize(
            SCALE, rounding=ROUND_HALF_UP
        )

    @property
    def tong_co(self) -> Decimal:
        return sum(line.co for line in self.lines).quantize(
            SCALE, rounding=ROUND_HALF_UP
        )

    def set_trang_thai(self, trang_thai_moi: str):
        """Cập nhật trạng thái bút toán (chỉ cho phép giá trị hợp lệ)."""
        if trang_thai_moi not in ("Draft", "Posted", "Locked"):
            raise ValueError(f"Trạng thái không hợp lệ: {trang_thai_moi}")
        self.trang_thai = trang_thai_moi
