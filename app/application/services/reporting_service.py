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
    TienVaCacKhoanTgTien,
    ChiTietTaiKhoan,
    ThuyetMinhTaiSan,
    ThuyetMinhNguonVon,
    ThuyetMinhKetQua,
    ThuNhapKhac, # Thêm import nếu cần thiết
    ChiPhiKhac # Thêm import nếu cần thiết
)
from app.domain.models.journal_entry import JournalEntryLine
from app.domain.models.account import TaiKhoan, LoaiTaiKhoan
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.infrastructure.repositories.account_repository import AccountRepository
from app.application.services.journaling_service import JournalingService
from app.application.services.accounting_period_service import AccountingPeriodService # Cần import này

# Định nghĩa hướng ghi sổ mặc định (Số dư cuối kỳ Nợ (+) / Có (-))
# Tài sản: Dư Nợ (Debit), Nợ Phải Trả & Vốn CSH: Dư Có (Credit)
HUONG_GHI_SO_MAC_DINH: Dict[LoaiTaiKhoan, str] = {
    LoaiTaiKhoan.TAI_SAN: 'NO',
    LoaiTaiKhoan.CHI_PHI: 'NO',
    LoaiTaiKhoan.GIA_VON: 'NO',
    LoaiTaiKhoan.NO_PHAI_TRA: 'CO',
    LoaiTaiKhoan.VON_CHU_SO_HUU: 'CO',
    LoaiTaiKhoan.DOANH_THU: 'CO',
    LoaiTaiKhoan.KHAC: 'NO', # Mặc định là NO, cần xem xét cụ thể cho từng tài khoản
}

