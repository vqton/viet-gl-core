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
    NoPhaiTraDaiHan, # <-- Thêm import
    VonChuSoHuu,
    TienVaCacKhoanTgTien, # <-- Thêm import
    ChiTietTaiKhoan,
    ThuyetMinhTaiSan,
    ThuyetMinhNguonVon,
    ThuyetMinhKetQua
)
from app.domain.models.journal_entry import JournalEntryLine
from app.domain.models.account import TaiKhoan, LoaiTaiKhoan
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.infrastructure.repositories.account_repository import AccountRepository
from app.application.services.journaling_service import JournalingService
from app.application.services.accounting_period_service import AccountingPeriodService

class ReportingService:
    def __init__(self, journal_entry_repo: JournalEntryRepository, account_repo: AccountRepository):
        self.journal_entry_repo = journal_entry_repo
        self.account_repo = account_repo
        # Danh sách tài khoản theo nhóm (dựa trên Phụ lục II TT99)
        # Danh sách này có thể được cấu hình trong tương lai qua MST-04 (Chính sách Kế toán)
        # self.tai_san_ngan_han_codes = [ ... ] # Không còn cần thiết nếu có logic phân loại
        # self.tai_san_dai_han_codes = [ ... ]
        # ... (các danh sách khác cũng tương tự)

    def _tinh_so_du_va_phan_loai_tai_khoan(self, ky_hieu: str, ngay_lap: date) -> Tuple[Dict[str, Decimal], Dict[str, LoaiTaiKhoan]]:
        """
        Core logic: Tính số dư cuối kỳ cho từng tài khoản và phân loại tài khoản.
        Đây là phương thức trung tâm để tính toán dữ liệu cho các báo cáo.
        Trả về:
        - so_du_tai_khoan: Dict ánh xạ mã tài khoản -> số dư cuối kỳ (theo nguyên tắc kế toán: tài sản ghi Nợ, nợ/vốn ghi Có, trừ tài khoản loại trừ)
        - phan_loai_tai_khoan: Dict ánh xạ mã tài khoản -> loại tài khoản (TaiSan, NoPhaiTra, ...)
        """
        # Bước 1: Lấy tất cả các dòng bút toán đã được "Posted" (và trong kỳ nếu có logic kỳ)
        # (Giả sử repository có phương thức lọc theo trạng thái và kỳ)
        all_journal_lines = self.journal_entry_repo.get_all_journal_lines_posted() # Cần có logic lọc theo kỳ thực tế sau

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
                    # Xử lý tài khoản đặc biệt như 214 (Hao mòn), 229 (Dự phòng), 352 (Dự phòng phải trả), 521 (Giảm trừ doanh thu)
                    # thường có số dư bên Có, nên giống như nợ/vốn.
                    # 911 (Xác định KQKD) là tài khoản cuối kỳ, số dư cuối kỳ = 0 sau kết chuyển.
                    # Giả sử tài khoản loại trừ (contra) có dấu hiệuệu ngược lại.
                    # Nếu tài khoản loại trừ, số dư cuối kỳ = -(Nợ - Có) = - số dư thô
                    # Nếu không, thì theo loại tài khoản cha (ví dụ 911 là kết chuyển, số dư = 0).
                    # Trong thực tế, có thể cần kiểm tra cụ thể mã tài khoản.
                    # Ví dụ: nếu tk_ma == "214": so_du_tai_khoan[tk_ma] = - so_du_tho_tk
                    #       elif tk_ma == "911": so_du_tai_khoan[tk_ma] = 0 (sau kết chuyển)
                    #       else: so_du_tai_khoan[tk_ma] = - so_du_tho_tk (nếu là tài khoản loại trừ)
                    # Trong ví dụ này, ta giả sử các tài khoản trong LoaiTaiKhoan.KHAC (như 214, 229, 352, 521) là tài khoản loại trừ.
                    # Còn 911 sẽ được xử lý riêng khi tính báo cáo kết quả.
                    # Vì 214 là tài khoản loại trừ, số dư cuối kỳ của nó là -(Nợ - Có) = - số dư thô.
                    # Nếu số dư thô của 214 là âm (Có > Nợ), thì số dư cuối kỳ là dương (làm giảm tài sản).
                    # Nếu số dư thô của 214 là dương (Nợ > Có), thì số dư cuối kỳ là âm (rất hiếm).
                    # Ví dụ: Có 20000, Nợ 0 -> SD_thô = -20000 -> SD_đk = -(-20000) = 20000.
                    # Ví dụ: Có 0, Nợ 20000 -> SD_thô = 20000 -> SD_đk = -20000 (hiếm).
                    # => sd_tai_khoan[tk_ma] = - so_du_tho_tk # ĐÚNG cho tài khoản loại trừ
                    # Tuy nhiên, để tính tổng tài sản, ta cộng số dư cuối kỳ của 211 và 214.
                    # Nếu 211 có SD_đk = 200000 (dương), 214 có SD_đk = 20000 (dương vì là loại trừ), thì Tổng TS = 200000 + 20000 = 220000. -> SAI.
                    # Phải là: Tổng TS = 200000 - 20000 = 180000.
                    # Vậy, khi *tổng hợp* tài sản, ta cộng số dư cuối kỳ của 211 và *trừ* số dư cuối kỳ của 214.
                    # Hoặc, nếu SD_đk của 214 được tính là âm (ví dụ: SD_thô 214 = -20000, SD_đk = -(-20000) = 20000 -> cộng vào TS thì tăng).
                    # Cách đúng: SD_đk của 214 = SD_thô (nếu là loại trừ và SD_thô âm -> SD_đk âm -> cộng vào TS làm giảm).
                    # SD_thô 214 = 0 - 20000 = -20000.
                    # SD_đk 214 = SD_thô 214 = -20000. -> Cộng vào TS: 200000 + (-20000) = 180000. -> ĐÚNG.
                    # => Với tài khoản loại trừ: SD_đk = SD_thô.
                    # => Khi tổng hợp vào nhóm tài sản/nợ, ta cộng số dư cuối kỳ (có thể âm nếu là loại trừ).
                    so_du_tai_khoan[tk_ma] = so_du_tho_tk # Giữ nguyên số dư thô cho tài khoản loại trừ
                else:
                    # Nên log lại nếu có loại tài khoản không xác định
                    so_du_tai_khoan[tk_ma] = so_du_tho_tk # Mặc định
            else:
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
        return (
            tk_ma.startswith(("11", "12", "13", "15")) or
            tk_ma.startswith("242") # Chi phí trả trước ngắn hạn
        ) and tk_ma not in ["241"] # Loại trừ XDCB dở dang dài hạn

    def _phan_loai_tai_san_dai_han(self, tk_ma: str) -> bool:
        """
        Kiểm tra xem tài khoản có phải là tài sản dài hạn không.
        Dựa trên mã tài khoản và/hoặc loại tài khoản.
        """
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
        return (
            tk_ma.startswith(("31", "33")) and not tk_ma.startswith("3387") or # 3387 là dài hạn
            tk_ma in ["341", "342"] # Một số tài khoản dài hạn có phần ngắn hạn
        ) and tk_ma not in ["341", "342"] # Loại trừ tài khoản gốc dài hạn nếu có phần chi tiết ngắn hạn

    def _phan_loai_no_dai_han(self, tk_ma: str) -> bool:
        """
        Kiểm tra xem tài khoản có phải là nợ phải trả dài hạn không.
        Dựa trên mã tài khoản và/hoặc loại tài khoản.
        """
        return (
            tk_ma.startswith(("34", "3387")) # Vay & nợ thuê TC, Phải trả dài hạn khác, Phải trả khác dài hạn
        )

    def _phan_loai_von_chu_so_huu(self, tk_ma: str) -> bool:
        """
        Kiểm tra xem tài khoản có phải là vốn chủ sở hữu không.
        Dựa trên mã tài khoản và/hoặc loại tài khoản.
        """
        return tk_ma.startswith(("41", "42")) # 41, 42

    def lay_bao_cao_tinh_hinh_tai_chinh(self, ky_hieu: str, ngay_lap: date) -> BaoCaoTinhHinhTaiChinh:
        """
        Tính toán và trả về Báo cáo tình hình tài chính (B01-DN) cho kỳ đã cho.
        """
        # Gọi core logic để lấy số dư và phân loại
        so_du_tai_khoan, phan_loai_tai_khoan = self._tinh_so_du_va_phan_loai_tai_khoan(ky_hieu, ngay_lap)

        # --- Bắt đầu tính toán các chỉ tiêu cho B01-DN ---
        # Tính các nhóm: TaiSanNganHan, TaiSanDaiHan, NoPhaiTraNganHan, NoPhaiTraDaiHan, VonChuSoHuu

        # 1. TÀI SẢN
        # 1.1. Tài sản ngắn hạn
        tien_mat = so_du_tai_khoan.get("111", Decimal('0'))
        tien_gui_ngan_hang = so_du_tai_khoan.get("112", Decimal('0')) # Có thể cần tách 1121, 1122, 1123 nếu cần chi tiết
        tien_gui_ngan_han_khac = so_du_tai_khoan.get("113", Decimal('0')) # Ví dụ: vàng, bạc, kim khí quý, đá quý (nếu xem là ngắn hạn)
        cac_khoan_dau_tu_tai_chinh_ngan_han = so_du_tai_khoan.get("121", Decimal('0')) + so_du_tai_khoan.get("128", Decimal('0')) # 121, 128
        phai_thu_ngan_han = Decimal('0')
        for tk, so_du in so_du_tai_khoan.items():
            if self._phan_loai_tai_san_ngan_han(tk) and tk.startswith("13"): # 131, 133, 136, 138, 139
                phai_thu_ngan_han += so_du
        hang_ton_kho = Decimal('0')
        for tk, so_du in so_du_tai_khoan.items():
            if self._phan_loai_tai_san_ngan_han(tk) and tk.startswith("15"): # 151, 152, 153, 154, 155, 156, 157
                hang_ton_kho += so_du
        tai_san_ngan_han_khac = Decimal('0')
        for tk, so_du in so_du_tai_khoan.items():
            if self._phan_loai_tai_san_ngan_han(tk) and not tk.startswith(("11", "12", "13", "15")):
                tai_san_ngan_han_khac += so_du

        # 1.2. Tài sản dài hạn
        tai_san_co_dinh_huu_hinh = so_du_tai_khoan.get("211", Decimal('0')) + so_du_tai_khoan.get("214", Decimal('0')) # 211 - 214 (Hao mòn)
        tai_san_co_dinh_vo_hinh = so_du_tai_khoan.get("212", Decimal('0')) # 212
        dau_tu_tai_chinh_dai_han = so_du_tai_khoan.get("221", Decimal('0')) + so_du_tai_khoan.get("222", Decimal('0')) + so_du_tai_khoan.get("228", Decimal('0')) + so_du_tai_khoan.get("229", Decimal('0')) # 221, 222, 228, 229 (loại trừ)
        tai_san_dai_han_khac = Decimal('0')
        for tk, so_du in so_du_tai_khoan.items():
            if self._phan_loai_tai_san_dai_han(tk) and not tk.startswith(("21", "22")):
                tai_san_dai_han_khac += so_du

        # Tổng cộng tài sản
        tong_cong_tai_san = (tien_mat + tien_gui_ngan_hang + tien_gui_ngan_han_khac +
                             cac_khoan_dau_tu_tai_chinh_ngan_han +
                             phai_thu_ngan_han +
                             hang_ton_kho +
                             tai_san_ngan_han_khac +
                             tai_san_co_dinh_huu_hinh +
                             tai_san_co_dinh_vo_hinh +
                             dau_tu_tai_chinh_dai_han +
                             tai_san_dai_han_khac)

        # 2. NỢ PHẢI TRẢ & VỐN CHỦ SỞ HỮU
        # 2.1. Nợ phải trả
        # 2.1.1. Ngắn hạn
        phai_tra_nguoi_ban = so_du_tai_khoan.get("331", Decimal('0'))
        # ... (các khoản khác theo Phụ lục IV)
        phai_tra_nguoi_ban_khac = Decimal('0')
        for tk, so_du in so_du_tai_khoan.items():
            if self._phan_loai_no_ngan_han(tk) and tk.startswith("33") and tk != "331":
                phai_tra_nguoi_ban_khac += so_du # Có thể cần phân loại cụ thể hơn

        tong_no_phai_tra_ngan_han = phai_tra_nguoi_ban + phai_tra_nguoi_ban_khac # + các khoản khác

        # 2.1.2. Dài hạn
        vay_dai_han = so_du_tai_khoan.get("341", Decimal('0'))
        no_phai_tra_dai_han_khac = Decimal('0')
        for tk, so_du in so_du_tai_khoan.items():
            if self._phan_loai_no_dai_han(tk) and tk != "341":
                no_phai_tra_dai_han_khac += so_du # Có thể cần phân loại cụ thể hơn

        tong_no_phai_tra_dai_han = vay_dai_han + no_phai_tra_dai_han_khac

        # Tổng cộng nợ phải trả
        tong_cong_no_phai_tra = tong_no_phai_tra_ngan_han + tong_no_phai_tra_dai_han

        # 2.2. Vốn chủ sở hữu
        von_dieu_le = so_du_tai_khoan.get("411", Decimal('0'))
        loi_nhuan_sau_thue_chua_phan_phoi = so_du_tai_khoan.get("421", Decimal('0'))
        # ... (các khoản khác theo Phụ lục IV)
        tong_von_chu_so_huu = von_dieu_le + loi_nhuan_sau_thue_chua_phan_phoi # + các khoản khác

        # Tổng cộng nguồn vốn
        tong_cong_nguon_von = tong_cong_no_phai_tra + tong_von_chu_so_huu

        # Tạo và trả về DTO BaoCaoTinhHinhTaiChinh
        return BaoCaoTinhHinhTaiChinh(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            tai_san_ngan_han=TaiSanNganHan(
                tien_va_cac_khoan_tuong_duong_tien=TienVaCacKhoanTgTien(
                    tien_mat=tien_mat,
                    tien_gui_ngan_hang=tien_gui_ngan_hang,
                    tien_gui_ngan_han_khac=tien_gui_ngan_han_khac
                ),
                cac_khoan_dau_tu_tai_chinh_ngan_han=cac_khoan_dau_tu_tai_chinh_ngan_han,
                phai_thu_ngan_han=phai_thu_ngan_han,
                hang_ton_kho=hang_ton_kho,
                tai_san_ngan_han_khac=tai_san_ngan_han_khac,
            ),
            tai_san_dai_han=TaiSanDaiHan(
                tai_san_co_dinh_huu_hinh=tai_san_co_dinh_huu_hinh,
                tai_san_co_dinh_vo_hinh=tai_san_co_dinh_vo_hinh,
                dau_tu_tai_chinh_dai_han=dau_tu_tai_chinh_dai_han,
                tai_san_dai_han_khac=tai_san_dai_han_khac,
            ),
            tong_cong_tai_san=tong_cong_tai_san,
            no_phai_tra_ngan_han=NoPhaiTraNganHan(
                phai_tra_nguoi_ban=phai_tra_nguoi_ban,
                phai_tra_nguoi_ban_khac=phai_tra_nguoi_ban_khac,
            ),
            no_phai_tra_dai_han=NoPhaiTraDaiHan( # <-- Thêm dòng này
                vay_dai_han=vay_dai_han,
                no_phai_tra_dai_han_khac=no_phai_tra_dai_han_khac,
            ), # <-- Đảm bảo có dấu phẩy ở dòng trước nếu cần
            tong_cong_no_phai_tra=tong_cong_no_phai_tra, # <-- Thêm dòng này
            von_chu_so_huu=VonChuSoHuu(
                von_dieu_le=von_dieu_le,
                loi_nhuan_sau_thue_chua_phan_phoi=loi_nhuan_sau_thue_chua_phan_phoi,
                # ... (các chỉ tiêu khác nếu có)
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
        # Dựa trên Phụ lục IV TT99/2025/TT-BTC
        doanh_thu_thuan = so_du_tai_khoan.get("511", Decimal('0')) - so_du_tai_khoan.get("521", Decimal('0')) # 521 là giảm trừ doanh thu
        gia_von_hang_ban = so_du_tai_khoan.get("632", Decimal('0')) # hoặc 631 nếu là thương mại
        chi_phi_ban_hang = so_du_tai_khoan.get("641", Decimal('0'))
        chi_phi_quan_ly_doanh_nghiep = so_du_tai_khoan.get("642", Decimal('0'))

        loi_nhuan_gop = doanh_thu_thuan - gia_von_hang_ban
        loi_nhuan_tu_hoat_dong_kd = loi_nhuan_gop - chi_phi_ban_hang - chi_phi_quan_ly_doanh_nghiep
        # ... (các khoản khác: thu nhập tài chính, chi phí tài chính, thu nhập khác, chi phí khác)
        loi_nhuan_truoc_thue = loi_nhuan_tu_hoat_dong_kd # + thu_nhap_tc - chi_phi_tc + thu_khac - chi_khac
        thue_thu_nhap_doanh_nghiep = so_du_tai_khoan.get("821", Decimal('0')) # Chi phí thuế TNDN
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
            # ... (các chỉ tiêu khác)
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

    # (Có thể thêm các phương thức khác như cap_nhat_tai_khoan, xoa_tai_khoan nếu cần)