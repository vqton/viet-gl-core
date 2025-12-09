# app/presentation/api/v1/schemas.py
"""
Schema chuẩn hóa cho API kế toán.
- Tuân thủ TT99/2025/TT-BTC.
- Validation nghiêm ngặt ở tầng API.
- Tách biệt hoàn toàn với domain model.
"""
from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

# Import enum từ domain để validation
from app.domain.models.account import LoaiTaiKhoan
from app.domain.models.journal_entry import DetailObjectType


# ====================================================================
# 1. TÀI KHOẢN KẾ TOÁN
# ====================================================================
class TaiKhoanBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    so_tai_khoan: str = Field(
        ...,
        pattern=r"^\d{3,6}$",
        description="Số tài khoản: 3–6 chữ số theo TT99",
    )
    ten_tai_khoan: str = Field(..., min_length=1, max_length=256)
    loai_tai_khoan: LoaiTaiKhoan
    cap_tai_khoan: int = Field(..., ge=1, le=5)
    so_tai_khoan_cha: Optional[str] = Field(None, pattern=r"^\d{3,6}$")
    la_tai_khoan_tong_hop: bool = True


class TaiKhoanCreate(TaiKhoanBase):
    pass


class TaiKhoanRead(TaiKhoanBase):
    pass


# ====================================================================
# 2. DÒNG BÚT TOÁN (Journal Entry Line)
# ====================================================================
class JournalEntryLineSchema(BaseModel):
    """
    [TT99-Đ10] Mỗi dòng bút toán phải có chứng từ gốc.
    """

    model_config = ConfigDict(from_attributes=True)

    so_tai_khoan: str = Field(..., pattern=r"^\d{3,6}$")
    no: Decimal = Field(..., ge=0, description="Số tiền ghi Nợ")
    co: Decimal = Field(..., ge=0, description="Số tiền ghi Có")

    # === BẮT BUỘC THEO TT99 ĐIỀU 10 ===
    so_chung_tu_goc: str = Field(
        ..., min_length=1, max_length=50, description="Số chứng từ gốc"
    )
    ngay_chung_tu_goc: date = Field(..., description="Ngày chứng từ gốc")

    # === Chi tiết bắt buộc (nếu tài khoản yêu cầu) ===
    detail_object_type: DetailObjectType = Field(default=DetailObjectType.NONE)
    detail_object_id: Optional[str] = Field(None, max_length=50)


# ====================================================================
# 3. BÚT TOÁN KẾ TOÁN (Journal Entry)
# ====================================================================
class JournalEntryCreate(BaseModel):
    """
    [TT99-Đ24] Bút toán phải cân bằng (Nợ = Có) và có chứng từ gốc.
    """

    model_config = ConfigDict(from_attributes=True)

    ngay_ct: date = Field(..., description="Ngày chứng từ")
    so_phieu: str = Field(
        ..., min_length=1, max_length=50, description="Số chứng từ"
    )
    mo_ta: Optional[str] = Field(None, max_length=512)
    lines: List[JournalEntryLineSchema] = Field(..., min_items=2)

    class Config:
        # Cho phép enum trả về giá trị string (ex: "KHACH_HANG")
        use_enum_values = True


class JournalEntryRead(JournalEntryCreate):
    id: int
    trang_thai: str = Field(..., pattern=r"^(Draft|Posted|Locked)$")


# ====================================================================
# 4. KỲ KẾ TOÁN
# ====================================================================
class KyKeToanCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ten_ky: str = Field(..., max_length=100)
    ngay_bat_dau: date
    ngay_ket_thuc: date
    ghi_chu: Optional[str] = Field(None, max_length=512)


class KyKeToanRead(KyKeToanCreate):
    id: int
    trang_thai: str = Field(..., pattern=r"^(Open|Locked)$")


# ====================================================================
# 5. BÁO CÁO TÀI CHÍNH (không cần schema riêng)
# ====================================================================
# Các báo cáo B01, B02, B03, B09 đã được định nghĩa trong domain dưới dạng Pydantic model
# → FastAPI có thể dùng trực tiếp làm response model.
# → Không cần định nghĩa lại ở đây để tránh trùng lặp.
