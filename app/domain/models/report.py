from pydantic import BaseModel
from decimal import Decimal
from typing import List, Optional
from datetime import date

# --- Các Model cho Báo cáo tài chính (DTOs) theo TT99/2025/TT-BTC (Phụ lục IV) ---
# Dữ liệu đầu ra từ ReportingService -> API -> Client

# Sử dụng Decimal cho các giá trị tiền tệ để đảm bảo độ chính xác
# Default các giá trị là Decimal(0)

class BaoCaoTaiChinhBase(BaseModel):
    """Model cơ sở cho các báo cáo tài chính."""
    ngay_lap: date  # Ngày lập báo cáo
    ky_hieu: str    # Kỳ lập báo cáo (ví dụ: "Năm 2025", "Quý 4/2025")

# --- 1. B01-DN: Báo cáo tình hình tài chính (Balance Sheet) ---
# Các chỉ tiêu chi tiết hơn theo Phụ lục IV

# 1.1. TÀI SẢN (ASSETS)
class TienVaCacKhoanTgTien(BaseModel):
    """Mã số 110: Tiền và các khoản tương đương tiền"""
    tien_mat: Decimal = Decimal(0)
    tien_gui_ngan_hang: Decimal = Decimal(0)
    tien_dang_chuyen: Decimal = Decimal(0) # Thêm chỉ tiêu này nếu có
    tong_cong: Decimal = Decimal(0) # Tổng cộng 111 + 112 + 113 + ...

class TaiSanNganHan(BaseModel):
    """A. TÀI SẢN NGẮN HẠN (Mã số 100)"""
    tien_va_cac_khoan_tuong_duong_tien: TienVaCacKhoanTgTien
    cac_khoan_dau_tu_tai_chinh_ngan_han: Decimal = Decimal(0) # Mã số 120
    cac_khoan_phai_thu_ngan_han: Decimal = Decimal(0)          # Mã số 130
    hang_ton_kho: Decimal = Decimal(0)                       # Mã số 140
    tai_san_ngan_han_khac: Decimal = Decimal(0)             # Mã số 150
    tong_tai_san_ngan_han: Decimal = Decimal(0)              # Mã số 100

class TaiSanDaiHan(BaseModel):
    """B. TÀI SẢN DÀI HẠN (Mã số 200)"""
    tai_san_co_dinh_huu_hinh: Decimal = Decimal(0)       # Mã số 211
    tai_san_co_dinh_vo_hinh: Decimal = Decimal(0)        # Mã số 221
    bat_dong_san_dau_tu: Decimal = Decimal(0)             # Mã số 230
    cac_khoan_dau_tu_tai_chinh_dai_han: Decimal = Decimal(0) # Mã số 250
    tai_san_dai_han_khac: Decimal = Decimal(0)            # Mã số 260
    tong_tai_san_dai_han: Decimal = Decimal(0)             # Mã số 200

class TongTaiSan(BaseModel):
    """Tổng cộng Tài sản (Mã số 270 = 100 + 200)"""
    tai_san_ngan_han: TaiSanNganHan
    tai_san_dai_han: TaiSanDaiHan
    tong_cong_tai_san: Decimal = Decimal(0)              # Mã số 270

# 1.2. NGUỒN VỐN (LIABILITIES AND EQUITY)
class NoPhaiTraNganHan(BaseModel):
    """I. NỢ PHẢI TRẢ NGẮN HẠN (Mã số 300)"""
    vay_va_no_thue_tai_chinh_ngan_han: Decimal = Decimal(0)
    phai_tra_ngan_han_nguoi_ban: Decimal = Decimal(0)
    thue_va_cac_khoan_phai_nop_nha_nuoc: Decimal = Decimal(0)
    phai_tra_ngan_han_khac: Decimal = Decimal(0)
    tong_no_ngan_han: Decimal = Decimal(0)                   # Mã số 300

