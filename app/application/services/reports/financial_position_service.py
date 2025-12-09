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
        # Giả định tài khoản chỉ thay đổi số dư cuối kỳ, không tính số dư đầu kỳ (01.01)
        all_accounts = self.repo.get_all_accounts()
        # Giả định _tinh_tat_ca_so_du tính Số dư cuối kỳ (End Date Balance)
        account_balances = self._tinh_tat_ca_so_du(
            all_accounts, date(ngay_ket_thuc.year, 1, 1), ngay_ket_thuc
        )

        def get_balance(so_tai_khoan_goc: str) -> Decimal:
            """Hàm tính Số dư cuối kỳ (Số dư Nợ - Số dư Có) cho TK Tài sản,
            và (Số dư Có - Số dư Nợ) cho TK Nguồn vốn."""
            tong_no = Decimal(0)
            tong_co = Decimal(0)
            for so_tai_khoan, (sd_no, sd_co) in account_balances.items():
                if so_tai_khoan.startswith(so_tai_khoan_goc):
                    tong_no += sd_no
                    tong_co += sd_co

            # Xác định loại tài khoản gốc
            tai_khoan_goc = next(
                (tk for tk in all_accounts if tk.so_tai_khoan == so_tai_khoan_goc),
                None,
            )
            if not tai_khoan_goc:
                # Nếu không tìm thấy TK gốc, cố gắng xác định loại qua đầu số
                first_digit = so_tai_khoan_goc[0]
                if first_digit in "12":  # Tài sản
                    net_balance = tong_no - tong_co
                    return abs(net_balance).quantize(Decimal("0.01"))
                elif first_digit in "34":  # Nguồn vốn
                    net_balance = tong_co - tong_no
                    return abs(net_balance).quantize(Decimal("0.01"))
                return Decimal(0)

            loai_tk = tai_khoan_goc.loai_tai_khoan
            if loai_tk in [LoaiTaiKhoan.TAI_SAN]:
                # Tài sản: Lấy Số dư Nợ (TK 1, 2)
                net_balance = tong_no - tong_co
                return abs(net_balance).quantize(Decimal("0.01"))
            elif loai_tk in [
                LoaiTaiKhoan.NO_PHAI_TRA,
                LoaiTaiKhoan.VON_CHU_SO_HUU,
            ]:
                # Nguồn vốn: Lấy Số dư Có (TK 3, 4)
                net_balance = tong_co - tong_no
                return abs(net_balance).quantize(Decimal("0.01"))
            return Decimal(0)

        # Tính Tài sản Ngắn hạn (I)
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
            # Tổng Tài sản Ngắn hạn (Mã số 100)
            tong_tai_san_ngan_han=tien_va_tg_tien
            + get_balance("121")
            + get_balance("131")
            + get_balance("156")
            + get_balance("150"),
        )

        # Tính Tài sản Dài hạn (II)
        tai_san_co_dinh_huu_hinh = get_balance("211") - get_balance("214")

        tai_san_dai_han = TaiSanDaiHan(
            tai_san_co_dinh_huu_hinh=tai_san_co_dinh_huu_hinh,
            tai_san_co_dinh_vo_hinh=get_balance("221"),
            bat_dong_san_dau_tu=get_balance("217"),
            cac_khoan_dau_tu_tc_dai_han=get_balance("221"),
            tai_san_dai_han_khac=get_balance("241"),
            # Tổng Tài sản Dài hạn (Mã số 200)
            tong_tai_san_dai_han=tai_san_co_dinh_huu_hinh
            + get_balance("221")
            + get_balance("217")
            + get_balance("221")
            + get_balance("241"),
        )

        # Tổng Tài sản (Mã số 270)
        tong_tai_san = TongTaiSan(
            tai_san_ngan_han=tai_san_ngan_han,
            tai_san_dai_han=tai_san_dai_han,
            tong_cong_tai_san=tai_san_ngan_han.tong_tai_san_ngan_han
            + tai_san_dai_han.tong_tai_san_dai_han,
        )

        # Tính nguồn vốn - Nợ Phải trả Ngắn hạn (A)
        no_ngan_han = NoPhaiTraNganHan(
            vay_no_thue_tai_chinh_ngan_han=get_balance("341"),
            phai_tra_ngan_han_nguoi_ban=get_balance("331"),
            thue_va_cac_khoan_phai_nop_nha_nuoc=get_balance("333"),
            phai_tra_ngan_han_khac=get_balance("338"),
            # Tổng Nợ Ngắn hạn (Mã số 300)
            tong_no_ngan_han=get_balance("341")
            + get_balance("331")
            + get_balance("333")
            + get_balance("338"),
        )

        # Tính nguồn vốn - Nợ Phải trả Dài hạn (B)
        no_dai_han = NoPhaiTraDaiHan(
            vay_no_thue_tai_chinh_dai_han=get_balance("341"),
            du_phong_phai_tra_dai_han=Decimal(0),
            # Tổng Nợ Dài hạn (Mã số 400)
            tong_no_dai_han=get_balance("341") + Decimal(0),
        )

        # Tính nguồn vốn - Vốn Chủ sở hữu (C)
        von_chu_so_huu = VonChuSoHuu(
            von_dau_tu_cua_chu_so_huu=get_balance("411"),
            loi_nhuan_sau_thue_chua_phan_phoi=get_balance("421"),
            # Tổng Vốn Chủ sở hữu (Mã số 500)
            tong_von_chu_so_huu=get_balance("411") + get_balance("421"),
        )

        # Tổng Nguồn vốn (Mã số 440)
        tong_nguon_von = TongNguonVon(
            no_phai_tra_ngan_han=no_ngan_han,
            no_phai_tra_dai_han=no_dai_han,
            von_chu_so_huu=von_chu_so_huu,
            tong_cong_nguon_von=no_ngan_han.tong_no_ngan_han
            + no_dai_han.tong_no_dai_han
            + von_chu_so_huu.tong_von_chu_so_huu,
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

    def _tinh_tat_ca_so_du(self, accounts: List[TaiKhoan], start: date, end: date):
        """
        Lấy số dư cuối kỳ (Ending Balance) của tất cả các tài khoản.
        """
        balances = {}
        for tk in accounts:
            # Giả định get_account_balance trả về (SDDK_No, SDDK_Co, PS_No, PS_Co, SDCK_No, SDCK_Co)
            _, _, _, _, sd_ck_no, sd_ck_co = self.repo.get_account_balance(
                tk.so_tai_khoan, start, end
            )
            # Lưu trữ Số dư Cuối kỳ Nợ và Có
            balances[tk.so_tai_khoan] = (sd_ck_no, sd_ck_co)
        return balances
