# app/application/services/reports/cash_flow_service.py
"""
[SRP] Service tính toán Báo cáo Lưu chuyển tiền tệ (B03-DN) theo TT99/2025/TT-BTC.
Phụ lục IV: Mẫu B03-DN – phương pháp gián tiếp.
"""
import logging
from datetime import date
from decimal import Decimal

from app.application.interfaces.report_repo import ReportRepositoryInterface
from app.domain.models.report import (
    BaoCaoLuuChuyenTienTe,
    LuuChuyenTienTeHDDT,
    LuuChuyenTienTeHDKD,
    LuuChuyenTienTeHDTC,
)

logger = logging.getLogger(__name__)


class CashFlowService:
    def __init__(self, repo: ReportRepositoryInterface):
        self.repo = repo

    def lay_bao_cao(
        self,
        ky_hieu: str,
        ngay_lap: date,
        ngay_bat_dau: date,
        ngay_ket_thuc: date,
    ) -> BaoCaoLuuChuyenTienTe:
        """
        [TT99-PL4] Báo cáo Lưu chuyển tiền tệ theo phương pháp gián tiếp.
        """
        # Lấy B02-DN (Lợi nhuận trước thuế)
        # → Tạm mock để không phụ thuộc service khác
        loi_nhuan_truoc_thue = self._tinh_loi_nhuan_truoc_thue(
            ngay_bat_dau, ngay_ket_thuc
        )

        # Điều chỉnh: Khấu hao, lãi vay...
        khau_hao = self._tinh_phat_sinh_tai_khoan(
            "214", "CO", ngay_bat_dau, ngay_ket_thuc
        )
        lai_vay = self._tinh_phat_sinh_tai_khoan(
            "335", "NO", ngay_bat_dau, ngay_ket_thuc
        )

        # Thay đổi số dư: Phải thu, hàng tồn kho, phải trả
        delta_phai_thu = self._tinh_thay_doi_so_du(
            "131", ngay_bat_dau, ngay_ket_thuc
        )
        delta_hang_ton = self._tinh_thay_doi_so_du(
            "156", ngay_bat_dau, ngay_ket_thuc
        )
        delta_phai_tra = self._tinh_thay_doi_so_du(
            "331", ngay_bat_dau, ngay_ket_thuc
        )

        luu_chuyen_hdkd = (
            loi_nhuan_truoc_thue
            + khau_hao
            + lai_vay
            - delta_phai_thu
            - delta_hang_ton
            + delta_phai_tra
        ).quantize(Decimal("0.01"))

        # HĐĐT và HĐTC (mock tạm)
        luu_chuyen_hddt = Decimal("0")
        luu_chuyen_hdtc = Decimal("0")

        luu_chuyen_thuan_trong_ky = (
            luu_chuyen_hdkd + luu_chuyen_hddt + luu_chuyen_hdtc
        )

        tien_dau_ky = self._tinh_tien_dau_ky(ngay_bat_dau)
        tien_cuoi_ky = tien_dau_ky + luu_chuyen_thuan_trong_ky

        logger.info(
            f"[BC_LCTT] Ky: {ky_hieu}, Luu chuyen HĐKD: {luu_chuyen_hdkd}"
        )

        return BaoCaoLuuChuyenTienTe(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            luu_chuyen_tien_te_hdkd=LuuChuyenTienTeHDKD(
                loi_nhuan_truoc_thue=loi_nhuan_truoc_thue,
                dieu_chinh_khau_hao_ts_co_dinh=khau_hao,
                tien_lai_phai_tra_chi_tra=lai_vay,
                tang_giam_cac_khoan_phai_thu=delta_phai_thu,
                tang_giam_hang_ton_kho=delta_hang_ton,
                tang_giam_cac_khoan_phai_tra=delta_phai_tra,
                luu_chuyen_tien_thuan_tu_hdkd=luu_chuyen_hdkd,
            ),
            luu_chuyen_tien_te_hddt=LuuChuyenTienTeHDDT(
                luu_chuyen_thuan_tu_hddt=luu_chuyen_hddt
            ),
            luu_chuyen_tien_te_hdtc=LuuChuyenTienTeHDTC(
                luu_chuyen_thuan_tu_hdtc=luu_chuyen_hdtc
            ),
            luu_chuyen_tien_thuan_trong_ky=luu_chuyen_thuan_trong_ky,
            tien_va_tuong_duong_tien_dau_ky=tien_dau_ky,
            tien_va_tuong_duong_tien_cuoi_ky=tien_cuoi_ky,
        )

    def _tinh_loi_nhuan_truoc_thue(self, bd, kt):
        # Trả về từ B02-DN hoặc tính tổng từ journal
        # Trong thực tế, nên inject PerformanceService để lấy B02
        return Decimal("50000000")

    def _tinh_phat_sinh_tai_khoan(self, tk, loai, bd, kt):
        # Tính từ repo
        all_entries = self.repo.get_all_posted_in_range(bd, kt)
        tong = Decimal(0)
        for entry in all_entries:
            for line in entry.lines:
                if line.so_tai_khoan.startswith(tk):
                    tong += line.no if loai == "NO" else line.co
        return tong

    def _tinh_thay_doi_so_du(self, tk, bd, kt):
        # Tính SD đầu kỳ và cuối kỳ, trả về chênh lệch
        # Giả lập: SDCK - SDDK
        return Decimal("5000000")

    def _tinh_tien_dau_ky(self, ngay):
        return Decimal("100000000")