class NoPhaiTraDaiHan(BaseModel):
    """II. NỢ PHẢI TRẢ DÀI HẠN (Mã số 400)"""
    vay_va_no_thue_tai_chinh_dai_han: Decimal = Decimal(0)
    du_phong_phai_tra_dai_han: Decimal = Decimal(0)
    tong_no_dai_han: Decimal = Decimal(0)                   # Mã số 400

class VonChuSoHuu(BaseModel):
    """III. VỐN CHỦ SỞ HỮU (Mã số 500)"""
    von_dau_tu_cua_chu_so_huu: Decimal = Decimal(0)
    thang_du_von_co_phan: Decimal = Decimal(0)
    loi_nhuan_sau_thue_chua_phan_phoi: Decimal = Decimal(0)
    tong_von_chu_so_huu: Decimal = Decimal(0)                # Mã số 500

class TongNguonVon(BaseModel):
    """Tổng cộng Nguồn vốn (Mã số 430 = 300 + 400 + 500)"""
    no_phai_tra_ngan_han: NoPhaiTraNganHan
    no_phai_tra_dai_han: NoPhaiTraDaiHan
    von_chu_so_huu: VonChuSoHuu
    tong_cong_nguon_von: Decimal = Decimal(0)            # Mã số 430

class BaoCaoTinhHinhTaiChinh(BaoCaoTaiChinhBase):
    """B01-DN: Báo cáo tình hình tài chính (Balance Sheet)"""
    tai_san: TongTaiSan
    nguon_von: TongNguonVon
    # (Kiểm tra: tai_san.tong_cong_tai_san == nguon_von.tong_cong_nguon_von)


# --- 2. B02-DN: Báo cáo kết quả hoạt động kinh doanh (Income Statement) ---

class BaoCaoKetQuaHDKD(BaoCaoTaiChinhBase):
    """B02-DN: Báo cáo kết quả hoạt động kinh doanh (Income Statement)"""
    # 1. Doanh thu bán hàng và cung cấp dịch vụ (Mã số 01)
    doanh_thu_ban_hang: Decimal = Decimal(0)
    # 2. Các khoản giảm trừ doanh thu (Mã số 02) - Contra Revenue
    cac_khoan_giam_tru_doanh_thu: Decimal = Decimal(0)
    # 3. Doanh thu thuần về bán hàng và cung cấp dịch vụ (Mã số 10 = 01 - 02)
    doanh_thu_thuan: Decimal = Decimal(0)

    # 4. Giá vốn hàng bán (Mã số 11)
    gia_von_hang_ban: Decimal = Decimal(0)
    # 5. Lợi nhuận gộp về bán hàng và cung cấp dịch vụ (Mã số 20 = 10 - 11)
    loi_nhuan_gop: Decimal = Decimal(0)

    # 6. Doanh thu hoạt động tài chính (Mã số 21)
    doanh_thu_hoat_dong_tai_chinh: Decimal = Decimal(0)
    # 7. Chi phí tài chính (Mã số 22)
    chi_phi_tai_chinh: Decimal = Decimal(0)
    # 8. Chi phí bán hàng (Mã số 25)
    chi_phi_ban_hang: Decimal = Decimal(0)
    # 9. Chi phí quản lý doanh nghiệp (Mã số 26)
    chi_phi_quan_ly_doanh_nghiep: Decimal = Decimal(0)

    # 10. Lợi nhuận thuần từ hoạt động kinh doanh (Mã số 30 = 20 + 21 - 22 - 25 - 26)
    loi_nhuan_thuan_tu_hdkd: Decimal = Decimal(0)

    # 11. Thu nhập khác (Mã số 31)
    thu_nhap_khac: Decimal = Decimal(0)
    # 12. Chi phí khác (Mã số 32)
    chi_phi_khac: Decimal = Decimal(0)
    # 13. Lợi nhuận khác (Mã số 40 = 31 - 32)
    loi_nhuan_khac: Decimal = Decimal(0)

    # 14. Tổng lợi nhuận kế toán trước thuế (Mã số 50 = 30 + 40)
    tong_loi_nhuan_truoc_thue: Decimal = Decimal(0)
    # 15. Chi phí thuế thu nhập doanh nghiệp hiện hành (Mã số 51)
    chi_phi_thue_thu_nhap_doanh_nghiep_hien_hanh: Decimal = Decimal(0)
    # 16. Chi phí thuế thu nhập doanh nghiệp hoãn lại (Mã số 52)
    chi_phi_thue_thu_nhap_doanh_nghiep_hoan_lai: Decimal = Decimal(0)

    # 17. Lợi nhuận sau thuế thu nhập doanh nghiệp (Mã số 60 = 50 - 51 - 52)
    loi_nhuan_sau_thue: Decimal = Decimal(0)


