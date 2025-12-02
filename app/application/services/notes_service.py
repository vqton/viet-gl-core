# app/application/services/notes_service.py
from datetime import date

from app.application.interfaces.reporting_repository import ReportingRepository
from app.application.services.base_report_service import BaseReportService
from app.domain.models.report import BaoCaoThuyetMinh


class NotesService(BaseReportService):
    """
    [SRP] Dịch vụ chuyên trách tính toán Bản thuyết minh Báo cáo tài chính (B09-DN).
    """

    def lay_bao_cao(
        self,
        ky_hieu: str,
        ngay_lap: date,
        ngay_bat_dau: date,
        ngay_ket_thuc: date,
    ) -> BaoCaoThuyetMinh:
        # Lấy dữ liệu từ các báo cáo khác để tổng hợp thuyết minh
        # Trong thực tế, bạn có thể inject các service khác vào đây
        return BaoCaoThuyetMinh(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            dac_diem_hoat_dong_cua_doanh_nghiep="Doanh nghiệp thương mại",
            chuan_muc_ke_toan_ap_dung="VAS và TT99/2025/TT-BTC",
            # ... các trường khác
        )
