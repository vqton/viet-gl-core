# File: app/domain/models/report.py

from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from datetime import date

# --- Các Model cho Báo cáo tài chính ---
# Dữ liệu đầu ra từ ReportingService -> API -> Client

class BaoCaoTaiChinhBase(BaseModel):
    """Model cơ sở cho các báo cáo tài chính."""
    ngay_lap: date  # Ngày lập báo cáo
    ky_hieu: str    # Kỳ lập báo cáo (ví dụ: "Năm 2025", "Quý 4/2025")

# --- 1. B01-DN: Báo cáo tình hình tài chính ---
class TaiSanNganHan(BaseModel):
    tien_va_cac_khoan_tuong_duong_tien: Decimal
    cac_khoan_dau_tu_tai_chinh_ngan_han: Decimal
    phai_thu_ngan_han: Decimal
    hang_ton_kho: Decimal
    # ... các khoản khác theo mẫu B01-DN

class TaiSanDaiHan(BaseModel):
    tai_san_dai_han_khac: Decimal
    # ... các khoản khác theo mẫu B01-DN

class NoPhaiTraNganHan(BaseModel):
    phai_tra_nguoi_ban: Decimal
    # ... các khoản khác theo mẫu B01-DN

class NoPhaiTraDaiHan(BaseModel):
    # ... các khoản khác theo mẫu B01-DN
    pass

class VonChuSoHuu(BaseModel):
    von_dieu_le: Decimal
    loi_nhuan_sau_thue_chua_phan_phoi: Decimal
    # ... các khoản khác theo mẫu B01-DN

class BaoCaoTinhHinhTaiChinh(BaoCaoTaiChinhBase):
    tai_san_ngan_han: TaiSanNganHan
    tai_san_dai_han: TaiSanDaiHan
    tong_cong_tai_san: Decimal # Tính từ tổng tài sản ngắn hạn và dài hạn

    no_phai_tra_ngan_han: NoPhaiTraNganHan
    no_phai_tra_dai_han: NoPhaiTraDaiHan
    tong_cong_no_phai_tra: Decimal # Tính từ tổng nợ ngắn hạn và dài hạn

    von_chu_so_huu: VonChuSoHuu
    tong_cong_nguon_von: Decimal # Tính từ tổng nợ và vốn chủ sở hữu

# --- 2. B02-DN: Báo cáo kết quả hoạt động kinh doanh ---
class BaoCaoKetQuaHDKD(BaoCaoTaiChinhBase):
    doanh_thu_thuan: Decimal
    gia_von_hang_ban: Decimal
    loi_nhuan_gop: Decimal # doanh_thu_thuan - gia_von_hang_ban
    chi_phi_ban_hang: Decimal
    chi_phi_quan_ly_doanh_nghiep: Decimal
    # ... các khoản khác theo mẫu B02-DN
    loi_nhuan_truoc_thue: Decimal
    thue_thu_nhap_doanh_nghiep: Decimal
    loi_nhuan_sau_thue: Decimal

# --- 3. B03-DN: Báo cáo lưu chuyển tiền tệ (giả định phương pháp trực tiếp) ---
class LuuChuyenTienTeHDKD(BaseModel):
    tien_thu_tu_khach_hang: Decimal
    tien_chi_cho_nha_cung_cap_va_nhan_vien: Decimal
    # ... các khoản khác theo mẫu B03-DN

class LuuChuyenTienTeHDTT(BaseModel):
    # ... các khoản khác theo mẫu B03-DN
    pass

class LuuChuyenTienTeHDTC(BaseModel):
    # ... các khoản khác theo mẫu B03-DN
    pass

class BaoCaoLuuChuyenTienTe(BaoCaoTaiChinhBase):
    luu_chuyen_tien_te_hdkd: LuuChuyenTienTeHDKD
    luu_chuyen_tien_te_hdtc: LuuChuyenTienTeHDTT
    luu_chuyen_tien_te_hdqt: LuuChuyenTienTeHDTC
    tien_va_tuong_duong_tien_dau_ky: Decimal
    tien_va_tuong_duong_tien_cuoi_ky: Decimal

# --- 4. B09-DN: Bản thuyết minh Báo cáo tài chính (Model đơn giản hóa) ---
class ChiTietTaiKhoan(BaseModel):
    so_tai_khoan: str
    ten_tai_khoan: str
    so_du_dau_ky: Decimal
    phat_sinh_no: Decimal
    phat_sinh_co: Decimal
    so_du_cuoi_ky: Decimal

class ThuyetMinhTaiSan(BaseModel):
    # Chi tiết cho từng nhóm tài sản
    tai_san_ngan_han: List[ChiTietTaiKhoan]
    tai_san_dai_han: List[ChiTietTaiKhoan]

class ThuyetMinhNguonVon(BaseModel):
    # Chi tiết cho nợ phải trả và vốn chủ sở hữu
    no_phai_tra: List[ChiTietTaiKhoan]
    von_chu_so_huu: List[ChiTietTaiKhoan]

class ThuyetMinhKetQua(BaseModel):
    # Chi tiết cho doanh thu, chi phí
    doanh_thu: List[ChiTietTaiKhoan]
    chi_phi: List[ChiTietTaiKhoan]

class BaoCaoThuyetMinh(BaoCaoTaiChinhBase):
    tai_san: ThuyetMinhTaiSan
    nguon_von: ThuyetMinhNguonVon
    ket_qua: ThuyetMinhKetQua
    # ... các phần khác theo mẫu B09-DN