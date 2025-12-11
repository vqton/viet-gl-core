# app/application/services/reports/performance_service.py
from datetime import date
from decimal import Decimal
from typing import List

from app.application.interfaces.journal_entry_repo import (
    JournalEntryRepositoryInterface,
)
from app.domain.models.report import BaoCaoKetQuaHDKD


class PerformanceService:
    def __init__(self, repo: JournalEntryRepositoryInterface, acc_repo=None):
        self.repo = repo
        # acc_repo không dùng trong B02, nhưng giữ để tương thích DI

    def _tinh_phat_sinh(
        self, tk: str, loai: str, start: date, end: date
    ) -> Decimal:
        ps = Decimal(0)
        for entry in self.repo.get_all_posted_in_range(start, end):
            for line in entry.lines:
                if line.so_tai_khoan.startswith(tk):
                    ps += line.no if loai == "NO" else line.co
        return ps

    def lay_bao_cao(
        self,
        ky_hieu: str,
        ngay_lap: date,
        ngay_bat_dau: date,
        ngay_ket_thuc: date,
    ) -> BaoCaoKetQuaHDKD:
        start, end = ngay_bat_dau, ngay_ket_thuc

        # 1. Doanh thu bán hàng (511)
        doanh_thu_ban_hang = self._tinh_phat_sinh("511", "CO", start, end)
        # 2. Giảm trừ (521: chiết khấu, giảm giá, hàng trả lại)
        giam_tru = self._tinh_phat_sinh("521", "NO", start, end)
        doanh_thu_thuan = doanh_thu_ban_hang - giam_tru

        # 3. Giá vốn (632)
        gia_von = self._tinh_phat_sinh("632", "NO", start, end)
        loi_nhuan_gop = doanh_thu_thuan - gia_von

        # 4. Chi phí tài chính (635)
        chi_phi_tc = self._tinh_phat_sinh("635", "NO", start, end)
        # 5. Chi phí bán hàng (641)
        chi_phi_bh = self._tinh_phat_sinh("641", "NO", start, end)
        # 6. Chi phí QLDN (642)
        chi_phi_qldn = self._tinh_phat_sinh("642", "NO", start, end)
        loi_nhuan_thuan = (
            loi_nhuan_gop - chi_phi_tc - chi_phi_bh - chi_phi_qldn
        )

        # 7. Thu nhập khác (711)
        thu_nhap_khac = self._tinh_phat_sinh("711", "CO", start, end)
        # 8. Chi phí khác (811)
        chi_phi_khac = self._tinh_phat_sinh("811", "NO", start, end)
        loi_nhuan_khac = thu_nhap_khac - chi_phi_khac

        tong_loi_nhuan_truoc_thue = loi_nhuan_thuan + loi_nhuan_khac
        # 9. Thuế TNDN (821)
        thue_hien_hanh = self._tinh_phat_sinh("821", "NO", start, end)
        thue_hoan_lai = Decimal(0)  # temporarily
        loi_nhuan_sau_thue = (
            tong_loi_nhuan_truoc_thue - thue_hien_hanh - thue_hoan_lai
        )

        return BaoCaoKetQuaHDKD(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            doanh_thu_ban_hang=doanh_thu_ban_hang,
            cac_khoan_giam_tru_doanh_thu=giam_tru,
            doanh_thu_thuan=doanh_thu_thuan,
            gia_von_hang_ban=gia_von,
            loi_nhuan_gop=loi_nhuan_gop,
            chi_phi_tai_chinh=chi_phi_tc,
            chi_phi_ban_hang=chi_phi_bh,
            chi_phi_quan_ly_doanh_nghiep=chi_phi_qldn,
            loi_nhuan_thuan_tu_hdkd=loi_nhuan_thuan,
            thu_nhap_khac=thu_nhap_khac,
            chi_phi_khac=chi_phi_khac,
            loi_nhuan_khac=loi_nhuan_khac,
            tong_loi_nhuan_truoc_thue=tong_loi_nhuan_truoc_thue,
            chi_phi_thue_thu_nhap_doanh_nghiep_hien_hanh=thue_hien_hanh,
            chi_phi_thue_thu_nhap_doanh_nghiep_hoan_lai=thue_hoan_lai,
            loi_nhuan_sau_thue=loi_nhuan_sau_thue,
        )
