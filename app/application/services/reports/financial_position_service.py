# app/application/services/reports/financial_position_service.py
"""
[SRP] Service chịu trách nhiệm tính toán Báo cáo tình hình tài chính (B01-DN) theo TT99/2025/TT-BTC.
Phụ lục IV: Mẫu B01-DN.
"""
import logging
from datetime import date
from decimal import Decimal
from typing import List

from app.application.interfaces.report_repo import ReportRepositoryInterface
from app.domain.models.account import LoaiTaiKhoan, TaiKhoan
from app.domain.models.report import (
    BaoCaoTinhHinhTaiChinh,
    NoPhaiTraDaiHan,
    NoPhaiTraNganHan,
    TaiSanDaiHan,
    TaiSanNganHan,
    TongNguonVon,
    TongTaiSan,
    VonChuSoHuu,
)

logger = logging.getLogger(__name__)


class FinancialPositionService:
    """
    [TT99-PL4] Lập Báo cáo tình hình tài chính (B01-DN).
    """

    def __init__(self, repo: ReportRepositoryInterface):
        self.repo = repo

    def lay_bao_cao(
        self, ky_hieu: str, ngay_lap: date, ngay_ket_thuc: date
    ) -> BaoCaoTinhHinhTaiChinh:
        all_accounts = self.repo.get_all_accounts()
        account_balances = self._tinh_tat_ca_so_du(
            all_accounts, date(ngay_ket_thuc.year, 1, 1), ngay_ket_thuc
        )

        def get_balance(so_tai_khoan_goc: str) -> Decimal:
            tong_no = Decimal(0)
            tong_co = Decimal(0)
            for so_tai_khoan, (sd_no, sd_co) in account_balances.items():
                if so_tai_khoan.startswith(so_tai_khoan_goc):
                    tong_no += sd_no
                    tong_co += sd_co

            # Xác định loại tài khoản từ DB
            tai_khoan_goc = next(
                (
                    tk
                    for tk in all_accounts
                    if tk.so_tai_khoan == so_tai_khoan_goc
                ),
                None,
            )
            if not tai_khoan_goc:
                return Decimal(0)

            loai_tk = tai_khoan_goc.loai_tai_khoan
            if loai_tk in [LoaiTaiKhoan.TAI_SAN]:
                net_balance = tong_no - tong_co
                return abs(net_balance).quantize(Decimal("0.01"))
            elif loai_tk in [
                LoaiTaiKhoan.NO_PHAI_TRA,
                LoaiTaiKhoan.VON_CHU_SO_HUU,
            ]:
                net_balance = tong_co - tong_no
                return abs(net_balance).quantize(Decimal("0.01"))
            return Decimal(0)

        # Tính tài sản
        tien_mat = get_balance("111")
        tien_gui = get_balance("112")
        tien_dang_chuyen = get_balance("113")
        tien_va_tg_tien = tien_mat + tien_gui + tien_dang_chuyen

        tai_san_ngan_han = TaiSanNganHan(
            tien_va_cac_khoan_tg_tien=tien_va_tg_tien,
            cac_khoan_dau_tu_tc_ngan_han=get_balance("121"),
            cac_khoan_phai_thu_ngan_han=get_balance("131"),
            hang_ton_kho=get_balance("156"),
            tai_san_ngan_han_khac=get_balance("150"),
            tong_tai_san_ngan_han=get_balance("100"),
        )

        tai_san_dai_han = TaiSanDaiHan(
            tai_san_co_dinh_huu_hinh=get_balance("211") - get_balance("214"),
            tai_san_co_dinh_vo_hinh=get_balance("221"),
            bat_dong_san_dau_tu=get_balance("217"),
            cac_khoan_dau_tu_tc_dai_han=get_balance("221"),
            tai_san_dai_han_khac=get_balance("241"),
            tong_tai_san_dai_han=get_balance("200"),
        )

        tong_tai_san = TongTaiSan(
            tai_san_ngan_han=tai_san_ngan_han,
            tai_san_dai_han=tai_san_dai_han,
            tong_cong_tai_san=get_balance("100") + get_balance("200"),
        )

        # Tính nguồn vốn
        no_ngan_han = NoPhaiTraNganHan(
            vay_no_thue_tai_chinh_ngan_han=get_balance("341"),
            phai_tra_ngan_han_nguoi_ban=get_balance("331"),
            thue_va_cac_khoan_phai_nop_nha_nuoc=get_balance("333"),
            phai_tra_ngan_han_khac=get_balance("338"),
            tong_no_ngan_han=get_balance("300"),
        )

        no_dai_han = NoPhaiTraDaiHan(
            vay_no_thue_tai_chinh_dai_han=get_balance("341"),
            du_phong_phai_tra_dai_han=Decimal(0),
            tong_no_dai_han=get_balance("400"),
        )

        von_chu_so_huu = VonChuSoHuu(
            von_dau_tu_cua_chu_so_huu=get_balance("411"),
            loi_nhuan_sau_thue_chua_phan_phoi=get_balance("421"),
            tong_von_chu_so_huu=get_balance("500"),
        )

        tong_nguon_von = TongNguonVon(
            no_phai_tra_ngan_han=no_ngan_han,
            no_phai_tra_dai_han=no_dai_han,
            von_chu_so_huu=von_chu_so_huu,
            tong_cong_nguon_von=get_balance("300")
            + get_balance("400")
            + get_balance("500"),
        )

        # Kiểm tra cân đối
        if abs(
            tong_tai_san.tong_cong_tai_san - tong_nguon_von.tong_cong_nguon_von
        ) > Decimal("0.01"):
            logger.warning(
                f"[CAN DOI LOI] TS: {tong_tai_san.tong_cong_tai_san}, NV: {tong_nguon_von.tong_cong_nguon_von}"
            )

        logger.info(
            f"[BC_TAI_SAN] Ky: {ky_hieu}, Tong tai san: {tong_tai_san.tong_cong_tai_san}"
        )
        return BaoCaoTinhHinhTaiChinh(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            tai_san=tong_tai_san,
            nguon_von=tong_nguon_von,
        )

    def _tinh_tat_ca_so_du(
        self, accounts: List[TaiKhoan], start: date, end: date
    ):
        balances = {}
        for tk in accounts:
            _, _, _, sd_ck_no, sd_ck_co = self.repo.get_account_balance(
                tk.so_tai_khoan, start, end
            )
            balances[tk.so_tai_khoan] = (sd_ck_no, sd_ck_co)
        return balances