# --- 3. B03-DN: Báo cáo lưu chuyển tiền tệ (Cash Flow Statement) ---
# Thường được lập theo phương pháp Gián tiếp (TT99 khuyến khích)

class LuuChuyenTienTeHDKD(BaseModel):
    """Lưu chuyển tiền từ Hoạt động kinh doanh (Mã số 20)"""
    loi_nhuan_truoc_thue: Decimal = Decimal(0)            # 01
    dieu_chinh_khau_hao_ts_co_dinh: Decimal = Decimal(0)   # 02
    dieu_chinh_cac_khoan_du_phong: Decimal = Decimal(0)     # 03
    dieu_chinh_lo_lai_chenh_lech_ty_gia: Decimal = Decimal(0) # 04
    tien_lai_phai_tra_chi_tra: Decimal = Decimal(0)          # 05
    # Các khoản điều chỉnh khác...
    tang_giam_cac_khoan_phai_thu: Decimal = Decimal(0)      # 06
    tang_giam_hang_ton_kho: Decimal = Decimal(0)           # 07
    tang_giam_cac_khoan_phai_tra: Decimal = Decimal(0)     # 08
    tien_chi_tra_lai_vay: Decimal = Decimal(0)             # 15
    tien_thue_thu_nhap_da_nop: Decimal = Decimal(0)        # 16
    luu_chuyen_tien_thuan_tu_hdkd: Decimal = Decimal(0)     # 20 (Tổng)

class LuuChuyenTienTeHDDT(BaseModel):
    """Lưu chuyển tiền từ Hoạt động đầu tư (Mã số 30)"""
    tien_chi_mua_sam_xay_dung_ts_dai_han: Decimal = Decimal(0) # 21
    tien_thu_thanh_ly_nhuong_ban_ts_dai_han: Decimal = Decimal(0) # 22
    tien_chi_cho_vay_mua_cac_cong_cu_no: Decimal = Decimal(0) # 24
    tien_thu_hoi_cho_vay_ban_lai_cac_cong_cu_no: Decimal = Decimal(0) # 25
    luu_chuyen_tien_thuan_tu_hddt: Decimal = Decimal(0)       # 30 (Tổng)

class LuuChuyenTienTeHDTC(BaseModel):
    """Lưu chuyển tiền từ Hoạt động tài chính (Mã số 40)"""
    tien_thu_tu_phat_hanh_co_phieu: Decimal = Decimal(0)       # 31
    tien_thu_tu_vay: Decimal = Decimal(0)                     # 32
    tien_chi_tra_goc_vay: Decimal = Decimal(0)                # 33
    tien_chi_tra_co_tuc_loi_nhuan: Decimal = Decimal(0)      # 36
    luu_chuyen_tien_thuan_tu_hdtc: Decimal = Decimal(0)      # 40 (Tổng)

