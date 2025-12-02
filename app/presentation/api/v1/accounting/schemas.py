# app/presentation/api/v1/accounting/schemas.py
from pydantic import BaseModel, Field

from app.domain.models.account import LoaiTaiKhoan
from app.domain.models.account import TaiKhoan as TaiKhoanDomain


class CreateTaiKhoanRequest(BaseModel):
    """
    Schema cho yêu cầu tạo tài khoản kế toán mới.
    [TT99-PL2] Theo Phụ lục II: tài khoản gồm 3-6 ký tự số, phân cấp.
    """

    so_tai_khoan: str = Field(
        ..., pattern=r'^\d{3,6}$', description="Số tài khoản: 3–6 chữ số"
    )
    ten_tai_khoan: str = Field(..., min_length=1, max_length=256)
    loai_tai_khoan: LoaiTaiKhoan
    cap_tai_khoan: int = Field(ge=1, le=3)
    so_tai_khoan_cha: str | None = Field(default=None)
    la_tai_khoan_tong_hop: bool = True

    def to_domain(self) -> 'TaiKhoanDomain':
        from app.domain.models.account import TaiKhoan

        return TaiKhoan(
            so_tai_khoan=self.so_tai_khoan,
            ten_tai_khoan=self.ten_tai_khoan,
            loai_tai_khoan=self.loai_tai_khoan,
            cap_tai_khoan=self.cap_tai_khoan,
            so_tai_khoan_cha=self.so_tai_khoan_cha,
            la_tai_khoan_tong_hop=self.la_tai_khoan_tong_hop,
        )


class UpdateTaiKhoanRequest(BaseModel):
    """
    Schema cho yêu cầu cập nhật tài khoản.
    Không cho phép thay đổi `so_tai_khoan` vì là PK.
    """

    ten_tai_khoan: str | None = Field(None, min_length=1, max_length=256)
    loai_tai_khoan: LoaiTaiKhoan | None = None
    cap_tai_khoan: int | None = Field(None, ge=1, le=3)
    so_tai_khoan_cha: str | None = Field(None)
    la_tai_khoan_tong_hop: bool | None = None
