# app/application/services/income_statement_service.py
from datetime import date
from decimal import Decimal

from app.application.interfaces.reporting_repository import ReportingRepository
from app.application.services.base_report_service import BaseReportService
from app.domain.models.report import BaoCaoKetQuaHDKD


class IncomeStatementService(BaseReportService):
    """
    [SRP] Dịch vụ chuyên trách tính toán Báo cáo kết quả hoạt động kinh doanh (B02-DN).
    Tuân thủ Phụ lục IV TT99/2025/TT-BTC.
    """

    def lay_bao_cao(
        self,
        ky_hieu: str,
        ngay_lap: date,
        ngay_bat_dau: date,
        ngay_ket_thuc: date,
    ) -> BaoCaoKetQuaHDKD:
        def get_ps(so_tai_khoan_goc: str, loai_ps: str) -> Decimal:
            all_accounts = self.repo.get_all_accounts()
            tong = Decimal(0)
            for tai_khoan in all_accounts:
                if tai_khoan.so_tai_khoan.startswith(so_tai_khoan_goc):
                    _, ps_no, ps_co, _, _ = self.repo.get_account_balance(
                        tai_khoan.so_tai_khoan, ngay_bat_dau, ngay_ket_thuc
                    )
                    if loai_ps == "NO":
                        tong += ps_no
                    elif loai_ps == "CO":
                        tong += ps_co
            return tong.quantize(Decimal("0.01"))

        doanh_thu_ban_hang = get_ps("511", "CO")
        giam_tru_doanh_thu = get_ps("521", "NO")
        doanh_thu_thuan = doanh_thu_ban_hang - giam_tru_doanh_thu

        gia_von_hang_ban = get_ps("632", "NO")
        loi_nhuan_gop = doanh_thu_thuan - gia_von_hang_ban

        doanh_thu_hoat_dong_tc = get_ps("515", "CO")
        chi_phi_tai_chinh = get_ps("635", "NO")
        chi_phi_ban_hang = get_ps("641", "NO")
        chi_phi_quan_ly = get_ps("642", "NO")
        loi_nhuan_thuan_tu_hdkd = (
            loi_nhuan_gop
            + doanh_thu_hoat_dong_tc
            - chi_phi_tai_chinh
            - chi_phi_ban_hang
            - chi_phi_quan_ly
        )

        thu_nhap_khac = get_ps("711", "CO")
        chi_phi_khac = get_ps("811", "NO")
        loi_nhuan_khac = thu_nhap_khac - chi_phi_khac

        tong_loi_nhuan_truoc_thue = loi_nhuan_thuan_tu_hdkd + loi_nhuan_khac
        chi_phi_thue = get_ps("821", "NO")
        loi_nhuan_sau_thue = tong_loi_nhuan_truoc_thue - chi_phi_thue

        return BaoCaoKetQuaHDKD(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            doanh_thu_ban_hang=doanh_thu_ban_hang,
            cac_khoan_giam_tru_doanh_thu=giam_tru_doanh_thu,
            doanh_thu_thuan=doanh_thu_thuan,
            gia_von_hang_ban=gia_von_hang_ban,
            loi_nhuan_gop=loi_nhuan_gop,
            doanh_thu_hoat_dong_tai_chinh=doanh_thu_hoat_dong_tc,
            chi_phi_tai_chinh=chi_phi_tai_chinh,
            chi_phi_ban_hang=chi_phi_ban_hang,
            chi_phi_quan_ly_doanh_nghiep=chi_phi_quan_ly,
            loi_nhuan_thuan_tu_hdkd=loi_nhuan_thuan_tu_hdkd,
            thu_nhap_khac=thu_nhap_khac,
            chi_phi_khac=chi_phi_khac,
            loi_nhuan_khac=loi_nhuan_khac,
            tong_loi_nhuan_truoc_thue=tong_loi_nhuan_truoc_thue,
            chi_phi_thue_thu_nhap_doanh_nghiep_hien_hanh=chi_phi_thue,
            loi_nhuan_sau_thue=loi_nhuan_sau_thue,
        )
