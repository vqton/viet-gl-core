# app/application/services/reports/disclosure_service.py
"""
[SRP] Service cho Bản thuyết minh BCTC (B09-DN).
"""
from datetime import date

from app.application.interfaces.report_repo import ReportRepositoryInterface
from app.domain.models.report import BaoCaoThuyetMinh


class DisclosureService:
    def __init__(self, repo: ReportRepositoryInterface):
        self.repo = repo

    def lay_bao_cao(
        self,
        ky_hieu: str,
        ngay_lap: date,
        ngay_bat_dau: date,
        ngay_ket_thuc: date,
    ) -> BaoCaoThuyetMinh:
        # Lấy dữ liệu từ các báo cáo khác hoặc repo
        return BaoCaoThuyetMinh(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            chuan_muc_ke_toan_ap_dung="VAS và TT99/2025/TT-BTC",
            # ...
        )
