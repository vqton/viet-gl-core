# File: app/application/services/reporting_service.py

from decimal import Decimal
from datetime import date
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from app.domain.models.report import (
    BaoCaoTinhHinhTaiChinh,
    BaoCaoKetQuaHDKD,
    BaoCaoLuuChuyenTienTe,
    BaoCaoThuyetMinh,
    TaiSanNganHan,
    TaiSanDaiHan,
    NoPhaiTraNganHan,
    NoPhaiTraDaiHan,
    VonChuSoHuu,
    ChiTietTaiKhoan,
    ThuyetMinhTaiSan,
    ThuyetMinhNguonVon,
    ThuyetMinhKetQua
)
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.infrastructure.repositories.account_repository import AccountRepository
from app.domain.models.account import TaiKhoan, LoaiTaiKhoan
from app.domain.models.journal_entry import JournalEntryLine
from app.application.services.journaling_service import JournalingService
from app.application.services.accounting_period_service import AccountingPeriodService


class ReportingService:
    def __init__(self, journal_entry_repo: JournalEntryRepository, account_repo: AccountRepository):
        self.journal_entry_repo = journal_entry_repo
        self.account_repo = account_repo

    def _tinh_so_du_va_phan_loai_tai_khoan(self, ky_hieu: str, ngay_lap: date) -> Tuple[Dict[str, Decimal], Dict[str, LoaiTaiKhoan]]:
        """
        Core logic: Tính số dư cuối kỳ cho từng tài khoản và phân loại tài khoản.
        Đây là phương thức trung tâm để tính toán dữ liệu cho các báo cáo.
        Trả về:
        - so_du_tai_khoan: Dict ánh xạ mã tài khoản -> số dư cuối kỳ (theo nguyên tắc kế toán: tài sản ghi Nợ, nợ/vốn ghi Có)
        - phan_loai_tai_khoan: Dict ánh xạ mã tài khoản -> loại tài khoản (TaiSan, NoPhaiTra, ...)
        """
        # Bước 1: Lấy tất cả các dòng bút toán đã được "Posted"
        # (Giả sử repository có phương thức lọc theo trạng thái)
        # (Chưa có logic lọc theo kỳ cụ thể, cần bổ sung sau)
        all_journal_lines = self.journal_entry_repo.get_all_journal_lines_posted()

        # Bước 2: Tính số dư thô (Nợ - Có) cho từng tài khoản
        so_du_tho = {}
        for line in all_journal_lines:
            tk = line.so_tai_khoan
            if tk not in so_du_tho:
                so_du_tho[tk] = Decimal('0')
            so_du_tho[tk] += line.no - line.co

        # Bước 3: Lấy thông tin loại tài khoản cho từng mã tài khoản
        so_du_tai_khoan = {}
        phan_loai_tai_khoan = {}
        for tk_ma in so_du_tho.keys():
            tai_khoan_chi_tiet = self.account_repo.get_by_id(tk_ma)
            if tai_khoan_chi_tiet: # Kiểm tra nếu tài khoản tồn tại
                loai = tai_khoan_chi_tiet.loai_tai_khoan
                phan_loai_tai_khoan[tk_ma] = loai
                # Bước 4: Áp dụng logic để tính số dư cuối kỳ phù hợp với loại tài khoản
                so_du_tho_tk = so_du_tho[tk_ma]
                if loai in [LoaiTaiKhoan.TAI_SAN, LoaiTaiKhoan.CHI_PHI]:
                    # Số dư cuối kỳ = Nợ - Có (số dư thô)
                    so_du_tai_khoan[tk_ma] = so_du_tho_tk
                elif loai in [LoaiTaiKhoan.NO_PHAI_TRA, LoaiTaiKhoan.VON_CHU_SO_HUU, LoaiTaiKhoan.DOANH_THU]:
                    # Số dư cuối kỳ = Có - Nợ = -(Nợ - Có) = - số dư thô
                    so_du_tai_khoan[tk_ma] = -so_du_tho_tk
                elif loai == LoaiTaiKhoan.KHAC:
                    # Xử lý tài khoản đặc biệt như 214 (Hao mòn), 229 (Dự phòng), 352 (Dự phòng phải trả), 521 (Giảm trừ)
                    # Các tài khoản này thường là tài khoản loại trừ (contra account), có số dư bên Có.
                    # Tức là, nếu số dư thô (Nợ - Có) là âm, thì số dư cuối kỳ là dương.
                    # Tức là, số dư cuối kỳ = -(Nợ - Có) = - số dư thô
                    so_du_tai_khoan[tk_ma] = - so_du_tho_tk
                else:
                    # Nên log lại nếu có loại tài khoản không xác định
                    so_du_tai_khoan[tk_ma] = so_du_tho_tk # Mặc định
            else:
                # Tài khoản trong bút toán không tồn tại trong danh mục -> BÁO LỖI hoặc LOG
                # Bỏ qua hoặc gán số dư = 0
                print(f"Warning: Tài khoản {tk_ma} trong bút toán không tồn tại trong danh mục tài khoản.")
                so_du_tho[tk_ma] = Decimal('0')
                phan_loai_tai_khoan[tk_ma] = None
                so_du_tai_khoan[tk_ma] = Decimal('0')

        return so_du_tai_khoan, phan_loai_tai_khoan

    def _phan_loai_tai_san_ngan_han(self, tk_ma: str) -> bool:
        """
        Kiểm tra xem tài khoản có phải là tài sản ngắn hạn không.
        Dựa trên mã tài khoản và/hoặc loại tài khoản.
        """
        # Ví dụ đơn giản: Tài khoản bắt đầu bằng 11, 12, 13, 15 trừ 154, 155, 156, 157 là ngắn hạn.
        # 154 (Chi phí SXKD dở dang), 155 (Thành phẩm), 156 (Hàng hóa), 157 (Hàng gửi đi bán) cũng là ngắn hạn.
        # 241 (Xây dựng cơ bản dở dang), 242 (Chi phí trả trước) - dài hạn hay ngắn hạn?
        # 242 ngắn hạn, 241 dài hạn (theo Phụ lục IV).
        # 11 (Tiền), 12 (ĐTTC ngắn hạn), 13 (Phải thu ngắn hạn), 15 (Hàng tồn kho) -> Ngắn hạn
        # 154, 155, 156, 157 thuộc 15 -> Ngắn hạn
        # 242 -> Ngắn hạn
        # 241 -> Dai han
        return (
            tk_ma.startswith(("11", "12", "13", "15")) or
            tk_ma.startswith("242") or # Chi phí trả trước ngắn hạn
            tk_ma in ["2411", "2412"] # Xây dựng cơ bản dở dang (nếu là ngắn hạn theo quy định DN)
        ) and tk_ma not in ["241"] # Loại trừ 241 nếu coi là dài hạn

    def _phan_loai_tai_san_dai_han(self, tk_ma: str) -> bool:
        """
        Kiểm tra xem tài khoản có phải là tài sản dài hạn không.
        Dựa trên mã tài khoản và/hoặc loại tài khoản.
        """
        # Ví dụ: 21 (TSCĐ), 22 (ĐTTC dài hạn), 241 (XDCB dở dang dài hạn), 243 (Tài sản thuế TND hoãn lại)
        return (
            tk_ma.startswith(("21", "22")) or
            tk_ma.startswith("241") or # Xây dựng cơ bản dở dang (dài hạn)
            tk_ma == "243" # Tài sản thuế thu nhập hoãn lại
        )

    def _phan_loai_no_ngan_han(self, tk_ma: str) -> bool:
        """
        Kiểm tra xem tài khoản có phải là nợ phải trả ngắn hạn không.
        Dựa trên mã tài khoản và/hoặc loại tài khoản.
        """
        # Ví dụ: 311, 331, 333, 334, 335, 336, 337, 338 trừ 3387, 341, 343, 347, 352
        # 3387 là dài hạn
        # 341, 343, 347, 352 là dài hạn
        # 338 trừ 3387 là ngắn hạn
        # 352 là dự phòng ngắn hạn (theo Phụ lục IV, có thể là ngắn hạn)
        # 338 trừ 3387 -> ngắn hạn
        # 352 -> ngắn hạn (dự phòng phải trả ngắn hạn)
        return (
            tk_ma.startswith("33") and not tk_ma.startswith("3387") or # 33x trừ 3387
            tk_ma in ["311", "352"] # Vay ngắn hạn, Dự phòng ngắn hạn
        ) and tk_ma not in ["341", "343", "347"] # Loại trừ dài hạn

    def _phan_loai_no_dai_han(self, tk_ma: str) -> bool:
        """
        Kiểm tra xem tài khoản có phải là nợ phải trả dài hạn không.
        Dựa trên mã tài khoản và/hoặc loại tài khoản.
        """
        # Ví dụ: 341, 343, 347, 3387, một số phần của 338 nếu quy định DN
        return (
            tk_ma.startswith(("34", "3387")) # Vay & nợ thuê TC, Phải trả dài hạn, Phải trả khác dài hạn
        )

    def _phan_loai_von_chu_so_huu(self, tk_ma: str) -> bool:
        """
        Kiểm tra xem tài khoản có phải là vốn chủ sở hữu không.
        Dựa trên mã tài khoản và/hoặc loại tài khoản.
        """
        # Ví dụ: 41, 42
        return tk_ma.startswith(("41", "42"))

    def lay_bao_cao_tinh_hinh_tai_chinh(self, ky_hieu: str, ngay_lap: date) -> BaoCaoTinhHinhTaiChinh:
        """
        Tính toán và trả về Báo cáo tình hình tài chính (B01-DN) cho kỳ đã cho.
        """
        # Gọi core logic để lấy số dư và phân loại
        so_du_tai_khoan, phan_loai_tai_khoan = self._tinh_so_du_va_phan_loai_tai_khoan(ky_hieu, ngay_lap)

        # --- Bắt đầu tính toán các chỉ tiêu cho B01-DN ---
        # Tính các nhóm: TaiSanNganHan, TaiSanDaiHan, NoPhaiTraNganHan, NoPhaiTraDaiHan, VonChuSoHuu

        # 1. TÀI SẢN NGẮN HẠN
        tien_va_cac_khoan_tuong_duong_tien = Decimal('0')
        cac_khoan_dau_tu_tai_chinh_ngan_han = Decimal('0')
        phai_thu_ngan_han = Decimal('0')
        hang_ton_kho = Decimal('0')
        tai_san_ngan_han_khac = Decimal('0')

        for tk, so_du in so_du_tai_khoan.items():
            if self._phan_loai_tai_san_ngan_han(tk):
                if tk.startswith("11"): # 111, 112, 113
                    tien_va_cac_khoan_tuong_duong_tien += so_du
                elif tk.startswith("12"): # 121, 128
                    cac_khoan_dau_tu_tai_chinh_ngan_han += so_du
                elif tk.startswith("13"): # 131, 133, 136, 138, 139
                    phai_thu_ngan_han += so_du
                elif tk.startswith("15"): # 151, 152, 153, 154, 155, 156, 157
                    hang_ton_kho += so_du
                elif tk.startswith("242"): # 242
                    tai_san_ngan_han_khac += so_du # Chi phí trả trước ngắn hạn

        # 2. TÀI SẢN DÀI HẠN
        tai_san_dai_han_khac = Decimal('0')
        for tk, so_du in so_du_tai_khoan.items():
            if self._phan_loai_tai_san_dai_han(tk):
                if tk.startswith("21"): # 211, 212, 213, 214
                    tai_san_dai_han_khac += so_du # Gộp TSCĐ, ĐTTC dài hạn, XDCB dở dang, TS thuế hoãn lại
                elif tk.startswith("22"): # 221, 222, 228, 229
                    tai_san_dai_han_khac += so_du
                elif tk.startswith("241"): # 241
                    tai_san_dai_han_khac += so_du
                elif tk == "243": # 243
                    tai_san_dai_han_khac += so_du

        # 3. NỢ PHẢI TRẢ NGẮN HẠN
        phai_tra_nguoi_ban = Decimal('0')
        no_phai_tra_ngan_han_khac = Decimal('0')
        for tk, so_du in so_du_tai_khoan.items():
            if self._phan_loai_no_ngan_han(tk):
                if tk == "331": # Phải trả người bán
                    phai_tra_nguoi_ban = so_du
                else:
                    no_phai_tra_ngan_han_khac += so_du

        # 4. NỢ PHẢI TRẢ DÀI HẠN
        no_phai_tra_dai_han_khac = Decimal('0')
        for tk, so_du in so_du_tai_khoan.items():
            if self._phan_loai_no_dai_han(tk):
                no_phai_tra_dai_han_khac += so_du

        # 5. VỐN CHỦ SỞ HỮU
        von_dieu_le = Decimal('0')
        loi_nhuan_sau_thue_chua_phan_phoi = Decimal('0')
        von_chu_so_huu_khac = Decimal('0')
        for tk, so_du in so_du_tai_khoan.items():
            if self._phan_loai_von_chu_so_huu(tk):
                if tk == "411": # Vốn đầu tư của chủ sở hữu
                    von_dieu_le = so_du
                elif tk == "421": # Lợi nhuận sau thuế chưa phân phối
                    loi_nhuan_sau_thue_chua_phan_phoi = so_du
                else:
                    von_chu_so_huu_khac += so_du

        # Tính tổng cộng
        tong_cong_tai_san = (tien_va_cac_khoan_tuong_duong_tien + cac_khoan_dau_tu_tai_chinh_ngan_han +
                             phai_thu_ngan_han + hang_ton_kho + tai_san_ngan_han_khac +
                             tai_san_dai_han_khac)

        tong_cong_no_phai_tra = (phai_tra_nguoi_ban + no_phai_tra_ngan_han_khac + no_phai_tra_dai_han_khac)
        tong_cong_nguon_von = tong_cong_no_phai_tra + (von_dieu_le + loi_nhuan_sau_thue_chua_phan_phoi + von_chu_so_huu_khac)

        # Tạo và trả về DTO
        return BaoCaoTinhHinhTaiChinh(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            tai_san_ngan_han=TaiSanNganHan(
                tien_va_cac_khoan_tuong_duong_tien=tien_va_cac_khoan_tuong_duong_tien,
                cac_khoan_dau_tu_tai_chinh_ngan_han=cac_khoan_dau_tu_tai_chinh_ngan_han,
                phai_thu_ngan_han=phai_thu_ngan_han,
                hang_ton_kho=hang_ton_kho,
                # ... các chỉ tiêu khác nếu cần chi tiết hơn
            ),
            tai_san_dai_han=TaiSanDaiHan(
                tai_san_dai_han_khac=tai_san_dai_han_khac,
            ),
            tong_cong_tai_san=tong_cong_tai_san,
            no_phai_tra_ngan_han=NoPhaiTraNganHan(
                phai_tra_nguoi_ban=phai_tra_nguoi_ban,
                # ... các chỉ tiêu khác nếu cần chi tiết hơn
            ),
            no_phai_tra_dai_han=NoPhaiTraDaiHan(
                # ... các chỉ tiêu
            ),
            tong_cong_no_phai_tra=tong_cong_no_phai_tra,
            von_chu_so_huu=VonChuSoHuu(
                von_dieu_le=von_dieu_le,
                loi_nhuan_sau_thue_chua_phan_phoi=loi_nhuan_sau_thue_chua_phan_phoi,
                # ... các chỉ tiêu khác nếu cần chi tiết hơn
            ),
            tong_cong_nguon_von=tong_cong_nguon_von
        )

    # --- Các phương thức khác (B02-DN, B03-DN, B09-DN) sẽ được cập nhật tương tự ---
    def lay_bao_cao_ket_qua_hdkd(self, ky_hieu: str, ngay_lap: date) -> BaoCaoKetQuaHDKD:
        """
        Tính toán và trả về Báo cáo kết quả hoạt động kinh doanh (B02-DN).
        """
        # Gọi core logic
        so_du_tai_khoan, phan_loai_tai_khoan = self._tinh_so_du_va_phan_loai_tai_khoan(ky_hieu, ngay_lap)

        # Tính các chỉ tiêu B02-DN
        # Doanh thu
        doanh_thu_ban_hang = so_du_tai_khoan.get("511", Decimal('0'))
        doanh_thu_hoat_dong_tai_chinh = so_du_tai_khoan.get("512", Decimal('0')) # hoặc tài khoản cụ thể khác
        doanh_thu_khac = so_du_tai_khoan.get("711", Decimal('0'))
        doanh_thu_thuan = doanh_thu_ban_hang - so_du_tai_khoan.get("521", Decimal('0')) # 521 là giảm trừ

        # Chi phí
        gia_von_hang_ban = so_du_tai_khoan.get("632", Decimal('0')) # hoặc 631 nếu là thương mại
        chi_phi_ban_hang = so_du_tai_khoan.get("641", Decimal('0'))
        chi_phi_quan_ly_doanh_nghiep = so_du_tai_khoan.get("642", Decimal('0'))
        chi_phi_tai_chinh = Decimal('0') # Cần logic cụ thể cho chi phí tài chính (635?)
        chi_phi_khac = so_du_tai_khoan.get("811", Decimal('0'))

        loi_nhuan_gop = doanh_thu_thuan - gia_von_hang_ban
        loi_nhuan_tu_hoat_dong_kd = loi_nhuan_gop - chi_phi_ban_hang - chi_phi_quan_ly_doanh_nghiep
        loi_nhuan_truoc_thue = loi_nhuan_tu_hoat_dong_kd + (doanh_thu_hoat_dong_tai_chinh - chi_phi_tai_chinh) + (doanh_thu_khac - chi_phi_khac)
        thue_thu_nhap_doanh_nghiep = so_du_tai_khoan.get("821", Decimal('0'))
        loi_nhuan_sau_thue = loi_nhuan_truoc_thue - thue_thu_nhap_doanh_nghiep

        # Tạo và trả về DTO
        return BaoCaoKetQuaHDKD(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            doanh_thu_thuan=doanh_thu_thuan,
            gia_von_hang_ban=gia_von_hang_ban,
            loi_nhuan_gop=loi_nhuan_gop,
            chi_phi_ban_hang=chi_phi_ban_hang,
            chi_phi_quan_ly_doanh_nghiep=chi_phi_quan_ly_doanh_nghiep,
            # ... các chỉ tiêu khác
            loi_nhuan_truoc_thue=loi_nhuan_truoc_thue,
            thue_thu_nhap_doanh_nghiep=thue_thu_nhap_doanh_nghiep,
            loi_nhuan_sau_thue=loi_nhuan_sau_thue
        )

    def lay_bao_cao_luu_chuyen_tien_te(self, ky_hieu: str, ngay_lap: date) -> BaoCaoLuuChuyenTienTe:
        """
        Tính toán và trả về Báo cáo lưu chuyển tiền tệ (B03-DN).
        """
        # Gợi ý: Logic phức tạp hơn, cần phân loại dòng tiền từ HĐKD, HĐTC, HĐQT
        # Dựa trên tài khoản Nợ/Có trong bút toán và loại tài khoản.
        # (Cần phương thức lấy bút toán thô hoặc phân loại dòng tiền)
        # ... (Chưa hoàn thiện)
        pass

    def lay_bao_cao_thuyet_minh(self, ky_hieu: str, ngay_lap: date) -> BaoCaoThuyetMinh:
        """
        Tính toán và trả về Bản thuyết minh Báo cáo tài chính (B09-DN).
        """
        # Gợi ý: Lấy chi tiết từng tài khoản trong từng nhóm để trình bày
        # ... (Chưa hoàn thiện)
        pass