class BaoCaoLuuChuyenTienTe(BaoCaoTaiChinhBase):
    """B03-DN: Báo cáo lưu chuyển tiền tệ (Cash Flow Statement)"""
    luu_chuyen_tien_te_hdkd: LuuChuyenTienTeHDKD
    luu_chuyen_tien_te_hddt: LuuChuyenTienTeHDDT
    luu_chuyen_tien_te_hdtc: LuuChuyenTienTeHDTC
    # Lưu chuyển tiền thuần trong kỳ (Mã số 50 = 20 + 30 + 40)
    luu_chuyen_tien_thuan_trong_ky: Decimal = Decimal(0)

    # Tiền và tương đương tiền đầu kỳ (Mã số 60)
    tien_va_tuong_duong_tien_dau_ky: Decimal = Decimal(0)
    # Ảnh hưởng của thay đổi tỷ giá hối đoái quy đổi ngoại tệ (Mã số 61)
    anh_huong_thay_doi_ty_gia: Decimal = Decimal(0)

    # Tiền và tương đương tiền cuối kỳ (Mã số 70 = 50 + 60 + 61)
    tien_va_tuong_duong_tien_cuoi_ky: Decimal = Decimal(0)


# --- 4. B09-DN: Bản thuyết minh Báo cáo tài chính (Model đơn giản hóa) ---
class ChiTietTaiKhoan(BaseModel):
    """Chi tiết về số dư và phát sinh của một tài khoản cụ thể"""
    so_tai_khoan: str
    ten_tai_khoan: str
    so_du_dau_ky_no: Decimal = Decimal(0) # Số dư đầu kỳ bên Nợ
    so_du_dau_ky_co: Decimal = Decimal(0) # Số dư đầu kỳ bên Có
    phat_sinh_no: Decimal = Decimal(0)
    phat_sinh_co: Decimal = Decimal(0)
    so_du_cuoi_ky_no: Decimal = Decimal(0) # Số dư cuối kỳ bên Nợ
    so_du_cuoi_ky_co: Decimal = Decimal(0) # Số dư cuối kỳ bên Có

class ThuyetMinhTaiSan(BaseModel):
    """Chi tiết thuyết minh về nhóm Tài sản (ví dụ: Hàng tồn kho, TSCĐ)"""
    tong_cong_thuyet_minh: Decimal = Decimal(0) # Tổng giá trị
    chi_tiet_tai_khoan: List[ChiTietTaiKhoan]
    ghi_chu_quan_trong: str = "Tóm tắt các chính sách kế toán liên quan đến Tài sản."

class ThuyetMinhNguonVon(BaseModel):
    """Chi tiết thuyết minh về nhóm Nguồn vốn (ví dụ: Nợ phải trả, Vốn CSH)"""
    tong_cong_thuyet_minh: Decimal = Decimal(0) # Tổng giá trị
    chi_tiet_tai_khoan: List[ChiTietTaiKhoan]
    ghi_chu_quan_trong: str = "Tóm tắt các chính sách kế toán liên quan đến Nguồn vốn."

class ThuyetMinhKetQua(BaseModel):
    """Chi tiết thuyết minh về nhóm Kết quả HĐKD (ví dụ: Doanh thu, Chi phí)"""
    tong_doanh_thu: Decimal = Decimal(0)
    tong_chi_phi: Decimal = Decimal(0)
    chi_tiet_tai_khoan: List[ChiTietTaiKhoan]
    ghi_chu_quan_trong: str = "Giải thích các biến động lớn trong doanh thu và chi phí."


class BaoCaoThuyetMinh(BaoCaoTaiChinhBase):
    """B09-DN: Bản thuyết minh Báo cáo tài chính (Notes to Financial Statements)"""
    # Các thông tin chung
    dac_diem_hoat_dong_cua_doanh_nghiep: str
    ky_ke_toan_va_don_vi_tien_te: str
    chuan_muc_ke_toan_ap_dung: str = "VAS và TT99/2025/TT-BTC"

    # Chi tiết thuyết minh theo các nhóm chính
    thuyet_minh_tai_san: ThuyetMinhTaiSan
    thuyet_minh_nguon_von: ThuyetMinhNguonVon
    thuyet_minh_ket_qua_hoat_dong_kinh_doanh: ThuyetMinhKetQua

    # Các thuyết minh khác
    thong_tin_giao_dich_voi_cac_ben_lien_quan: str = "Không có"
    cac_su_kien_sau_ngay_ket_thuc_ky_ke_toan: str = "Không có"
    # ... (các phần khác của thuyết minh)