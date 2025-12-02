# app/application/services/balance_sheet_service.py
from datetime import date
from decimal import Decimal
from typing import Dict, Tuple

from app.application.interfaces.reporting_repository import ReportingRepository
from app.application.services.base_report_service import BaseReportService
from app.domain.models.account import LoaiTaiKhoan
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


class BalanceSheetService(BaseReportService):
    """
    [SRP] Dịch vụ chuyên trách tính toán Báo cáo tình hình tài chính (B01-DN).
    Tuân thủ Phụ lục IV TT99/2025/TT-BTC.
    """

    def lay_bao_cao(
        self, ky_hieu: str, ngay_lap: date, ngay_ket_thuc: date
    ) -> BaoCaoTinhHinhTaiChinh:
        all_accounts = self.repo.get_all_accounts()
        account_balances: Dict[str, Tuple[Decimal, Decimal]] = {}

        ngay_dau_nam = date(ngay_ket_thuc.year, 1, 1)

        for tai_khoan in all_accounts:
            _, _, _, sd_cuoi_ky_no, sd_cuoi_ky_co = (
                self.repo.get_account_balance(
                    tai_khoan.so_tai_khoan, ngay_dau_nam, ngay_ket_thuc
                )
            )
            account_balances[tai_khoan.so_tai_khoan] = (
                sd_cuoi_ky_no,
                sd_cuoi_ky_co,
            )

        def get_balance(so_tai_khoan_goc: str) -> Decimal:
            tong_no = Decimal(0)
            tong_co = Decimal(0)
            for so_tai_khoan, (sd_no, sd_co) in account_balances.items():
                if so_tai_khoan.startswith(so_tai_khoan_goc):
                    tong_no += sd_no
                    tong_co += sd_co

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
            tien_va_cac_khoan_tuong_duong_tien=tien_va_tg_tien,
            cac_khoan_dau_tu_tc_ngan_han=get_balance("121"),
            cac_khoan_phai_thu_ngan_han=get_balance("131"),
            hang_ton_kho=get_balance("156"),
            tai_san_ngan_han_khac=get_balance("150"),
            tong_tai_san_ngan_han=get_balance("100"),  # 1xx
        )

        tai_san_dai_han = TaiSanDaiHan(
            tai_san_co_dinh_huu_hinh=get_balance("211"),
            tai_san_co_dinh_vo_hinh=get_balance("221"),
            bat_dong_san_dau_tu=get_balance("217"),
            cac_khoan_dau_tu_tc_dai_han=get_balance("221"),
            tai_san_dai_han_khac=get_balance("241"),
            tong_tai_san_dai_han=get_balance("200"),  # 2xx
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
            thue_va_cac_khoan_phai_nop=get_balance("333"),
            phai_tra_ngan_han_khac=get_balance("338"),
            tong_no_ngan_han=get_balance("300"),
        )

        no_dai_han = NoPhaiTraDaiHan(
            vay_no_thue_tai_chinh_dai_han=get_balance("341"),
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
            raise ValueError("Báo cáo tài chính không cân đối!")

        return BaoCaoTinhHinhTaiChinh(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            tai_san=tong_tai_san,
            nguon_von=tong_nguon_von,
        )