class ReportingService:
    def __init__(
        self,
        journal_entry_repo: JournalEntryRepository,
        account_repo: AccountRepository,
        accounting_period_service: AccountingPeriodService # Đã thêm dependency mới
    ):
        self.journal_entry_repo = journal_entry_repo
        self.account_repo = account_repo
        self.accounting_period_service = accounting_period_service

    def _get_balance_at_date(self, so_tai_khoan: str, end_date: date) -> Tuple[Decimal, Decimal, Decimal]:
        """
        [LOGIC CỐT LÕI] Tính toán số dư đầu kỳ (01/01 năm tài chính hoặc đầu kỳ báo cáo),
        tổng phát sinh Nợ/Có, và số dư cuối kỳ cho một tài khoản đến ngày `end_date`.

        Hàm này là giả định, trong thực tế sẽ phức tạp hơn (cần số dư đầu năm, số dư chuyển kỳ).
        Hiện tại chỉ tính tổng phát sinh từ đầu năm đến end_date.

        Returns: (SoDuDauKy, PhatSinhNo, PhatSinhCo, SoDuCuoiKy)
        """
        # Giả định: Lấy tất cả bút toán đã "Posted" từ đầu năm đến end_date
        # (Để đơn giản, chúng ta sẽ bỏ qua số dư đầu năm và chỉ tính PS trong kỳ)
        
        # 1. Giả định ngày bắt đầu tính toán là 01/01 của năm đó.
        start_date = date(end_date.year, 1, 1)

        # 2. Lấy tất cả bút toán đã được Ghi sổ (Posted) trong khoảng thời gian
        posted_entries = self.journal_entry_repo.get_all_posted_in_range(start_date, end_date)
        
        tong_no = Decimal(0)
        tong_co = Decimal(0)
        
        # 3. Tổng hợp Nợ/Có từ các dòng bút toán
        for entry in posted_entries:
            for line in entry.lines:
                if line.so_tai_khoan == so_tai_khoan:
                    tong_no += line.no
                    tong_co += line.co
        
        # 4. Xác định số dư cuối kỳ
        tai_khoan = self.account_repo.get_by_id(so_tai_khoan)
        if not tai_khoan:
            raise ValueError(f"Tài khoản {so_tai_khoan} không tồn tại.")

        loai_tai_khoan = tai_khoan.loai_tai_khoan
        huong_mac_dinh = HUONG_GHI_SO_MAC_DINH.get(loai_tai_khoan, 'NO')

        so_du_dau_ky = Decimal(0) # GIẢ ĐỊNH: Chỉ tính PS trong kỳ
        so_du_cuoi_ky = so_du_dau_ky + (tong_no - tong_co) if huong_mac_dinh == 'NO' else so_du_dau_ky + (tong_co - tong_no)

        # Trả về kết quả: (SỐ DƯ ĐẦU KỲ, PHÁT SINH NỢ, PHÁT SINH CÓ, SỐ DƯ CUỐI KỲ)
        return (so_du_dau_ky, tong_no, tong_co, so_du_cuoi_ky)


    def lay_bao_cao_tinh_hinh_tai_chinh(self, ky_hieu: str, ngay_lap: date) -> BaoCaoTinhHinhTaiChinh:
        """
        Tính toán và trả về Báo cáo tình hình tài chính (B01-DN).
        """
        # 1. Tìm kỳ kế toán để xác định ngày bắt đầu/kết thúc
        ky_ke_toan = self.accounting_period_service.lay_ky_ke_toan_theo_ten(ky_hieu)
        if not ky_ke_toan:
             raise ValueError(f"Không tìm thấy kỳ kế toán với ký hiệu '{ky_hieu}'.")
        
        end_date = ky_ke_toan.ngay_ket_thuc # Báo cáo tại thời điểm cuối kỳ

        # 2. Lấy số liệu cho các chỉ tiêu:
        # Ví dụ: Lấy tiền và các khoản tương đương tiền (TK 111, 112, 113)
        # Báo cáo này cần số dư cuối kỳ, không cần Phát sinh Nợ/Có.
        
        so_du_111 = self._get_balance_at_date("111", end_date)[3] # Số dư cuối kỳ
        so_du_112 = self._get_balance_at_date("112", end_date)[3]
        
        tien_va_tg_tien = TienVaCacKhoanTgTien(
            tien_mat=so_du_111,
            tien_gui_ngan_hang=so_du_112,
            tien_gui_ngan_han_khac=Decimal(0) # Cần logic cho TK 113
        )
        
        tong_tien_va_tg_tien = tien_va_tg_tien.tien_mat + tien_va_tg_tien.tien_gui_ngan_hang + tien_va_tg_tien.tien_gui_ngan_han_khac

        tai_san_ngan_han = TaiSanNganHan(
            tien_va_cac_khoan_tuong_duong_tien=tong_tien_va_tg_tien,
            cac_khoan_dau_tu_tai_chinh_ngan_han=Decimal(0), # Cần logic cho TK 121, 128
            phai_thu_ngan_han=Decimal(0), # Cần logic cho TK 131, 138, ...
            hang_ton_kho=Decimal(0), # Cần logic cho TK 151, 152, 153, 155, 156
            tai_san_ngan_han_khac=Decimal(0) # Cần logic cho TK 141, 142, ...
        )

        # Giả định các phần còn lại là 0 để hoàn thành DTO
        tai_san_dai_han = TaiSanDaiHan(tai_san_co_dinh=Decimal(0))
        no_phai_tra_ngan_han = NoPhaiTraNganHan(phai_tra_nguoi_ban_ngan_han=Decimal(0))
        no_phai_tra_dai_han = NoPhaiTraDaiHan(phai_tra_dai_han_khac=Decimal(0))
        von_chu_so_huu = VonChuSoHuu(von_gop_cua_chu_so_huu=Decimal(0))

        # Tổng cộng
        tong_tai_san = (
            tai_san_ngan_han.tien_va_cac_khoan_tuong_duong_tien +
            tai_san_ngan_han.cac_khoan_dau_tu_tai_chinh_ngan_han +
            tai_san_ngan_han.phai_thu_ngan_han +
            tai_san_ngan_han.hang_ton_kho +
            tai_san_ngan_han.tai_san_ngan_han_khac +
            tai_san_dai_han.tai_san_co_dinh # Chỉ lấy 1 chỉ tiêu đại diện
        )
        
        tong_nguon_von = (
            no_phai_tra_ngan_han.phai_tra_nguoi_ban_ngan_han + 
            no_phai_tra_dai_han.phai_tra_dai_han_khac + 
            von_chu_so_huu.von_gop_cua_chu_so_huu
        )

        # Tạo và trả về DTO
        return BaoCaoTinhHinhTaiChinh(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            tai_san_ngan_han=tai_san_ngan_han,
            tai_san_dai_han=tai_san_dai_han,
            tong_tai_san=tong_tai_san,
            no_phai_tra_ngan_han=no_phai_tra_ngan_han,
            no_phai_tra_dai_han=no_phai_tra_dai_han,
            von_chu_so_huu=von_chu_so_huu,
            tong_nguon_von=tong_nguon_von
        )


    def lay_bao_cao_ket_qua_hoat_dong_kinh_doanh(self, ky_hieu: str, ngay_lap: date) -> BaoCaoKetQuaHDKD:
        """
        Tính toán và trả về Báo cáo kết quả hoạt động kinh doanh (B02-DN).
        """
        # Logic tính toán dựa trên các tài khoản Doanh thu (5xx, 7xx) và Chi phí (6xx, 8xx)
        
        # 1. Tìm kỳ kế toán để xác định ngày bắt đầu/kết thúc
        ky_ke_toan = self.accounting_period_service.lay_ky_ke_toan_theo_ten(ky_hieu)
        if not ky_ke_toan:
             raise ValueError(f"Không tìm thấy kỳ kế toán với ký hiệu '{ky_hieu}'.")
        
        start_date = ky_ke_toan.ngay_bat_dau
        end_date = ky_ke_toan.ngay_ket_thuc

        # Giả định: Tính tổng phát sinh trong kỳ từ start_date đến end_date
        
        # Lấy tổng phát sinh Có của TK 511 (Doanh thu bán hàng và cung cấp dịch vụ) trong kỳ
        ps_co_511 = self._get_balance_in_range("511", start_date, end_date)['co']
        # Lấy tổng phát sinh Nợ của TK 521 (Các khoản giảm trừ doanh thu) trong kỳ
        ps_no_521 = self._get_balance_in_range("521", start_date, end_date)['no']
        
        doanh_thu_thuan = ps_co_511 - ps_no_521
        
        # Lấy tổng phát sinh Nợ của TK 632 (Giá vốn hàng bán) trong kỳ
        ps_no_632 = self._get_balance_in_range("632", start_date, end_date)['no']
        gia_von_hang_ban = ps_no_632

        loi_nhuan_gop = doanh_thu_thuan - gia_von_hang_ban

        # Lấy tổng phát sinh Nợ của TK 641 (Chi phí bán hàng) trong kỳ
        chi_phi_ban_hang = self._get_balance_in_range("641", start_date, end_date)['no']
        # Lấy tổng phát sinh Nợ của TK 642 (Chi phí quản lý doanh nghiệp) trong kỳ
        chi_phi_quan_ly_doanh_nghiep = self._get_balance_in_range("642", start_date, end_date)['no']

        # Thu nhập và chi phí tài chính (TK 515, 635)
        thu_nhap_tai_chinh = self._get_balance_in_range("515", start_date, end_date)['co']
        chi_phi_tai_chinh = self._get_balance_in_range("635", start_date, end_date)['no']
        
        loi_nhuan_thuan_tu_hdkd = (
            loi_nhuan_gop + 
            thu_nhap_tai_chinh - 
            chi_phi_tai_chinh - 
            chi_phi_ban_hang - 
            chi_phi_quan_ly_doanh_nghiep
        )

        # Thu nhập và chi phí khác (TK 711, 811)
        thu_nhap_khac = self._get_balance_in_range("711", start_date, end_date)['co']
        chi_phi_khac = self._get_balance_in_range("811", start_date, end_date)['no']

        loi_nhuan_khac = thu_nhap_khac - chi_phi_khac
        
        loi_nhuan_truoc_thue = loi_nhuan_thuan_tu_hdkd + loi_nhuan_khac

        # Giả định thuế TNDN (TK 8211) là 20% lợi nhuận trước thuế (chỉ là ví dụ)
        thue_suat = Decimal('0.20')
        thue_thu_nhap_doanh_nghiep = loi_nhuan_truoc_thue * thue_suat if loi_nhuan_truoc_thue > 0 else Decimal(0)
        loi_nhuan_sau_thue = loi_nhuan_truoc_thue - thue_thu_nhap_doanh_nghiep

        # Tạo và trả về DTO
        return BaoCaoKetQuaHDKD(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            doanh_thu_thuan=doanh_thu_thuan,
            gia_von_hang_ban=gia_von_hang_ban,
            loi_nhuan_gop=loi_nhuan_gop,
            doanh_thu_hoat_dong_tai_chinh=thu_nhap_tai_chinh,
            chi_phi_tai_chinh=chi_phi_tai_chinh,
            chi_phi_ban_hang=chi_phi_ban_hang,
            chi_phi_quan_ly_doanh_nghiep=chi_phi_quan_ly_doanh_nghiep,
            loi_nhuan_thuan_tu_hoat_dong_kinh_doanh=loi_nhuan_thuan_tu_hdkd,
            thu_nhap_khac=thu_nhap_khac,
            chi_phi_khac=chi_phi_khac,
            loi_nhuan_khac=loi_nhuan_khac,
            loi_nhuan_truoc_thue=loi_nhuan_truoc_thue,
            thue_thu_nhap_doanh_nghiep=thue_thu_nhap_doanh_nghiep,
            loi_nhuan_sau_thue=loi_nhuan_sau_thue
        )
    
    # Hàm hỗ trợ cho Báo cáo KQHĐKD (chỉ tính phát sinh trong phạm vi ngày)
    def _get_balance_in_range(self, so_tai_khoan: str, start_date: date, end_date: date) -> Dict[str, Decimal]:
        """Tính tổng phát sinh Nợ và Có trong khoảng thời gian."""
        posted_entries = self.journal_entry_repo.get_all_posted_in_range(start_date, end_date)
        
        tong_no = Decimal(0)
        tong_co = Decimal(0)
        
        for entry in posted_entries:
            for line in entry.lines:
                if line.so_tai_khoan == so_tai_khoan:
                    tong_no += line.no
                    tong_co += line.co
        
        return {'no': tong_no, 'co': tong_co}


    def lay_bao_cao_luu_chuyen_tien_te(self, ky_hieu: str, ngay_lap: date) -> BaoCaoLuuChuyenTienTe:
        """
        Tính toán và trả về Báo cáo lưu chuyển tiền tệ (B03-DN).
        """
        # Gợi ý: Logic phức tạp hơn, cần phân loại dòng tiền từ HĐKD, HĐTC, HĐQT...
        # ... (Tạm thời giữ nguyên vì nó phức tạp)
        return BaoCaoLuuChuyenTienTe(
             ngay_lap=ngay_lap,
             ky_hieu=ky_hieu,
             luu_chuyen_tien_te_hdkd=None, # Cần tạo instance chi tiết
             luu_chuyen_tien_te_hdtc=None,
             luu_chuyen_tien_te_hdqt=None,
             tien_va_tuong_duong_tien_dau_ky=Decimal(0),
             tien_va_tuong_duong_tien_cuoi_ky=Decimal(0)
        )

    def lay_thuyet_minh_bao_cao_tai_chinh(self, ky_hieu: str, ngay_lap: date) -> BaoCaoThuyetMinh:
        """
        Tính toán và trả về Bản thuyết minh Báo cáo tài chính (B09-DN).
        """
        # Logic lấy chi tiết các tài khoản, chi tiết tài sản cố định, ...
        # ... (Tạm thời giữ nguyên)
        return BaoCaoThuyetMinh(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            chi_tiet_tai_khoan=None, # Cần List[ChiTietTaiKhoan]
            thuyet_minh_tai_san=None,
            thuyet_minh_nguon_von=None,
            thuyet_minh_ket_qua=None,
        )