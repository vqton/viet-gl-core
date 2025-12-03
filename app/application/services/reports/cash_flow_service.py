# app/application/services/reports/cash_flow_service.py
from datetime import date
from decimal import Decimal
from typing import List

from app.application.interfaces.journal_entry_repo import (
    JournalEntryRepositoryInterface,
)

# Giả định PerformanceService đã được định nghĩa
from app.application.services.reports.performance_service import (
    PerformanceService,
)
from app.domain.models.journal_entry import JournalEntryDomain
from app.domain.models.report import (
    BaoCaoLuuChuyenTienTe,
    LuuChuyenTienTeHDDT,
    LuuChuyenTienTeHDKD,
    LuuChuyenTienTeHDTC,
)

# Giả định: Các Domain Models/Interfaces khác đã được import chính xác


class CashFlowService:
    """
    Dịch vụ tạo Báo cáo Lưu chuyển Tiền tệ (B03-DN) theo phương pháp Gián tiếp.
    """

    def __init__(
        self,
        repo: JournalEntryRepositoryInterface,
        performance_service: PerformanceService,  # Dependency mới
    ):
        self.repo = repo
        self.performance_service = performance_service

    # --------------------------------------------------------
    # PHƯƠNG THỨC NỀN TẢNG
    # --------------------------------------------------------

    def _tinh_phat_sinh_tai_khoan(
        self, tk: str, loai: str, bd: date, kt: date
    ) -> Decimal:
        """
        Tính tổng phát sinh NỢ (loai='NO') hoặc CÓ (loai='CO') cho một tài khoản
        trong khoảng thời gian (bd, kt) từ các bút toán đã Posted.
        """
        all_entries: List[JournalEntryDomain] = (
            self.repo.get_all_posted_in_range(bd, kt)
        )

        tong_phat_sinh = Decimal(0)

        for entry in all_entries:
            for line in entry.lines:
                if line.so_tai_khoan == tk:
                    if loai == "NO":
                        tong_phat_sinh += line.no
                    elif loai == "CO":
                        tong_phat_sinh += line.co

        return tong_phat_sinh

    # --------------------------------------------------------
    # I. LƯU CHUYỂN TIỀN TỪ HOẠT ĐỘNG KINH DOANH (HĐKD)
    # --------------------------------------------------------

    def _tinh_loi_nhuan_truoc_thue(
        self, ky_hieu: str, ngay_lap: date, start: date, end: date
    ) -> Decimal:
        """
        I.01: Lợi nhuận trước thuế (Lấy từ Báo cáo B02-DN).
        """
        b02_report = self.performance_service.lay_bao_cao(
            ky_hieu=ky_hieu,
            ngay_lap=ngay_lap,
            ngay_bat_dau=start,
            ngay_ket_thuc=end,
        )
        # Giả định B02 model có thuộc tính loi_nhuan_truoc_thue (Mã số 21)
        return b02_report.loi_nhuan_truoc_thue

    def _tinh_dieu_chinh_khau_hao_ts_co_dinh(
        self, start: date, end: date
    ) -> Decimal:
        """
        I.02: Điều chỉnh Khấu hao tài sản cố định (TK 214). Phát sinh Có.
        """
        # TK 214 (Hao mòn TSCĐ) - Phát sinh CÓ là khấu hao tăng
        khau_hao = self._tinh_phat_sinh_tai_khoan(
            tk="214", loai="CO", bd=start, kt=end
        )
        return khau_hao

    def _tinh_dieu_chinh_du_phong(self, start: date, end: date) -> Decimal:
        """
        I.03: Điều chỉnh các khoản dự phòng (TK 2xx, 3xx, 159). Tính tổng thay đổi.
        Logic phức tạp, tạm thời lấy thay đổi số dư một số TK dự phòng chính.
        (Số dư Cuối kỳ - Số dư Đầu kỳ). Nếu tăng thì cộng, giảm thì trừ.
        """
        # Để đơn giản, giả định một giá trị mock cho đến khi logic Số dư được triển khai đầy đủ.
        # Logic thực tế cần tính: (SDCK TK dự phòng - SDĐK TK dự phòng)
        return Decimal("100000")  # MOCK

    def _tinh_lai_tien_vay_da_tra(self, start: date, end: date) -> Decimal:
        """
        I.06: Chi phí lãi vay (Chi tiền trả lãi vay trong kỳ) - Liên quan đến TK 111, 112.
        Tổng phát sinh CÓ TK 111, 112 đối ứng với TK 335, 341.
        Cách tính đơn giản: Tổng phát sinh NỢ TK 635 (Chi phí tài chính)
        """
        # Logic phức tạp. Tạm tính dựa trên TK Chi phí tài chính (635) hoặc lấy từ B02
        return Decimal("15000000")  # MOCK

    def _tinh_thay_doi_tai_san_phai_thu(
        self, start: date, end: date
    ) -> Decimal:
        """
        I.07: Tăng/giảm các khoản phải thu.
        (Phát sinh NỢ TK 131, 138, 141... - Phát sinh CÓ TK 131, 138, 141...)
        Tăng phải thu -> TRỪ khỏi Lợi nhuận (Tiền chưa về)
        Giảm phải thu -> CỘNG vào Lợi nhuận (Tiền đã về)
        """
        # Giả định: Tài khoản 131 (Phải thu khách hàng)
        ps_no = self._tinh_phat_sinh_tai_khoan(
            tk="131", loai="NO", bd=start, kt=end
        )
        ps_co = self._tinh_phat_sinh_tai_khoan(
            tk="131", loai="CO", bd=start, kt=end
        )
        # Tăng ròng phải thu
        tang_giam_rong = ps_no - ps_co

        return (
            tang_giam_rong.copy_negate()
        )  # Phải thu tăng (dương) thì cần TRỪ (âm) vào Lợi nhuận

    def _tinh_thay_doi_phai_tra(self, start: date, end: date) -> Decimal:
        """
        I.09: Tăng/giảm các khoản phải trả (trừ lãi vay, thuế thu nhập).
        (Phát sinh CÓ TK 331, 334, 338... - Phát sinh NỢ TK 331, 334, 338...)
        Tăng phải trả -> CỘNG vào Lợi nhuận (Tiền chưa chi)
        Giảm phải trả -> TRỪ khỏi Lợi nhuận (Tiền đã chi)
        """
        # Giả định: Tài khoản 331 (Phải trả người bán)
        ps_co = self._tinh_phat_sinh_tai_khoan(
            tk="331", loai="CO", bd=start, kt=end
        )
        ps_no = self._tinh_phat_sinh_tai_khoan(
            tk="331", loai="NO", bd=start, kt=end
        )
        # Tăng ròng phải trả
        tang_giam_rong = ps_co - ps_no

        return tang_giam_rong  # Phải trả tăng (dương) thì CỘNG vào Lợi nhuận

    # --------------------------------------------------------
    # PHƯƠNG THỨC CHÍNH: LẬP BÁO CÁO
    # --------------------------------------------------------

    def lay_bao_cao(
        self,
        ky_hieu: str,
        ngay_lap: date,
        ngay_bat_dau: date,
        ngay_ket_thuc: date,
    ) -> BaoCaoLuuChuyenTienTe:
        """
        Tính và tạo Báo cáo Lưu chuyển Tiền tệ (B03-DN).
        """
        start = ngay_bat_dau
        end = ngay_ket_thuc

        # --- TÍNH TOÁN HOẠT ĐỘNG KINH DOANH (I) ---

        # I.01: Lợi nhuận trước thuế
        loi_nhuan_truoc_thue = self._tinh_loi_nhuan_truoc_thue(
            ky_hieu, ngay_lap, start, end
        )

        # CÁC KHOẢN ĐIỀU CHỈNH
        khau_hao = self._tinh_dieu_chinh_khau_hao_ts_co_dinh(start, end)
        du_phong = self._tinh_dieu_chinh_du_phong(start, end)
        lai_tien_vay_da_tra = self._tinh_lai_tien_vay_da_tra(start, end)

        # I.07: Thay đổi các khoản phải thu
        thay_doi_phai_thu = self._tinh_thay_doi_tai_san_phai_thu(start, end)

        # I.09: Thay đổi các khoản phải trả (trừ lãi vay, thuế TN)
        thay_doi_phai_tra = self._tinh_thay_doi_phai_tra(start, end)

        # I.11: LƯU CHUYỂN TIỀN THUẦN TỪ HĐKD (I.01 + I.02 + ... + I.10)
        luu_chuyen_tien_thuan_tu_hdkd = (
            loi_nhuan_truoc_thue
            + khau_hao
            + du_phong
            # ... (Thêm các chỉ tiêu I.04, I.05, I.08, I.10)
            + lai_tien_vay_da_tra.copy_negate()  # Chi phí lãi vay (I.06) phải được trừ
            + thay_doi_phai_thu
            + thay_doi_phai_tra
            # ... (Tiền thuế TN đã nộp, I.10)
        )

        # Giả định các Hoạt động Đầu tư và Tài chính trả về 0 để tập trung vào HĐKD
        luu_chuyen_tien_thuan_tu_hddt = Decimal(0)
        luu_chuyen_tien_thuan_tu_hdtc = Decimal(0)

        # IV. Lưu chuyển tiền thuần trong kỳ (I.11 + II.06 + III.06)
        luu_chuyen_tien_thuan_trong_ky = (
            luu_chuyen_tien_thuan_tu_hdkd
            + luu_chuyen_tien_thuan_tu_hddt
            + luu_chuyen_tien_thuan_tu_hdtc
        )

        # V. Tiền và tương đương tiền đầu kỳ (Cần logic phức tạp, tạm mock)
        tien_va_tuong_duong_tien_dau_ky = Decimal("200000000")  # MOCK

        # VI. Tiền và tương đương tiền cuối kỳ (IV + V)
        tien_va_tuong_duong_tien_cuoi_ky = (
            luu_chuyen_tien_thuan_trong_ky + tien_va_tuong_duong_tien_dau_ky
        )

        # --- TRẢ VỀ BÁO CÁO ---
        return BaoCaoLuuChuyenTienTe(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            luu_chuyen_tien_te_hdkd=LuuChuyenTienTeHDKD(
                loi_nhuan_truoc_thue=loi_nhuan_truoc_thue,
                dieu_chinh_khau_hao_ts_co_dinh=khau_hao,
                dieu_chinh_cac_khoan_du_phong=du_phong,
                chi_phi_lai_vay=lai_tien_vay_da_tra,
                tang_giam_cac_khoan_phai_thu=thay_doi_phai_thu,
                tang_giam_hang_ton_kho=Decimal(0),  # Cần triển khai
                tang_giam_cac_khoan_phai_tra=thay_doi_phai_tra,
                tien_thue_thu_nhap_doanh_nghiep_da_nop=Decimal(
                    0
                ),  # Cần triển khai
                luu_chuyen_tien_thuan_tu_hdkd=luu_chuyen_tien_thuan_trong_ky,  # Mã số 20 (Tổng HĐKD)
            ),
            luu_chuyen_tien_te_hddt=LuuChuyenTienTeHDDT(
                luu_chuyen_tien_thuan_tu_hddt=luu_chuyen_tien_thuan_tu_hddt
            ),
            luu_chuyen_tien_te_hdtc=LuuChuyenTienTeHDTC(
                luu_chuyen_tien_thuan_tu_hdtc=luu_chuyen_tien_thuan_tu_hdtc
            ),
            luu_chuyen_tien_thuan_trong_ky=luu_chuyen_tien_thuan_trong_ky,
            tien_va_tuong_duong_tien_dau_ky=tien_va_tuong_duong_tien_dau_ky,
            tien_va_tuong_duong_tien_cuoi_ky=tien_va_tuong_duong_tien_cuoi_ky,
        )



    def _tinh_thay_doi_hang_ton_kho(self, start: date, end: date) -> Decimal:
        """
        I.08: Tăng/giảm Hàng tồn kho (TK 151, 152, 153, 155, 156...).
        Tăng HTK -> Trừ khỏi Lợi nhuận.
        """
        
        # Giả định tập trung vào TK 152 (Nguyên vật liệu) và 156 (Hàng hóa)
        tai_khoan_hang_ton_kho = ["152", "156"]
        
        tong_tang_rong = Decimal(0)
        
        for tk in tai_khoan_hang_ton_kho:
            ps_no = self._tinh_phat_sinh_tai_khoan(tk=tk, loai="NO", bd=start, kt=end)
            ps_co = self._tinh_phat_sinh_tai_khoan(tk=tk, loai="CO", bd=start, kt=end)
            
            # Tăng ròng trong kỳ: PS Nợ (tăng) - PS Có (giảm)
            tang_giam_rong_tai_khoan = ps_no - ps_co
            tong_tang_rong += tang_giam_rong_tai_khoan

        # Nếu tổng tăng ròng là dương (tăng HTK), thì phải trả về giá trị âm (trừ khỏi dòng tiền)
        return tong_tang_rong.copy_negate()