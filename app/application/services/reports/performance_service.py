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
        # Trong thực tế, service này sẽ tổng hợp thông tin chi tiết từ các báo cáo khác (B01, B02, B03)
        # và các thông tin định tính khác để lập Bản Thuyết minh BCTC.
        # Ở đây, ta chỉ cung cấp một khung sườn.
        return BaoCaoThuyetMinh(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            chuan_muc_ke_toan_ap_dung="VAS và Thông tư 200/2014/TT-BTC",
            noi_dung_chinh="Các chính sách kế toán quan trọng, thông tin bổ sung cho B01, B02, B03.",
            # ... (Thêm các trường dữ liệu chi tiết cho thuyết minh) ...
        )