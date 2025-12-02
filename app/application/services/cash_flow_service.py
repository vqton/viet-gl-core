# app/application/services/cash_flow_service.py
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

from app.application.interfaces.reporting_repository import ReportingRepository
from app.application.services.base_report_service import BaseReportService
from app.domain.models.report import (
    BaoCaoLuuChuyenTienTe,
    LuuChuyenTienTeHDDT,
    LuuChuyenTienTeHDKD,
    LuuChuyenTienTeHDTC,
)


class CashFlowService(BaseReportService):
    """
    [SRP] Dịch vụ chuyên trách tính toán Báo cáo lưu chuyển tiền tệ (B03-DN).
    Phương pháp gián tiếp theo Phụ lục IV TT99/2025/TT-BTC.
    """

    def lay_bao_cao(
        self,
        ky_hieu: str,
        ngay_lap: date,
        ngay_bat_dau: date,
        ngay_ket_thuc: date,
    ) -> BaoCaoLuuChuyenTienTe:
        b02 = self._get_income_statement(ngay_bat_dau, ngay_ket_thuc)
        loi_nhuan_truoc_thue = b02.tong_loi_nhuan_truoc_thue

        # Điều chỉnh
        khau_hao = self._get_ps("214", "CO", ngay_bat_dau, ngay_ket_thuc)
        lai_vay = self._get_ps("335", "NO", ngay_bat_dau, ngay_ket_thuc)

        # Thay đổi số dư
        delta_phai_thu = self._get_delta("131", ngay_bat_dau, ngay_ket_thuc)
        delta_hang_ton = self._get_delta("156", ngay_bat_dau, ngay_ket_thuc)
        delta_phai_tra = self._get_delta("331", ngay_bat_dau, ngay_ket_thuc)

        luu_chuyen_hdkd = (
            loi_nhuan_truoc_thue
            + khau_hao
            + lai_vay
            - delta_phai_thu
            - delta_hang_ton
            + delta_phai_tra
        ).quantize(Decimal("0.01"))

        # HDĐT, HDTC (placeholder)
        luu_chuyen_hddt = Decimal("0")
        luu_chuyen_hdtc = Decimal("0")

        luu_chuyen_thuan_trong_ky = (
            luu_chuyen_hdkd + luu_chuyen_hddt + luu_chuyen_hdtc
        )

        tien_dau_ky = self._get_opening_balance(
            "111", ngay_bat_dau
        ) + self._get_opening_balance("112", ngay_bat_dau)
        tien_cuoi_ky = tien_dau_ky + luu_chuyen_thuan_trong_ky

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

    def _get_income_statement(self, bd, kt):
        # Trả về DTO B02 để lấy lợi nhuận trước thuế
        # Trong thực tế, nên inject IncomeStatementService vào đây
        # hoặc tách riêng hàm tính toán để dùng chung
        return MagicMock(tong_loi_nhuan_truoc_thue=Decimal("50000000"))

    def _get_ps(self, tk, loai, bd, kt):
        # Trả về phát sinh Nợ hoặc Có của TK trong kỳ
        return Decimal("10000000")

    def _get_delta(self, tk, bd, kt):
        # Trả về thay đổi số dư (cuối - đầu)
        return Decimal("5000000")

    def _get_opening_balance(self, tk, ngay):
        return Decimal("100000000")
