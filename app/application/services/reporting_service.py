# app/application/services/reporting_service.py
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Import Domain Models cho Reports (Pydantic DTOs)
from app.domain.models.report import (
    BaoCaoTinhHinhTaiChinh,
    BaoCaoKetQuaHDKD,
    BaoCaoLuuChuyenTienTe,
    BaoCaoThuyetMinh,
    TaiSanNganHan,
    TaiSanDaiHan,
    NoPhaiTraNganHan,
    NoPhaiTraDaiHan,
    VonChuSoHuu,
    TienVaCacKhoanTgTien,
    ChiTietTaiKhoan,
    ThuyetMinhTaiSan,
    ThuyetMinhNguonVon,
    ThuyetMinhKetQua,
    TongTaiSan,
    TongNguonVon
)

# Import Domain Models và Enum Kế toán
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine
from app.domain.models.account import TaiKhoan, LoaiTaiKhoan

# Import Repositories
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.infrastructure.repositories.account_repository import AccountRepository

# Import Services khác (nếu cần)
from app.application.services.accounting_period_service import AccountingPeriodService  # Cần cho việc xác định kỳ

# Làm tròn kết quả tính toán đến 2 chữ số thập phân
SCALE = 2
QUANT = Decimal('0.01')

class ReportingService:
    """
    Service chịu trách nhiệm tính toán và lập các báo cáo tài chính.
    """
    def __init__(self, journal_entry_repo: JournalEntryRepository, account_repo: AccountRepository, period_service: AccountingPeriodService = None):
        self.journal_entry_repo = journal_entry_repo
        self.account_repo = account_repo
        self.period_service = period_service  # Dùng để xác định kỳ kế toán (nếu cần)

    def _get_opening_balance(self, so_tai_khoan: str, ngay_bat_dau: date) -> Decimal:
        """
        [PLACEHOLDER] Lấy số dư đầu kỳ của một tài khoản tại ngày bắt đầu.
        Trả về Decimal đã được làm tròn.
        """
        # Giả lập số dư đầu kỳ cho mục đích demo (ví dụ: TK 111 có 100,000,000)
        if so_tai_khoan == '111':
            return Decimal("100000000").quantize(QUANT, rounding=ROUND_HALF_UP)
        return Decimal(0).quantize(QUANT, rounding=ROUND_HALF_UP)

    def _tinh_so_du_tai_khoan_theo_ngay(self, so_tai_khoan: str, ngay_bat_dau: date, ngay_ket_thuc: date) -> Tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
        """
        Tính toán số dư (SDĐK, PS Nợ, PS Có, SDCK Nợ, SDCK Có) cho một tài khoản trong một khoảng thời gian.
        Trả về: (SDĐK, PS Nợ, PS Có, SDCK Nợ, SDCK Có)
        """
        sd_dau_ky = self._get_opening_balance(so_tai_khoan, ngay_bat_dau)

        # Lấy tất cả bút toán đã Posted trong kỳ (repository cung cấp)
        journal_entries = self.journal_entry_repo.get_all_posted_in_range(ngay_bat_dau, ngay_ket_thuc)

        phat_sinh_no = Decimal(0)
        phat_sinh_co = Decimal(0)
        for entry in journal_entries:
            for line in entry.lines:
                if line.so_tai_khoan == so_tai_khoan:
                    phat_sinh_no += (line.no or Decimal(0))
                    phat_sinh_co += (line.co or Decimal(0))

        phat_sinh_no = phat_sinh_no.quantize(QUANT, rounding=ROUND_HALF_UP)
        phat_sinh_co = phat_sinh_co.quantize(QUANT, rounding=ROUND_HALF_UP)

        tai_khoan = self.account_repo.get_by_id(so_tai_khoan)
        if not tai_khoan:
            return sd_dau_ky, phat_sinh_no, phat_sinh_co, Decimal(0).quantize(QUANT), Decimal(0).quantize(QUANT)

        loai_tai_khoan = tai_khoan.loai_tai_khoan

        sd_cuoi_ky_no = Decimal(0)
        sd_cuoi_ky_co = Decimal(0)

        # Loại I: Tài sản/Chi phí/Giá vốn -> Nợ tăng, Có giảm
        if loai_tai_khoan in [LoaiTaiKhoan.TAI_SAN, LoaiTaiKhoan.CHI_PHI, LoaiTaiKhoan.GIA_VON]:
            tong_no = sd_dau_ky + phat_sinh_no
            tong_co = phat_sinh_co
            if tong_no >= tong_co:
                sd_cuoi_ky_no = tong_no - tong_co
            else:
                sd_cuoi_ky_co = tong_co - tong_no

        # Loại II: Nguồn vốn/Doanh thu/Thu nhập khác -> Có tăng, Nợ giảm
        elif loai_tai_khoan in [LoaiTaiKhoan.NO_PHAI_TRA, LoaiTaiKhoan.VON_CHU_SO_HUU, LoaiTaiKhoan.DOANH_THU, LoaiTaiKhoan.THU_NHAP_KHAC]:
            tong_no = phat_sinh_no
            tong_co = sd_dau_ky + phat_sinh_co
            if tong_co >= tong_no:
                sd_cuoi_ky_co = tong_co - tong_no
            else:
                sd_cuoi_ky_no = tong_no - tong_co

        sd_cuoi_ky_no = sd_cuoi_ky_no.quantize(QUANT, rounding=ROUND_HALF_UP)
        sd_cuoi_ky_co = sd_cuoi_ky_co.quantize(QUANT, rounding=ROUND_HALF_UP)

        return sd_dau_ky, phat_sinh_no, phat_sinh_co, sd_cuoi_ky_no, sd_cuoi_ky_co

    # ----------------------------
    # Trial Balance
    # ----------------------------
    def lay_bang_can_doi_so_phat_sinh(self, ky_hieu: str, ngay_lap: date, ngay_bat_dau: date, ngay_ket_thuc: date) -> List[ChiTietTaiKhoan]:
        all_accounts = self.account_repo.get_all()
        result_details: List[ChiTietTaiKhoan] = []

        for tai_khoan in all_accounts:
            sd_dau_ky, ps_no, ps_co, sd_cuoi_ky_no, sd_cuoi_ky_co = self._tinh_so_du_tai_khoan_theo_ngay(
                tai_khoan.so_tai_khoan, ngay_bat_dau, ngay_ket_thuc
            )

            sd_dk_no = Decimal(0)
            sd_dk_co = Decimal(0)
            if tai_khoan.loai_tai_khoan in [LoaiTaiKhoan.TAI_SAN, LoaiTaiKhoan.CHI_PHI, LoaiTaiKhoan.GIA_VON]:
                sd_dk_no = sd_dau_ky
            else:
                sd_dk_co = sd_dau_ky

            if (sd_dk_no == 0 and sd_dk_co == 0 and ps_no == 0 and ps_co == 0):
                continue

            result_details.append(
                ChiTietTaiKhoan(
                    so_tai_khoan=tai_khoan.so_tai_khoan,
                    ten_tai_khoan=tai_khoan.ten_tai_khoan,
                    so_du_dau_ky_no=sd_dk_no,
                    so_du_dau_ky_co=sd_dk_co,
                    phat_sinh_no=ps_no,
                    phat_sinh_co=ps_co,
                    so_du_cuoi_ky_no=sd_cuoi_ky_no,
                    so_du_cuoi_ky_co=sd_cuoi_ky_co,
                )
            )
        return result_details

    # ----------------------------
    # Balance Sheet (B01-DN)
    # ----------------------------
    def lay_bao_cao_tinh_hinh_tai_chinh(self, ky_hieu: str, ngay_lap: date, ngay_ket_thuc: date) -> BaoCaoTinhHinhTaiChinh:
        all_accounts = self.account_repo.get_all()
        account_balances: Dict[str, Tuple[Decimal, Decimal]] = {}
        ngay_dau_nam = date(ngay_ket_thuc.year, 1, 1)

        for tai_khoan in all_accounts:
            _, _, _, sd_cuoi_ky_no, sd_cuoi_ky_co = self._tinh_so_du_tai_khoan_theo_ngay(
                tai_khoan.so_tai_khoan, ngay_dau_nam, ngay_ket_thuc
            )
            account_balances[tai_khoan.so_tai_khoan] = (sd_cuoi_ky_no, sd_cuoi_ky_co)

        def get_balance(so_tai_khoan_tong_hop: str) -> Decimal:
            tong_sd_no = Decimal(0)
            tong_sd_co = Decimal(0)
            for so_tai_khoan, (sd_no, sd_co) in account_balances.items():
                if so_tai_khoan.startswith(so_tai_khoan_tong_hop):
                    tong_sd_no += sd_no
                    tong_sd_co += sd_co

            tai_khoan_goc = self.account_repo.get_by_id(so_tai_khoan_tong_hop)
            if not tai_khoan_goc:
                return Decimal(0).quantize(QUANT)

            loai_tk = tai_khoan_goc.loai_tai_khoan
            if loai_tk in [LoaiTaiKhoan.TAI_SAN]:
                net_balance = tong_sd_no - tong_sd_co
                return abs(net_balance).quantize(QUANT, rounding=ROUND_HALF_UP)
            elif loai_tk in [LoaiTaiKhoan.NO_PHAI_TRA, LoaiTaiKhoan.VON_CHU_SO_HUU]:
                net_balance = tong_sd_co - tong_sd_no
                return abs(net_balance).quantize(QUANT, rounding=ROUND_HALF_UP)
            return Decimal(0).quantize(QUANT)

        # Tien va cac khoan tuong duong tien
        tien_va = TienVaCacKhoanTgTien(
            tien_mat=get_balance('111'),
            tien_gui_ngan_hang=get_balance('112'),
            tien_dang_chuyen=get_balance('113'),
        )
        tien_va.tong_cong = (tien_va.tien_mat + tien_va.tien_gui_ngan_hang + tien_va.tien_dang_chuyen).quantize(QUANT)

        # Tai san ngan han
        cac_khoan_phai_thu_ngan_han = (get_balance('131') + get_balance('138')).quantize(QUANT)
        hang_ton_kho = (get_balance('152') + get_balance('153') + get_balance('155') + get_balance('156')).quantize(QUANT)
        tai_san_ngan_han_khac = get_balance('150')
        tong_tai_san_ngan_han = (tien_va.tong_cong + cac_khoan_phai_thu_ngan_han + hang_ton_kho + tai_san_ngan_han_khac).quantize(QUANT)

        tai_san_ngan_han = TaiSanNganHan(
            tien_va_cac_khoan_tuong_duong_tien=tien_va,
            cac_khoan_dau_tu_tai_chinh_ngan_han=get_balance('121'),
            cac_khoan_phai_thu_ngan_han=cac_khoan_phai_thu_ngan_han,
            hang_ton_kho=hang_ton_kho,
            tai_san_ngan_han_khac=tai_san_ngan_han_khac,
            tong_tai_san_ngan_han=tong_tai_san_ngan_han
        )

        # Tai san dai han
        tai_san_co_dinh_huu_hinh = (get_balance('211') - get_balance('214')).quantize(QUANT)
        tai_san_co_dinh_vo_hinh = get_balance('221')
        bat_dong_san_dau_tu = get_balance('217')
        cac_khoan_dau_tu_tai_chinh_dai_han = get_balance('221')  # nếu khác map lại
        tai_san_dai_han_khac = (get_balance('241') + get_balance('242')).quantize(QUANT)
        tong_tai_san_dai_han = (tai_san_co_dinh_huu_hinh + tai_san_co_dinh_vo_hinh + bat_dong_san_dau_tu + cac_khoan_dau_tu_tai_chinh_dai_han + tai_san_dai_han_khac).quantize(QUANT)

        tai_san_dai_han = TaiSanDaiHan(
            tai_san_co_dinh_huu_hinh=tai_san_co_dinh_huu_hinh,
            tai_san_co_dinh_vo_hinh=tai_san_co_dinh_vo_hinh,
            bat_dong_san_dau_tu=bat_dong_san_dau_tu,
            cac_khoan_dau_tu_tai_chinh_dai_han=cac_khoan_dau_tu_tai_chinh_dai_han,
            tai_san_dai_han_khac=tai_san_dai_han_khac,
            tong_tai_san_dai_han=tong_tai_san_dai_han
        )

        tong_tai_san_total = (tong_tai_san_ngan_han + tong_tai_san_dai_han).quantize(QUANT)

        tong_tai_san = TongTaiSan(
            tai_san_ngan_han=tai_san_ngan_han,
            tai_san_dai_han=tai_san_dai_han,
            tong_cong_tai_san=tong_tai_san_total
        )

        # Nguon von
        phai_tra_ngan_han = (
            get_balance('331') +
            get_balance('333') +  
            get_balance('334') + 
            get_balance('338') + 
            get_balance('341')).quantize(QUANT)
        no_ngan_han_obj = NoPhaiTraNganHan(
            vay_va_no_thue_tai_chinh_ngan_han=get_balance('341'),
            phai_tra_ngan_han_nguoi_ban=get_balance('331'),
            thue_va_cac_khoan_phai_nop_nha_nuoc=get_balance('333'),
            phai_tra_ngan_han_khac=(get_balance('334') + get_balance('338')).quantize(QUANT),
            tong_no_ngan_han=phai_tra_ngan_han
        )

        no_dai_han_obj = NoPhaiTraDaiHan(
            vay_va_no_thue_tai_chinh_dai_han=get_balance('341'),
            du_phong_phai_tra_dai_han=Decimal(0),
            tong_no_dai_han=get_balance('341')
        )

        tong_no_phai_tra = (phai_tra_ngan_han + get_balance('341')).quantize(QUANT)

        von_obj = VonChuSoHuu(
            von_dau_tu_cua_chu_so_huu=get_balance('411'),
            thang_du_von_co_phan=get_balance('412'),
            loi_nhuan_sau_thue_chua_phan_phoi=get_balance('421'),
            tong_von_chu_so_huu=(get_balance('411') + get_balance('421')).quantize(QUANT)
        )

        tong_nguon_von_total = (tong_no_phai_tra + von_obj.tong_von_chu_so_huu).quantize(QUANT)

        tong_nguon_von = TongNguonVon(
            no_phai_tra_ngan_han=no_ngan_han_obj,
            no_phai_tra_dai_han=no_dai_han_obj,
            von_chu_so_huu=von_obj,
            tong_cong_nguon_von=tong_nguon_von_total
        )

        # Kiểm tra cân bằng
        if (tong_tai_san.tong_cong_tai_san - tong_nguon_von.tong_cong_nguon_von).quantize(QUANT, rounding=ROUND_HALF_UP) != Decimal(0):
            print(f"[CẢNH BÁO] Bảng Cân Đối không cân bằng! TS: {tong_tai_san.tong_cong_tai_san}, NV: {tong_nguon_von.tong_cong_nguon_von}")

        return BaoCaoTinhHinhTaiChinh(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            tai_san=tong_tai_san,
            nguon_von=tong_nguon_von
        )

    # ----------------------------
    # Income statement (B02)
    # ----------------------------
    def lay_bao_cao_ket_qua_hdkd(self, ky_hieu: str, ngay_lap: date, ngay_bat_dau: date, ngay_ket_thuc: date) -> BaoCaoKetQuaHDKD:
        def get_ps(so_tai_khoan_goc: str, loai_ps: str) -> Decimal:
            tong = Decimal(0)
            all_accounts = self.account_repo.get_all()
            for tai_khoan in all_accounts:
                if tai_khoan.so_tai_khoan.startswith(so_tai_khoan_goc):
                    _, ps_no, ps_co, _, _ = self._tinh_so_du_tai_khoan_theo_ngay(
                        tai_khoan.so_tai_khoan, ngay_bat_dau, ngay_ket_thuc
                    )
                    if loai_ps == 'NO':
                        tong += ps_no
                    elif loai_ps == 'CO':
                        tong += ps_co
            return tong.quantize(QUANT, rounding=ROUND_HALF_UP)

        doanh_thu_ban_hang = get_ps('511', 'CO')
        giam_tru_doanh_thu = get_ps('521', 'NO')
        doanh_thu_thuan = (doanh_thu_ban_hang - giam_tru_doanh_thu).quantize(QUANT)
        gia_von_hang_ban = get_ps('632', 'NO')
        loi_nhuan_gop = (doanh_thu_thuan - gia_von_hang_ban).quantize(QUANT)
        doanh_thu_hoat_dong_tai_chinh = get_ps('515', 'CO')
        chi_phi_tai_chinh = get_ps('635', 'NO')
        chi_phi_ban_hang = get_ps('641', 'NO')
        chi_phi_quan_ly_doanh_nghiep = get_ps('642', 'NO')
        loi_nhuan_thuan_tu_hdkd = (loi_nhuan_gop + doanh_thu_hoat_dong_tai_chinh - chi_phi_tai_chinh - chi_phi_ban_hang - chi_phi_quan_ly_doanh_nghiep).quantize(QUANT)
        thu_nhap_khac = get_ps('711', 'CO')
        chi_phi_khac = get_ps('811', 'NO')
        loi_nhuan_khac = (thu_nhap_khac - chi_phi_khac).quantize(QUANT)
        tong_loi_nhuan_truoc_thue = (loi_nhuan_thuan_tu_hdkd + loi_nhuan_khac).quantize(QUANT)
        chi_phi_thue_thu_nhap_doanh_nghiep_hien_hanh = get_ps('821', 'NO')
        loi_nhuan_sau_thue = (tong_loi_nhuan_truoc_thue - chi_phi_thue_thu_nhap_doanh_nghiep_hien_hanh).quantize(QUANT)

        return BaoCaoKetQuaHDKD(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            doanh_thu_ban_hang=doanh_thu_ban_hang,
            cac_khoan_giam_tru_doanh_thu=giam_tru_doanh_thu,
            doanh_thu_thuan=doanh_thu_thuan,
            gia_von_hang_ban=gia_von_hang_ban,
            loi_nhuan_gop=loi_nhuan_gop,
            doanh_thu_hoat_dong_tai_chinh=doanh_thu_hoat_dong_tai_chinh,
            chi_phi_tai_chinh=chi_phi_tai_chinh,
            chi_phi_ban_hang=chi_phi_ban_hang,
            chi_phi_quan_ly_doanh_nghiep=chi_phi_quan_ly_doanh_nghiep,
            loi_nhuan_thuan_tu_hdkd=loi_nhuan_thuan_tu_hdkd,
            thu_nhap_khac=thu_nhap_khac,
            chi_phi_khac=chi_phi_khac,
            loi_nhuan_khac=loi_nhuan_khac,
            tong_loi_nhuan_truoc_thue=tong_loi_nhuan_truoc_thue,
            chi_phi_thue_thu_nhap_doanh_nghiep_hien_hanh=chi_phi_thue_thu_nhap_doanh_nghiep_hien_hanh,
            chi_phi_thue_thu_nhap_doanh_nghiep_hoan_lai=Decimal(0),
            loi_nhuan_sau_thue=loi_nhuan_sau_thue
        )

    # ----------------------------
    # Cash flow (placeholder)
    # ----------------------------
    def lay_bao_cao_luu_chuyen_tien_te(self, ky_hieu: str, ngay_lap: date, ngay_bat_dau: date, ngay_ket_thuc: date) -> BaoCaoLuuChuyenTienTe:
        luu_chuyen_tien_te_hdkd = {
            "loi_nhuan_truoc_thue": Decimal(0),
            "khau_hao_tscd": Decimal(0),
            "lai_lo_hoat_dong_dau_tu": Decimal(0),
            "tien_thu_tu_ban_hang_va_cung_cap_dv": Decimal(0),
            "tien_chi_tra_cho_nha_cung_cap_va_nhan_vien": Decimal(0),
            "luu_chuyen_thuan_tu_hdkd": Decimal(0),
        }
        return BaoCaoLuuChuyenTienTe(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            luu_chuyen_tien_te_hdkd=luu_chuyen_tien_te_hdkd,
            luu_chuyen_tien_te_hddt={"luu_chuyen_thuan_tu_hddt": Decimal(0)},
            luu_chuyen_tien_te_hdtc={"luu_chuyen_thuan_tu_hdtc": Decimal(0)},
            luu_chuyen_tien_thuan_trong_ky=Decimal(0),
            tien_va_tuong_duong_tien_dau_ky=self._get_opening_balance('111', ngay_bat_dau) + self._get_opening_balance('112', ngay_bat_dau),
            tien_va_tuong_duong_tien_cuoi_ky=Decimal(0)
        )

    # ----------------------------
    # Notes (placeholder)
    # ----------------------------
    def lay_bao_cao_thuyet_minh(self, ky_hieu: str, ngay_lap: date, ngay_bat_dau: date, ngay_ket_thuc: date) -> BaoCaoThuyetMinh:
        bang_can_doi = self.lay_bang_can_doi_so_phat_sinh(ky_hieu, ngay_lap, ngay_bat_dau, ngay_ket_thuc)

        chi_tiet_131 = [d for d in bang_can_doi if d.so_tai_khoan.startswith('131')]
        thuyet_minh_tai_san = ThuyetMinhTaiSan(
            tong_cong_thuyet_minh=sum([d.so_du_cuoi_ky_no + d.so_du_cuoi_ky_co for d in chi_tiet_131]),
            chi_tiet_tai_khoan=chi_tiet_131,
            ghi_chu_quan_trong="Chi tiết Tài sản"
        )

        chi_tiet_331 = [d for d in bang_can_doi if d.so_tai_khoan.startswith('331')]
        thuyet_minh_nguon_von = ThuyetMinhNguonVon(
            tong_cong_thuyet_minh=sum([d.so_du_cuoi_ky_no + d.so_du_cuoi_ky_co for d in chi_tiet_331]),
            chi_tiet_tai_khoan=chi_tiet_331,
            ghi_chu_quan_trong="Chi tiết Nguồn vốn"
        )

        chi_tiet_doanh_thu = [d for d in bang_can_doi if d.so_tai_khoan.startswith('511')]
        thuyet_minh_ket_qua = ThuyetMinhKetQua(
            tong_doanh_thu=sum([d.phat_sinh_co for d in chi_tiet_doanh_thu]),
            tong_chi_phi=Decimal(0),
            chi_tiet_tai_khoan=chi_tiet_doanh_thu,
            ghi_chu_quan_trong="Chi tiết Doanh thu"
        )

        return BaoCaoThuyetMinh(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            dac_diem_hoat_dong_cua_doanh_nghiep="Hoạt động thương mại/dịch vụ",
            ky_ke_toan_va_don_vi_tien_te=f"Kỳ: {ky_hieu}, Tiền tệ: VND",
            chuan_muc_ke_toan_ap_dung="VAS và TT99/2025/TT-BTC",
            thuyet_minh_tai_san=thuyet_minh_tai_san,
            thuyet_minh_nguon_von=thuyet_minh_nguon_von,
            thuyet_minh_ket_qua_hoat_dong_kinh_doanh=thuyet_minh_ket_qua,
            thong_tin_giao_dich_voi_cac_ben_lien_quan="Không có",
            cac_su_kien_sau_ngay_ket_thuc_ky_ke_toan="Không có"
        )
