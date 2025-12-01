from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from pydantic import BaseModel
# Import Domain Models cho Reports
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
    ThuyetMinhKetQua
)

# Import Domain Models và Enum Kế toán
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine
from app.domain.models.account import TaiKhoan, LoaiTaiKhoan

# Import Repositories
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.infrastructure.repositories.account_repository import AccountRepository

# Import Services khác (nếu cần)
from app.application.services.accounting_period_service import AccountingPeriodService # Cần cho việc xác định kỳ

# Làm tròn kết quả tính toán đến 2 chữ số thập phân
SCALE = 2

class ReportingService:
    """
    Service chịu trách nhiệm tính toán và lập các báo cáo tài chính.
    """
    def __init__(self, journal_entry_repo: JournalEntryRepository, account_repo: AccountRepository, period_service: AccountingPeriodService):
        self.journal_entry_repo = journal_entry_repo
        self.account_repo = account_repo
        self.period_service = period_service # Dùng để xác định kỳ kế toán

    def _get_opening_balance(self, so_tai_khoan: str, ngay_bat_dau: date) -> Decimal:
        """
        [PLACEHOLDER] Lấy số dư đầu kỳ của một tài khoản tại ngày bắt đầu.
        Trong hệ thống thực tế:
        - Số dư đầu kỳ của tài khoản Tài sản/Nguồn vốn là số dư cuối kỳ của kỳ trước.
        - Số dư đầu kỳ của tài khoản Doanh thu/Chi phí là 0 (vì chúng đã được kết chuyển).
        - Cần truy vấn bảng số dư đầu kỳ hoặc kết quả khóa sổ.
        
        Tạm thời trả về 0 cho tất cả, hoặc 1 giá trị mẫu nếu cần demo.
        """
        # Giả lập số dư đầu kỳ cho mục đích demo (ví dụ: TK 111 có 100,000,000)
        if so_tai_khoan == '111':
            return Decimal("100000000").quantize(Decimal(f'0.01'), rounding=ROUND_HALF_UP)
        return Decimal(0).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    def _tinh_so_du_tai_khoan_theo_ngay(self, so_tai_khoan: str, ngay_bat_dau: date, ngay_ket_thuc: date) -> Tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
        """
        Tính toán số dư (SDĐK, PS Nợ, PS Có, SDCK Nợ, SDCK Có) cho một tài khoản trong một khoảng thời gian.
        
        Trả về: (SDĐK, PS Nợ, PS Có, SDCK Nợ, SDCK Có)
        """
        # 1. Lấy số dư đầu kỳ
        sd_dau_ky = self._get_opening_balance(so_tai_khoan, ngay_bat_dau)
        
        # 2. Lấy tất cả bút toán đã Posted trong kỳ
        journal_entries = self.journal_entry_repo.get_all_posted_in_range(ngay_bat_dau, ngay_ket_thuc)

        phat_sinh_no = Decimal(0)
        phat_sinh_co = Decimal(0)

        for entry in journal_entries:
            for line in entry.lines:
                if line.so_tai_khoan == so_tai_khoan:
                    phat_sinh_no += line.no
                    phat_sinh_co += line.co
        
        # Làm tròn phát sinh
        phat_sinh_no = phat_sinh_no.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        phat_sinh_co = phat_sinh_co.quantize(Decimal(f'0.01'), rounding=ROUND_HALF_UP)

        # 3. Tính số dư cuối kỳ
        tai_khoan = self.account_repo.get_by_id(so_tai_khoan)
        if not tai_khoan:
            # Nếu tài khoản không tồn tại, trả về 0
            return sd_dau_ky, phat_sinh_no, phat_sinh_co, Decimal(0), Decimal(0)

        loai_tai_khoan = tai_khoan.loai_tai_khoan

        sd_cuoi_ky_no = Decimal(0)
        sd_cuoi_ky_co = Decimal(0)

        # Tài khoản loại I (Nợ tăng/Có giảm - Tài sản, Chi phí)
        if loai_tai_khoan in [LoaiTaiKhoan.TAI_SAN, LoaiTaiKhoan.CHI_PHI, LoaiTaiKhoan.GIA_VON]:
            tong_no = sd_dau_ky + phat_sinh_no
            tong_co = phat_sinh_co
            
            if tong_no >= tong_co:
                sd_cuoi_ky_no = tong_no - tong_co
            else:
                sd_cuoi_ky_co = tong_co - tong_no
        
        # Tài khoản loại II (Có tăng/Nợ giảm - Nguồn vốn, Doanh thu)
        elif loai_tai_khoan in [LoaiTaiKhoan.NO_PHAI_TRA, LoaiTaiKhoan.VON_CHU_SO_HUU, LoaiTaiKhoan.DOANH_THU, LoaiTaiKhoan.THU_NHAP_KHAC]:
            tong_no = phat_sinh_no
            tong_co = sd_dau_ky + phat_sinh_co

            if tong_co >= tong_no:
                sd_cuoi_ky_co = tong_co - tong_no
            else:
                sd_cuoi_ky_no = tong_no - tong_co
        
        # Làm tròn số dư cuối kỳ
        sd_cuoi_ky_no = sd_cuoi_ky_no.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        sd_cuoi_ky_co = sd_cuoi_ky_co.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        return sd_dau_ky, phat_sinh_no, phat_sinh_co, sd_cuoi_ky_no, sd_cuoi_ky_co

    # =========================================================================
    # Báo cáo chi tiết: Sổ Cái (General Ledger)
    # =========================================================================

    def lay_so_cai(self, so_tai_khoan: str, ngay_bat_dau: date, ngay_ket_thuc: date) -> Dict:
        """
        Lấy chi tiết Sổ Cái (Sổ Nhật Ký Sổ Cái) cho một tài khoản trong kỳ.
        """
        tai_khoan = self.account_repo.get_by_id(so_tai_khoan)
        if not tai_khoan:
            raise ValueError(f"Tài khoản {so_tai_khoan} không tồn tại.")

        # Lấy số dư đầu kỳ
        sd_dau_ky, ps_no, ps_co, sd_cuoi_ky_no, sd_cuoi_ky_co = self._tinh_so_du_tai_khoan_theo_ngay(
            so_tai_khoan, ngay_bat_dau, ngay_ket_thuc
        )

        # Lấy chi tiết các bút toán phát sinh
        journal_entries = self.journal_entry_repo.get_all_posted_in_range(ngay_bat_dau, ngay_ket_thuc)
        
        details = []
        # Duyệt qua các bút toán để trích xuất thông tin dòng
        for entry in journal_entries:
            for line in entry.lines:
                if line.so_tai_khoan == so_tai_khoan:
                    # Tìm tài khoản đối ứng (TK còn lại trong bút toán)
                    tai_khoan_doi_ung = [
                        l.so_tai_khoan for l in entry.lines if l.so_tai_khoan != so_tai_khoan
                    ]
                    # Nếu chỉ có 2 dòng Nợ/Có, thì TK đối ứng là TK còn lại.
                    # Nếu có nhiều dòng, TK đối ứng là "Nhiều tài khoản"
                    so_tai_khoan_doi_ung = tai_khoan_doi_ung[0] if len(entry.lines) == 2 else "Nhiều TK"
                    
                    details.append({
                        "ngay_ct": entry.ngay_ct,
                        "so_phieu": entry.so_phieu,
                        "mo_ta_chung": entry.mo_ta,
                        "so_tai_khoan_doi_ung": so_tai_khoan_doi_ung,
                        "phat_sinh_no": line.no,
                        "phat_sinh_co": line.co,
                        "mo_ta_line": line.mo_ta or entry.mo_ta
                    })

        return {
            "so_tai_khoan": so_tai_khoan,
            "ten_tai_khoan": tai_khoan.ten_tai_khoan,
            "ngay_bat_dau": ngay_bat_dau,
            "ngay_ket_thuc": ngay_ket_thuc,
            "so_du_dau_ky": sd_dau_ky,
            "tong_phat_sinh_no": ps_no,
            "tong_phat_sinh_co": ps_co,
            "so_du_cuoi_ky_no": sd_cuoi_ky_no,
            "so_du_cuoi_ky_co": sd_cuoi_ky_co,
            "chi_tiet_phat_sinh": details
        }
    
    # =========================================================================
    # Báo cáo tổng hợp: Bảng Cân đối Số phát sinh (Trial Balance)
    # =========================================================================

    def lay_bang_can_doi_so_phat_sinh(self, ky_hieu: str, ngay_lap: date, ngay_bat_dau: date, ngay_ket_thuc: date) -> List[ChiTietTaiKhoan]:
        """
        Tính toán và trả về Bảng Cân đối Số phát sinh cho một kỳ.
        """
        all_accounts = self.account_repo.get_all()
        result_details: List[ChiTietTaiKhoan] = []

        for tai_khoan in all_accounts:
            # 1. Bỏ qua các tài khoản tổng hợp cấp cao nếu đã có tài khoản cấp con (tùy thuộc yêu cầu chi tiết)
            if tai_khoan.la_tai_khoan_tong_hop and len(tai_khoan.so_tai_khoan) == 3: # Chỉ lấy chi tiết nếu là TK cấp 2 trở lên
                 # Trong bản đơn giản, ta chỉ lấy các tài khoản cấp 1 và cấp 2 để tính tổng,
                 # nhưng khi hiển thị thường chỉ hiển thị TK cấp chi tiết.
                 # Để đơn giản, ta tính toán trên tất cả TK và gom nhóm nếu cần.
                 pass

            # 2. Tính số dư và phát sinh
            sd_dau_ky, ps_no, ps_co, sd_cuoi_ky_no, sd_cuoi_ky_co = self._tinh_so_du_tai_khoan_theo_ngay(
                tai_khoan.so_tai_khoan, ngay_bat_dau, ngay_ket_thuc
            )

            # 3. Tạo ChiTietTaiKhoan DTO
            # Chuyển số dư đầu kỳ thành Nợ/Có
            # Giả sử TK loại Tài sản/Chi phí có SDĐK Nợ, còn lại là SDĐK Có (Đơn giản hóa)
            sd_dk_no = Decimal(0)
            sd_dk_co = Decimal(0)
            if tai_khoan.loai_tai_khoan in [LoaiTaiKhoan.TAI_SAN, LoaiTaiKhoan.CHI_PHI, LoaiTaiKhoan.GIA_VON]:
                sd_dk_no = sd_dau_ky
            else:
                sd_dk_co = sd_dau_ky
            
            # Xử lý trường hợp Tài khoản lưỡng tính (ví dụ 131, 331) - Cần logic phức tạp hơn
            # Tạm thời, nếu SDĐK = 0 và PS Nợ/Có đều bằng 0, ta bỏ qua không đưa vào báo cáo
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
        
        # NOTE: Bảng Cân đối Số phát sinh cần đảm bảo:
        # Tổng SDĐK Nợ = Tổng SDĐK Có
        # Tổng PS Nợ = Tổng PS Có
        # Tổng SDCK Nợ = Tổng SDCK Có
        return result_details

    # =========================================================================
    # Báo cáo Tài chính: Bảng Cân đối Kế toán (B01-DN)
    # =========================================================================

    def lay_bao_cao_tinh_hinh_tai_chinh(self, ky_hieu: str, ngay_lap: date, ngay_ket_thuc: date) -> BaoCaoTinhHinhTaiChinh:
        """
        Tính toán và trả về Báo cáo tình hình tài chính (Bảng cân đối kế toán - B01-DN).
        Sử dụng số dư cuối kỳ tại ngày_ket_thuc.
        """
        
        # 1. Lấy tất cả tài khoản
        all_accounts = self.account_repo.get_all()
        
        # 2. Tạo Dictionary để lưu số dư cuối kỳ của tất cả tài khoản
        # Key: So_tai_khoan, Value: (SDCK Nợ, SDCK Có)
        account_balances: Dict[str, Tuple[Decimal, Decimal]] = {}
        # Lấy ngày đầu năm để tính số dư đầu kỳ (để đơn giản)
        ngay_dau_nam = date(ngay_ket_thuc.year, 1, 1)

        for tai_khoan in all_accounts:
            # Ta chỉ cần SDCK tại ngày kết thúc
            _, _, _, sd_cuoi_ky_no, sd_cuoi_ky_co = self._tinh_so_du_tai_khoan_theo_ngay(
                tai_khoan.so_tai_khoan, ngay_dau_nam, ngay_ket_thuc
            )
            account_balances[tai_khoan.so_tai_khoan] = (sd_cuoi_ky_no, sd_cuoi_ky_co)
        
        def get_balance(so_tai_khoan_tong_hop: str) -> Decimal:
            """
            Hàm tiện ích để tổng hợp số dư cuối kỳ (Net Balance)
            Net Balance = (SDCK Nợ - SDCK Có) | (SDCK Có - SDCK Nợ) tùy loại TK
            """
            tong_sd_no = Decimal(0)
            tong_sd_co = Decimal(0)
            
            # Lấy tất cả TK con có cùng prefix
            for so_tai_khoan, (sd_no, sd_co) in account_balances.items():
                if so_tai_khoan.startswith(so_tai_khoan_tong_hop):
                    tong_sd_no += sd_no
                    tong_sd_co += sd_co
            
            # Xác định loại TK tổng hợp để tính số dư ròng.
            tai_khoan_goc = self.account_repo.get_by_id(so_tai_khoan_tong_hop)
            if not tai_khoan_goc:
                return Decimal(0)

            loai_tk = tai_khoan_goc.loai_tai_khoan
            
            # Tài sản (1xx, 2xx) -> Lấy SDCK Nợ ròng (Nợ - Có)
            if loai_tk in [LoaiTaiKhoan.TAI_SAN]:
                # Xử lý các TK loại trừ (Contra Accounts) như 214, 229, 352
                # Tạm thời chỉ cần lấy SD ròng (Nợ - Có) nếu là Tài sản
                # Số dư ròng > 0: Nợ; Số dư ròng < 0: Có
                net_balance = tong_sd_no - tong_sd_co
                # Bảng Cân đối chỉ lấy giá trị tuyệt đối cho từng chỉ tiêu
                return abs(net_balance)

            # Nguồn vốn (3xx, 4xx) -> Lấy SDCK Có ròng (Có - Nợ)
            elif loai_tk in [LoaiTaiKhoan.NO_PHAI_TRA, LoaiTaiKhoan.VON_CHU_SO_HUU]:
                net_balance = tong_sd_co - tong_sd_no
                return abs(net_balance)
            
            return Decimal(0)

        # 3. Tính toán các chỉ tiêu chi tiết theo B01-DN (Đơn giản hóa)
        
        # --- A. TÀI SẢN ---
        # A.I. Tài sản ngắn hạn (Mã 100)
        tien_va_tg_tien = TienVaCacKhoanTgTien(
            tien_mat=get_balance('111'),
            tien_gui_ngan_hang=get_balance('112'),
            tien_gui_ngan_han_khac=get_balance('113')
        )
        # Mã 120 (Phải thu ngắn hạn)
        phai_thu_ngan_han = get_balance('131') + get_balance('138') 
        # Mã 140 (Hàng tồn kho)
        hang_ton_kho = get_balance('152') + get_balance('153') + get_balance('155') + get_balance('156')
        
        # --- SỬA LỖI TẠI ĐÂY ---
        # 1. Tính giá trị cho Tài sản ngắn hạn khác (ví dụ TK 141, 171...)
        tai_san_ngan_han_khac_value = get_balance('141') + get_balance('171')
        
        # 👇 BỎ `tien_gui_ngan_han_khac` NẾU FIELD NÀY KHÔNG TỒN TẠI TRONG DTO
        tong_tai_san_ngan_han = (        tien_va_tg_tien.tien_mat + tien_va_tg_tien.tien_gui_ngan_hang +  # ✅ CHỈ GIỮ CÁC FIELD CÓ TRONG DTO
        phai_thu_ngan_han + hang_ton_kho + tai_san_ngan_han_khac_value
        )
        
        tai_san_ngan_han = TaiSanNganHan(
            tien_va_cac_khoan_tuong_duong_tien=tien_va_tg_tien,
            cac_khoan_dau_tu_tai_chinh_ngan_han=get_balance('121'),
            phai_thu_ngan_han=phai_thu_ngan_han,
            hang_ton_kho=hang_ton_kho,
            tai_san_ngan_han_khac=get_balance('150')
        )

        # A.II. Tài sản dài hạn (Mã 200)
        tai_san_co_dinh_huu_hinh = get_balance('211') - get_balance('214') # Nguyên giá - Hao mòn
        
        tong_tai_san_dai_han = tai_san_co_dinh_huu_hinh + get_balance('221') + get_balance('241') + get_balance('242')
        
        tai_san_dai_han = TaiSanDaiHan(
            tai_san_co_dinh_huu_hinh=tai_san_co_dinh_huu_hinh,
            cac_khoan_dau_tu_tai_chinh_dai_han=get_balance('221'),
            bat_dong_san_dau_tu=get_balance('217'),
            tai_san_dai_han_khac=get_balance('241') + get_balance('242')
        )

        # Tổng cộng Tài sản (Mã 270)
        tong_tai_san = tong_tai_san_ngan_han + tong_tai_san_dai_han

        # --- B. NGUỒN VỐN ---
        
        # B.I. Nợ phải trả (Mã 300)
        # Nợ ngắn hạn (Mã 310)
        phai_tra_ngan_han = get_balance('331') + get_balance('334') + get_balance('338') + get_balance('341')
        
        no_phai_tra_ngan_han = NoPhaiTraNganHan(
            vay_va_no_thue_tai_chinh_ngan_han=get_balance('341'),
            phai_tra_nguoi_ban_ngan_han=get_balance('331'),
            thue_va_cac_khoan_phai_nop_nha_nuoc=get_balance('333'),
            phai_tra_ngan_han_khac=get_balance('334') + get_balance('338')
        )
        
        tong_no_phai_tra_ngan_han = phai_tra_ngan_han + get_balance('333')
        
        # Nợ dài hạn (Mã 330) - Giả sử đơn giản chỉ có 341 dài hạn
        no_phai_tra_dai_han = NoPhaiTraDaiHan(
            vay_va_no_thue_tai_chinh_dai_han=get_balance('341')
        )
        tong_no_phai_tra_dai_han = get_balance('341') # Lấy phần dài hạn

        tong_no_phai_tra = tong_no_phai_tra_ngan_han + tong_no_phai_tra_dai_han

        # B.II. Vốn chủ sở hữu (Mã 400)
        von_chu_so_huu = VonChuSoHuu(
            von_dau_tu_cua_chu_so_huu=get_balance('411'),
            thang_du_von_co_phan=get_balance('412'),
            loi_nhuan_sau_thue_chua_phan_phoi=get_balance('421') # Lãi/Lỗ lũy kế
        )
        
        tong_von_chu_so_huu = get_balance('411') + get_balance('421')

        # Tổng cộng Nguồn vốn (Mã 440)
        tong_nguon_von = tong_no_phai_tra + tong_von_chu_so_huu
        
        # Kiểm tra Cân bằng: TỔNG TÀI SẢN (270) = TỔNG NGUỒN VỐN (440)
        if (tong_tai_san - tong_nguon_von).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) != Decimal(0):
            print(f"[CẢNH BÁO] Bảng Cân Đối không cân bằng! TS: {tong_tai_san}, NV: {tong_nguon_von}")

        # 4. Tạo và trả về DTO BaoCaoTinhHinhTaiChinh
        return BaoCaoTinhHinhTaiChinh(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            tai_san_ngan_han=tai_san_ngan_han,
            tai_san_dai_han=tai_san_dai_han,
            tong_tai_san=tong_tai_san,
            no_phai_tra_ngan_han=no_phai_tra_ngan_han,
            no_phai_tra_dai_han=no_phai_tra_dai_han,
            tong_no_phai_tra=tong_no_phai_tra,
            von_chu_so_huu=von_chu_so_huu,
            tong_nguon_von=tong_nguon_von,
        )

    # =========================================================================
    # Báo cáo Tài chính: Báo cáo Kết quả Hoạt động Kinh doanh (B02-DN)
    # =========================================================================

    def lay_bao_cao_ket_qua_hdkd(self, ky_hieu: str, ngay_lap: date, ngay_bat_dau: date, ngay_ket_thuc: date) -> BaoCaoKetQuaHDKD:
        """
        Tính toán và trả về Báo cáo kết quả hoạt động kinh doanh (B02-DN).
        Sử dụng số phát sinh trong kỳ từ ngay_bat_dau đến ngay_ket_thuc.
        """
        
        # Hàm tiện ích để lấy tổng phát sinh Nợ hoặc Có trong kỳ của một nhóm TK
        def get_ps(so_tai_khoan_goc: str, loai_ps: str) -> Decimal:
            """loai_ps: 'NO' hoặc 'CO'"""
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
            return tong.quantize(Decimal(f'1e-{-SCALE}'), rounding=ROUND_HALF_UP)

        # 1. DOANH THU (Mã 01, TK 511)
        doanh_thu_ban_hang = get_ps('511', 'CO')

        # 2. Các khoản giảm trừ doanh thu (Mã 02, TK 521)
        # Giảm trừ là TK loại trừ, có số dư Nợ, nên lấy PS Nợ
        giam_tru_doanh_thu = get_ps('521', 'NO') 

        # 3. DOANH THU THUẦN (Mã 10) = Mã 01 - Mã 02
        doanh_thu_thuan = doanh_thu_ban_hang - giam_tru_doanh_thu
        
        # 4. Giá vốn hàng bán (Mã 11, TK 632)
        gia_von_hang_ban = get_ps('632', 'NO') # PS Nợ của TK 632 (trước kết chuyển)

        # 5. Lợi nhuận gộp (Mã 20) = Mã 10 - Mã 11
        loi_nhuan_gop = doanh_thu_thuan - gia_von_hang_ban

        # 6. Doanh thu hoạt động tài chính (Mã 21, TK 515)
        doanh_thu_tai_chinh = get_ps('515', 'CO')

        # 7. Chi phí tài chính (Mã 22, TK 635)
        chi_phi_tai_chinh = get_ps('635', 'NO')

        # 8. Chi phí bán hàng (Mã 25, TK 641)
        chi_phi_ban_hang = get_ps('641', 'NO')

        # 9. Chi phí quản lý doanh nghiệp (Mã 26, TK 642)
        chi_phi_quan_ly_doanh_nghiep = get_ps('642', 'NO')

        # 10. Lợi nhuận thuần từ HĐKD (Mã 30) = 20 + 21 - 22 - 25 - 26
        loi_nhuan_thuan_hdkd = loi_nhuan_gop + doanh_thu_tai_chinh - chi_phi_tai_chinh - chi_phi_ban_hang - chi_phi_quan_ly_doanh_nghiep
        
        # 11. Thu nhập khác (Mã 31, TK 711)
        thu_nhap_khac = get_ps('711', 'CO')

        # 12. Chi phí khác (Mã 32, TK 811)
        chi_phi_khac = get_ps('811', 'NO')

        # 13. Lợi nhuận khác (Mã 40) = Mã 31 - Mã 32
        loi_nhuan_khac = thu_nhap_khac - chi_phi_khac

        # 14. Tổng lợi nhuận kế toán trước thuế (Mã 50) = Mã 30 + Mã 40
        loi_nhuan_truoc_thue = loi_nhuan_thuan_hdkd + loi_nhuan_khac

        # 15. Chi phí thuế thu nhập doanh nghiệp (Mã 51, TK 821)
        thue_thu_nhap_doanh_nghiep = get_ps('821', 'NO') # Giả sử chỉ lấy PS Nợ

        # 16. Lợi nhuận sau thuế (Mã 60) = Mã 50 - Mã 51
        loi_nhuan_sau_thue = loi_nhuan_truoc_thue - thue_thu_nhap_doanh_nghiep
        
        # 17. Đảm bảo tất cả được làm tròn
        doanh_thu_thuan = doanh_thu_thuan.quantize(Decimal(f'1e-{-SCALE}'), rounding=ROUND_HALF_UP)
        loi_nhuan_sau_thue = loi_nhuan_sau_thue.quantize(Decimal(f'1e-{-SCALE}'), rounding=ROUND_HALF_UP)

        # 18. Tạo và trả về DTO
        return BaoCaoKetQuaHDKD(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            doanh_thu_thuan=doanh_thu_thuan,
            gia_von_hang_ban=gia_von_hang_ban,
            loi_nhuan_gop=loi_nhuan_gop,
            doanh_thu_tai_chinh=doanh_thu_tai_chinh,
            chi_phi_tai_chinh=chi_phi_tai_chinh,
            chi_phi_ban_hang=chi_phi_ban_hang,
            chi_phi_quan_ly_doanh_nghiep=chi_phi_quan_ly_doanh_nghiep,
            loi_nhuan_thuan_hdkd=loi_nhuan_thuan_hdkd,
            thu_nhap_khac=thu_nhap_khac,
            chi_phi_khac=chi_phi_khac,
            loi_nhuan_khac=loi_nhuan_khac,
            loi_nhuan_truoc_thue=loi_nhuan_truoc_thue,
            thue_thu_nhap_doanh_nghiep=thue_thu_nhap_doanh_nghiep,
            loi_nhuan_sau_thue=loi_nhuan_sau_thue
        )

    # =========================================================================
    # Báo cáo Tài chính: Báo cáo Lưu chuyển tiền tệ (B03-DN)
    # =========================================================================
    
    def lay_bao_cao_luu_chuyen_tien_te(self, ky_hieu: str, ngay_lap: date, ngay_bat_dau: date, ngay_ket_thuc: date) -> BaoCaoLuuChuyenTienTe:
        """
        [PLACEHOLDER] Tính toán và trả về Báo cáo lưu chuyển tiền tệ (B03-DN).
        Báo cáo này RẤT phức tạp, đòi hỏi phải phân loại dòng tiền trên từng bút toán (dòng tiền từ HĐKD, HĐTC, HĐQT).
        
        Trong bản đơn giản này, ta chỉ tạo một DTO rỗng/placeholder.
        """
        # Lưu chuyển tiền tệ đòi hỏi phải gắn mã dòng tiền (Cash Flow Code) vào mỗi bút toán.
        
        # Giả lập các chỉ tiêu chính (rỗng)
        luu_chuyen_tien_te_hdkd = {
            "loi_nhuan_truoc_thue": Decimal(0),
            "khau_hao_tscd": Decimal(0),
            "lai_lo_hoat_dong_dau_tu": Decimal(0),
            # ... các dòng khác
            "tien_thu_tu_ban_hang_va_cung_cap_dv": Decimal(0),
            "tien_chi_tra_cho_nha_cung_cap_va_nhan_vien": Decimal(0),
            "luu_chuyen_thuan_tu_hdkd": Decimal(0),
        }
        
        return BaoCaoLuuChuyenTienTe(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            luu_chuyen_tien_te_hdkd=luu_chuyen_tien_te_hdkd,
            luu_chuyen_tien_te_hdtc={"luu_chuyen_thuan_tu_hdtc": Decimal(0)},
            luu_chuyen_tien_te_hdqt={"luu_chuyen_thuan_tu_hdqt": Decimal(0)},
            tien_va_tuong_duong_tien_dau_ky=self._get_opening_balance('111', ngay_bat_dau) + self._get_opening_balance('112', ngay_bat_dau),
            tien_va_tuong_duong_tien_cuoi_ky=Decimal(0) # SDCK TK 111, 112
        )

    # =========================================================================
    # Báo cáo Tài chính: Bản Thuyết minh Báo cáo tài chính (B09-DN)
    # =========================================================================
    
    def lay_bao_cao_thuyet_minh(self, ky_hieu: str, ngay_lap: date, ngay_bat_dau: date, ngay_ket_thuc: date) -> BaoCaoThuyetMinh:
        """
        [PLACEHOLDER] Tạo Bản Thuyết minh Báo cáo tài chính (B09-DN).
        Bao gồm các chi tiết cho các chỉ tiêu quan trọng.
        Ta sẽ sử dụng kết quả từ lay_bang_can_doi_so_phat_sinh.
        """
        bang_can_doi = self.lay_bang_can_doi_so_phat_sinh(ky_hieu, ngay_lap, ngay_bat_dau, ngay_ket_thuc)
        
        # Chỉ tiêu thuyết minh tài sản (VD: Chi tiết Tài khoản 131)
        chi_tiet_131 = [d for d in bang_can_doi if d.so_tai_khoan.startswith('131')]
        thuyet_minh_tai_san = ThuyetMinhTaiSan(
            chi_tiet_tai_khoan_phai_thu=chi_tiet_131,
            chi_tiet_tai_khoan_khac=[] # Placeholder
        )
        
        # Chỉ tiêu thuyết minh nguồn vốn (VD: Chi tiết Tài khoản 331)
        chi_tiet_331 = [d for d in bang_can_doi if d.so_tai_khoan.startswith('331')]
        thuyet_minh_nguon_von = ThuyetMinhNguonVon(
            chi_tiet_tai_khoan_phai_tra=chi_tiet_331,
            chi_tiet_tai_khoan_khac=[] # Placeholder
        )

        # Chỉ tiêu thuyết minh kết quả hoạt động (VD: Chi tiết TK Doanh thu 511)
        chi_tiet_doanh_thu = [d for d in bang_can_doi if d.so_tai_khoan.startswith('511')]
        thuyet_minh_ket_qua = ThuyetMinhKetQua(
            chi_tiet_doanh_thu=chi_tiet_doanh_thu,
            chi_tiet_chi_phi=[] # Placeholder
        )

        return BaoCaoThuyetMinh(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            thuyet_minh_tai_san=thuyet_minh_tai_san,
            thuyet_minh_nguon_von=thuyet_minh_nguon_von,
            thuyet_minh_ket_qua=thuyet_minh_ket_qua,
            # ... các phần khác trong B09-DN
        )