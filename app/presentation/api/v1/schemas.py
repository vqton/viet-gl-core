# app/presentation/api/v1/schemas.py
from datetime import date
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field

# Import LoaiTaiKhoan Enum để dùng cho validation
from app.domain.models.account import LoaiTaiKhoan


# --- Schema cơ sở ---
class BaseSchema(BaseModel):
    """Schema cơ sở cho các DTO. Cho phép sử dụng Domain Enum."""

    class Config:
        # Cho phép các trường không phải Pydantic (như Enum từ Domain)
        # Bắt buộc phải có để Pydantic nhận diện đúng LoaiTaiKhoan
        use_enum_values = True
        from_attributes = True


# ====================================================================
# 1. Tài khoản Kế toán (TaiKhoan)
# ====================================================================


class TaiKhoanCreate(BaseSchema):
    """Schema cho việc tạo mới Tài khoản."""

    so_tai_khoan: str = Field(
        ..., max_length=20, description="Số tài khoản (Ví dụ: 111, 641)"
    )
    ten_tai_khoan: str = Field(
        ..., max_length=256, description="Tên tài khoản (Ví dụ: Tiền mặt)"
    )
    loai_tai_khoan: LoaiTaiKhoan
    cap_tai_khoan: int = Field(
        default=1, ge=1, le=9, description="Cấp tài khoản (1, 2, 3...)"
    )
    so_tai_khoan_cha: Optional[str] = Field(
        None, max_length=20, description="Số tài khoản cha (nếu có)"
    )
    la_tai_khoan_tong_hop: bool = Field(
        default=True,
        description="Là tài khoản tổng hợp (true) hay chi tiết (false)",
    )


class TaiKhoanRead(TaiKhoanCreate):
    """Schema cho việc đọc thông tin Tài khoản."""

    # Các trường đã định nghĩa ở TaiKhoanCreate là đủ cho việc hiển thị


# ====================================================================
# 2. Kỳ Kế toán (KyKeToan)
# ====================================================================


class KyKeToanCreate(BaseSchema):
    """Schema cho việc tạo mới Kỳ kế toán."""

    ten_ky: str = Field(
        ..., max_length=100, description="Ví dụ: 'Q4-2025', 'Năm 2026'"
    )
    ngay_bat_dau: date = Field(..., description="Ngày bắt đầu kỳ")
    ngay_ket_thuc: date = Field(..., description="Ngày kết thúc kỳ")
    ghi_chu: Optional[str] = Field(None, max_length=512)


class KyKeToanRead(KyKeToanCreate):
    """Schema cho việc đọc thông tin Kỳ kế toán."""

    id: int
    trang_thai: str = Field(
        ..., description="Trạng thái: 'Open' hoặc 'Locked'"
    )
    # Thừa kế các trường còn lại từ KyKeToanCreate


# ====================================================================
# 3. Bút toán Kế toán (JournalEntry)
# ====================================================================


class JournalEntryLineSchema(BaseSchema):
    """Schema cho một dòng Bút toán (Value Object)."""

    so_tai_khoan: str = Field(
        ..., max_length=20, description="Số tài khoản ghi Nợ hoặc Có"
    )
    no: Decimal = Field(
        Decimal(0), ge=Decimal(0), description="Số tiền ghi Nợ"
    )
    co: Decimal = Field(
        Decimal(0), ge=Decimal(0), description="Số tiền ghi Có"
    )
    mo_ta: Optional[str] = Field(
        None, max_length=256, description="Mô tả chi tiết dòng (tùy chọn)"
    )


class JournalEntryCreate(BaseSchema):
    """Schema cho việc tạo mới Bút toán."""

    ngay_ct: date = Field(..., description="Ngày chứng từ")
    so_phieu: str = Field(
        ..., max_length=50, description="Số hiệu chứng từ (phải là duy nhất)"
    )
    mo_ta: Optional[str] = Field(
        None, max_length=512, description="Mô tả chung cho bút toán"
    )
    lines: List[JournalEntryLineSchema] = Field(
        ...,
        min_length=2,
        description="Danh sách các dòng bút toán (ít nhất 2 dòng)",
    )


class JournalEntryRead(JournalEntryCreate):
    """Schema cho việc đọc thông tin Bút toán."""

    id: int
    trang_thai: str = Field(
        ..., description="Trạng thái: 'Draft', 'Posted', 'Locked'"
    )
    lines: List[JournalEntryLineSchema]  # Sử dụng lại dòng bút toán schema
    # Thừa kế các trường còn lại từ JournalEntryCreate


# ====================================================================
# 4. Báo cáo Tài chính (DTOs cho dữ liệu trả về)
# Sử dụng lại các DTOs từ Report Domain Model (vì chúng đã là Pydantic)
# Tuy nhiên, nếu muốn DTO API khác với DTO Domain, bạn sẽ định nghĩa lại ở đây.
# Hiện tại, ta sẽ sử dụng trực tiếp các model từ report.py như các Schema Read.
# ====================================================================
from app.domain.models.report import (
    BaoCaoKetQuaHDKD,
    BaoCaoLuuChuyenTienTe,
    BaoCaoThuyetMinh,
    BaoCaoTinhHinhTaiChinh,
)

# Đặt bí danh để chúng rõ ràng là các Schema cho API
BaoCaoTinhHinhTaiChinhRead = BaoCaoTinhHinhTaiChinh
BaoCaoKetQuaHDKDRead = BaoCaoKetQuaHDKD
BaoCaoLuuChuyenTienTeRead = BaoCaoLuuChuyenTienTe
BaoCaoThuyetMinhRead = BaoCaoThuyetMinh
