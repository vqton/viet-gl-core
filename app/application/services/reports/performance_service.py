# app/application/services/reports/performance_service.py
"""
[SRP] Service tính Báo cáo Kết quả HĐKD (B02-DN).
"""
from datetime import date
from decimal import Decimal

from app.application.interfaces.report_repo import ReportRepositoryInterface
from app.domain.models.report import BaoCaoKetQuaHDKD


class PerformanceService:
    def __init__(self, repo: ReportRepositoryInterface):
        self.repo = repo

    def lay_bao_cao(
        self,
        ky_hieu: str,
        ngay_lap: date,
        ngay_bat_dau: date,
        ngay_ket_thuc: date,
    ) -> BaoCaoKetQuaHDKD:
        # Tính toán tương tự như trong ReportingService cũ
        doanh_thu = self._tinh_phat_sinh_tai_khoan(
            "511", "CO", ngay_bat_dau, ngay_ket_thuc
        )
        gia_von = self._tinh_phat_sinh_tai_khoan(
            "632", "NO", ngay_bat_dau, ngay_ket_thuc
        )
        loi_nhuan = doanh_thu - gia_von

        return BaoCaoKetQuaHDKD(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            doanh_thu_ban_hang=doanh_thu,
            gia_von_hang_ban=gia_von,
            loi_nhuan_sau_thue=loi_nhuan,
        )

    def _tinh_phat_sinh_tai_khoan(self, tk_goc, loai_ps, bd, kt):
        all_entries = self.repo.get_all_posted_in_range(bd, kt)
        tong = Decimal(0)
        for entry in all_entries:
            for line in entry.lines:
                if line.so_tai_khoan.startswith(tk_goc):
                    tong += line.no if loai_ps == "NO" else line.co
        return tong
