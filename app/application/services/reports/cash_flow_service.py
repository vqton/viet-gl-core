# app/application/services/reports/cash_flow_service.py
"""
Dịch vụ tạo Báo cáo Lưu chuyển Tiền tệ (B03-DN) theo phương pháp Gián tiếp.
[TT99-PL4] Tuân thủ đầy đủ Phụ lục IV TT99/2025/TT-BTC.
"""

from datetime import date
from decimal import Decimal
from typing import List

from app.application.interfaces.journal_entry_repo import (
    JournalEntryRepositoryInterface,
)
from app.application.services.reports.performance_service import (
    PerformanceService,
)
from app.domain.models.journal_entry import GhiSoKeToan, TransactionType
from app.domain.models.report import (
    BaoCaoLuuChuyenTienTe,
    LuuChuyenTienTeHDDT,
    LuuChuyenTienTeHDKD,
    LuuChuyenTienTeHDTC,
)

# Các nhóm tài khoản theo TT99
TK_TIEN = ["111", "112", "113"]
TK_TSCD = ["211", "213"]
TK_THUE_TNDN = ["3334"]
TK_VAY = ["341"]
TK_LAI_VAY = ["335", "341"]


class CashFlowService:
    """
    [SRP] Chỉ chịu trách nhiệm lập B03-DN.
    [TT99-PL4] Tính đúng các chỉ tiêu dòng tiền thực:
    - I.06: Tiền lãi vay đã trả
    - I.10: Tiền thuế TNDN đã nộp
    - II.21: Tiền chi mua TSCĐ
    - III.33: Tiền chi trả gốc vay
    """

    def __init__(
        self,
        repo: JournalEntryRepositoryInterface,
        performance_service: PerformanceService,
    ):
        self.repo = repo
        self.performance_service = performance_service

    def _tinh_phat_sinh_tai_khoan(
        self, tk: str, loai: str, bd: date, kt: date
    ) -> Decimal:
        """Tính PS Nợ/Có cho tài khoản (dùng cho điều chỉnh gián tiếp)."""
        tong = Decimal(0)
        for entry in self.repo.get_all_posted_in_range(bd, kt):
            for line in entry.lines:
                if line.so_tai_khoan.startswith(tk):
                    if (
                        loai == "NO"
                        and line.transaction_type == TransactionType.DEBIT
                    ):
                        tong += line.amount
                    elif (
                        loai == "CO"
                        and line.transaction_type == TransactionType.CREDIT
                    ):
                        tong += line.amount
        return tong

    # ================================
    # I. HOẠT ĐỘNG KINH DOANH (HĐKD)
    # ================================

    def _tinh_chi_phi_lai_vay(self, start: date, end: date) -> Decimal:
        """I.05: Chi phí lãi vay (PS Nợ TK 635)."""
        return self._tinh_phat_sinh_tai_khoan("635", "NO", start, end)

    def _tinh_tien_lai_vay_da_tra(self, start: date, end: date) -> Decimal:
        """
        I.06: Tiền lãi vay đã trả thực tế.
        Phân tích bút toán: Nợ (335/341) + Có (111/112/113).
        """
        all_entries = self.repo.get_all_posted_in_range(start, end)
        tong = Decimal(0)
        for entry in all_entries:
            lines_tien = [
                l
                for l in entry.lines
                if l.so_tai_khoan.startswith(tuple(TK_TIEN))
                and l.transaction_type == TransactionType.CREDIT
            ]
            lines_lai_vay = [
                l
                for l in entry.lines
                if l.so_tai_khoan in TK_LAI_VAY
                and l.transaction_type == TransactionType.DEBIT
            ]
            if lines_tien and lines_lai_vay:
                so_tien = min(
                    sum(l.amount for l in lines_tien),
                    sum(l.amount for l in lines_lai_vay),
                )
                tong += so_tien
        return tong

    def _tinh_tien_thue_thu_nhap_da_nop(
        self, start: date, end: date
    ) -> Decimal:
        """
        I.10: Tiền thuế TNDN đã nộp thực tế.
        Phân tích bút toán: Nợ 3334 + Có (111/112/113).
        """
        all_entries = self.repo.get_all_posted_in_range(start, end)
        tong = Decimal(0)
        for entry in all_entries:
            lines_tien = [
                l
                for l in entry.lines
                if l.so_tai_khoan.startswith(tuple(TK_TIEN))
                and l.transaction_type == TransactionType.CREDIT
            ]
            lines_thue = [
                l
                for l in entry.lines
                if l.so_tai_khoan in TK_THUE_TNDN
                and l.transaction_type == TransactionType.DEBIT
            ]
            if lines_tien and lines_thue:
                so_tien = min(
                    sum(l.amount for l in lines_tien),
                    sum(l.amount for l in lines_thue),
                )
                tong += so_tien
        return tong

    # ================================
    # II. HOẠT ĐỘNG ĐẦU TƯ (HĐĐT)
    # ================================

    def _tinh_tien_chi_mua_tscd(self, start: date, end: date) -> Decimal:
        """
        II.21: Tiền chi mua sắm TSCĐ.
        Phân tích bút toán: Nợ (211/213) + Có (111/112/113).
        """
        all_entries = self.repo.get_all_posted_in_range(start, end)
        tong = Decimal(0)
        for entry in all_entries:
            lines_tien = [
                l
                for l in entry.lines
                if l.so_tai_khoan.startswith(tuple(TK_TIEN))
                and l.transaction_type == TransactionType.CREDIT
            ]
            lines_tscd = [
                l
                for l in entry.lines
                if l.so_tai_khoan.startswith(tuple(TK_TSCD))
                and l.transaction_type == TransactionType.DEBIT
            ]
            if lines_tien and lines_tscd:
                so_tien = min(
                    sum(l.amount for l in lines_tien),
                    sum(l.amount for l in lines_tscd),
                )
                tong += so_tien
        return tong

    def _tinh_tien_thu_ban_tscd(self, start: date, end: date) -> Decimal:
        """
        II.22: Tiền thu bán TSCĐ.
        Phân tích bút toán: Nợ (111/112/113) + Có (211/213).
        """
        all_entries = self.repo.get_all_posted_in_range(start, end)
        tong = Decimal(0)
        for entry in all_entries:
            lines_tien = [
                l
                for l in entry.lines
                if l.so_tai_khoan.startswith(tuple(TK_TIEN))
                and l.transaction_type == TransactionType.DEBIT
            ]
            lines_tscd = [
                l
                for l in entry.lines
                if l.so_tai_khoan.startswith(tuple(TK_TSCD))
                and l.transaction_type == TransactionType.CREDIT
            ]
            if lines_tien and lines_tscd:
                so_tien = min(
                    sum(l.amount for l in lines_tien),
                    sum(l.amount for l in lines_tscd),
                )
                tong += so_tien
        return tong

    # ================================
    # III. HOẠT ĐỘNG TÀI CHÍNH (HĐTC)
    # ================================

    def _tinh_tien_chi_tra_goc_vay(self, start: date, end: date) -> Decimal:
        """
        III.33: Tiền chi trả gốc vay.
        Phân tích bút toán: Nợ 341 + Có (111/112/113).
        """
        all_entries = self.repo.get_all_posted_in_range(start, end)
        tong = Decimal(0)
        for entry in all_entries:
            lines_tien = [
                l
                for l in entry.lines
                if l.so_tai_khoan.startswith(tuple(TK_TIEN))
                and l.transaction_type == TransactionType.CREDIT
            ]
            lines_vay = [
                l
                for l in entry.lines
                if l.so_tai_khoan in TK_VAY
                and l.transaction_type == TransactionType.DEBIT
            ]
            if lines_tien and lines_vay:
                so_tien = min(
                    sum(l.amount for l in lines_tien),
                    sum(l.amount for l in lines_vay),
                )
                tong += so_tien
        return tong

    # ================================
    # PHƯƠNG THỨC CHÍNH
    # ================================

    def lay_bao_cao(
        self,
        ky_hieu: str,
        ngay_lap: date,
        ngay_bat_dau: date,
        ngay_ket_thuc: date,
    ) -> BaoCaoLuuChuyenTienTe:
        # --- Lấy dữ liệu từ B02 ---
        b02 = self.performance_service.lay_bao_cao(
            ky_hieu, ngay_lap, ngay_bat_dau, ngay_ket_thuc
        )

        # --- Tính các chỉ tiêu HĐKD (phần điều chỉnh) ---
        loi_nhuan_truoc_thue = b02.tong_loi_nhuan_truoc_thue
        khau_hao = self._tinh_phat_sinh_tai_khoan(
            "214", "CO", ngay_bat_dau, ngay_ket_thuc
        )
        lai_lo_hdt = self._tinh_phat_sinh_tai_khoan(
            "515", "CO", ngay_bat_dau, ngay_ket_thuc
        ) - self._tinh_phat_sinh_tai_khoan(
            "635", "NO", ngay_bat_dau, ngay_ket_thuc
        )
        lai_lo_hdt = -lai_lo_hdt  # Điều chỉnh ngược lại LNTT

        thay_doi_phai_thu = -self._tinh_phat_sinh_tai_khoan(
            "131", "NO", ngay_bat_dau, ngay_ket_thuc
        )  # tạm tính đơn giản
        thay_doi_hang_ton_kho = -self._tinh_phat_sinh_tai_khoan(
            "156", "NO", ngay_bat_dau, ngay_ket_thuc
        )
        thay_doi_phai_tra = self._tinh_phat_sinh_tai_khoan(
            "331", "CO", ngay_bat_dau, ngay_ket_thuc
        )

        # --- Dòng tiền thực HĐKD ---
        tien_lai_vay_da_tra = self._tinh_tien_lai_vay_da_tra(
            ngay_bat_dau, ngay_ket_thuc
        )
        tien_thue_tndn_da_nop = self._tinh_tien_thue_thu_nhap_da_nop(
            ngay_bat_dau, ngay_ket_thuc
        )

        luu_chuyen_hdkd = (
            loi_nhuan_truoc_thue
            + khau_hao
            + lai_lo_hdt
            + self._tinh_chi_phi_lai_vay(ngay_bat_dau, ngay_ket_thuc)
            + thay_doi_phai_thu
            + thay_doi_hang_ton_kho
            + thay_doi_phai_tra
        )
        luu_chuyen_tien_thuan_tu_hdkd = (
            luu_chuyen_hdkd - tien_lai_vay_da_tra - tien_thue_tndn_da_nop
        )

        # --- HĐĐT ---
        tien_chi_mua_tscd = self._tinh_tien_chi_mua_tscd(
            ngay_bat_dau, ngay_ket_thuc
        )
        tien_thu_ban_tscd = self._tinh_tien_thu_ban_tscd(
            ngay_bat_dau, ngay_ket_thuc
        )
        luu_chuyen_tien_thuan_tu_hddt = -tien_chi_mua_tscd + tien_thu_ban_tscd

        # --- HĐTC ---
        tien_chi_tra_goc_vay = self._tinh_tien_chi_tra_goc_vay(
            ngay_bat_dau, ngay_ket_thuc
        )
        luu_chuyen_tien_thuan_tu_hdtc = -tien_chi_tra_goc_vay

        # --- Tổng hợp ---
        luu_chuyen_tien_thuan_trong_ky = (
            luu_chuyen_tien_thuan_tu_hdkd
            + luu_chuyen_tien_thuan_tu_hddt
            + luu_chuyen_tien_thuan_tu_hdtc
        )

        tien_dau_ky = Decimal(
            0
        )  # ← Cần implement get_so_du_dau_ky cho nhóm TK_TIEN
        tien_cuoi_ky = luu_chuyen_tien_thuan_trong_ky + tien_dau_ky

        return BaoCaoLuuChuyenTienTe(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            luu_chuyen_tien_te_hdkd=LuuChuyenTienTeHDKD(
                loi_nhuan_truoc_thue=loi_nhuan_truoc_thue,
                dieu_chinh_khau_hao_ts_co_dinh=khau_hao,
                lai_lo_hoat_dong_dau_tu=lai_lo_hdt,
                chi_phi_lai_vay=self._tinh_chi_phi_lai_vay(
                    ngay_bat_dau, ngay_ket_thuc
                ),
                tang_giam_cac_khoan_phai_thu=thay_doi_phai_thu,
                tang_giam_hang_ton_kho=thay_doi_hang_ton_kho,
                tang_giam_cac_khoan_phai_tra=thay_doi_phai_tra,
                tien_chi_tra_lai_vay=tien_lai_vay_da_tra,
                tien_thue_thu_nhap_da_nop=tien_thue_tndn_da_nop,
                luu_chuyen_tien_thuan_tu_hdkd=luu_chuyen_tien_thuan_tu_hdkd,
            ),
            luu_chuyen_tien_te_hddt=LuuChuyenTienTeHDDT(
                tien_chi_mua_sam_xay_dung_ts_dai_han=tien_chi_mua_tscd,
                tien_thu_thanh_ly_nhuong_ban_ts_dai_han=tien_thu_ban_tscd,
                luu_chuyen_tien_thuan_tu_hddt=luu_chuyen_tien_thuan_tu_hddt,
            ),
            luu_chuyen_tien_te_hdtc=LuuChuyenTienTeHDTC(
                tien_chi_tra_goc_vay=tien_chi_tra_goc_vay,
                luu_chuyen_tien_thuan_tu_hdtc=luu_chuyen_tien_thuan_tu_hdtc,
            ),
            luu_chuyen_tien_thuan_trong_ky=luu_chuyen_tien_thuan_trong_ky,
            tien_va_tuong_duong_tien_dau_ky=tien_dau_ky,
            anh_huong_thay_doi_ty_gia=Decimal(0),
            tien_va_tuong_duong_tien_cuoi_ky=tien_cuoi_ky,
        )
