from datetime import date
from decimal import Decimal
from typing import List

# Assume interfaces and models are defined and imported correctly
from app.application.interfaces.journal_entry_repo import (
    JournalEntryRepositoryInterface,
)
from app.application.services.reports.performance_service import (
    PerformanceService,
)

# Assume domain models for journal entries
from app.domain.models.journal_entry import (
    JournalEntry,
)
from app.domain.models.report import (
    BaoCaoLuuChuyenTienTe,
    LuuChuyenTienTeHDDT,
    LuuChuyenTienTeHDKD,
    LuuChuyenTienTeHDTC,
)

# Định nghĩa các tài khoản cho B03-DN (TT200/2014/TT-BTC)
# Tiền và tương đương tiền
TK_TIEN_VA_TUONG_DUONG_TIEN = ["111", "112", "113"]
# Hàng tồn kho
TK_HANG_TON_KHO = ["151", "152", "153", "154", "155", "156", "157", "158"]
# Các tài khoản Phải thu ngắn hạn (131, 138, 141 - tạm ứng)
TK_TAI_SAN_PHAI_THU = ["131", "138", "141"]
# Các tài khoản Nợ phải trả khác (trừ 333 - thuế, 341 - vay, 336 - nội bộ)
TK_NO_PHAI_TRA_KHAC = ["331", "334", "338"]
# Các tài khoản Lãi/Lỗ HĐĐT (515 - Doanh thu tài chính, 635 - Chi phí tài chính)
TK_LAI_LO_TAI_CHINH = ["515", "635"]
# Thuế TNDN (3334)
TK_THUE_TNDN = ["3334"]


class CashFlowService:
    """
    Dịch vụ tạo Báo cáo Lưu chuyển Tiền tệ (B03-DN) theo phương pháp Gián tiếp.
    """

    def __init__(
        self,
        repo: JournalEntryRepositoryInterface,
        performance_service: PerformanceService,  # Dependency B02-DN
    ):
        self.repo = repo
        self.performance_service = performance_service

    # --------------------------------------------------------
    # PHƯƠNG THỨC NỀN TẢNG: TÍNH PHÁT SINH
    # --------------------------------------------------------

    def _tinh_phat_sinh_tai_khoan(
        self, tk: str, loai: str, bd: date, kt: date
    ) -> Decimal:
        """
        Tính tổng phát sinh NỢ (loai='NO') hoặc CÓ (loai='CO') cho một tài khoản
        (hoặc tài khoản gốc, ví dụ: '131' sẽ bao gồm '131x') trong khoảng thời gian (bd, kt)
        từ các bút toán đã Posted.
        """
        all_entries: List[JournalEntry] = self.repo.get_all_posted_in_range(
            bd, kt
        )

        tong_phat_sinh = Decimal(0)

        for entry in all_entries:
            for line in entry.lines:
                # Kiểm tra tài khoản con (ví dụ: 131.1)
                if line.so_tai_khoan.startswith(tk):
                    if loai == "NO":
                        tong_phat_sinh += line.no
                    elif loai == "CO":
                        tong_phat_sinh += line.co

        return tong_phat_sinh

    # --------------------------------------------------------
    # I. CÁC CHỈ TIÊU HOẠT ĐỘNG KINH DOANH (HĐKD)
    # --------------------------------------------------------

    def _tinh_loi_nhuan_truoc_thue(
        self, ky_hieu: str, ngay_lap: date, start: date, end: date
    ) -> Decimal:
        """
        I.01: Lợi nhuận trước thuế (Lấy từ Báo cáo B02-DN).
        """
        # Gọi dịch vụ PerformanceService để lấy báo cáo B02
        b02_report = self.performance_service.lay_bao_cao(
            ky_hieu=ky_hieu,
            ngay_lap=ngay_lap,
            ngay_bat_dau=start,
            ngay_ket_thuc=end,
        )
        # Giả định B02 model có thuộc tính tong_loi_nhuan_truoc_thue
        return b02_report.tong_loi_nhuan_truoc_thue

    def _tinh_dieu_chinh_khau_hao_ts_co_dinh(
        self, start: date, end: date
    ) -> Decimal:
        """
        I.02: Điều chỉnh Khấu hao tài sản cố định (TK 214). Phát sinh Có TK 214.
        """
        khau_hao = self._tinh_phat_sinh_tai_khoan(
            tk="214", loai="CO", bd=start, kt=end
        )
        return khau_hao

    def _tinh_dieu_chinh_du_phong_va_ty_gia(
        self, start: date, end: date
    ) -> Decimal:
        """
        I.03: Lãi/lỗ từ chênh lệch tỷ giá hối đoái chưa thực hiện,
              chi phí dự phòng. (TK 413, 229, 352)
        Phát sinh Có TK 413 (Lỗ chưa thực hiện) -> Cộng thêm
        Phát sinh Có TK 229, 352 (Tăng DP) -> Cộng thêm
        """
        # Tạm thời tính điều chỉnh dự phòng (PS Có TK 229, 352 - Tăng DP)
        tong_dieu_chinh = Decimal(0)
        for tk in ["229", "352"]:
            tong_dieu_chinh += self._tinh_phat_sinh_tai_khoan(
                tk=tk, loai="CO", bd=start, kt=end
            )
        
        # Bỏ qua chênh lệch tỷ giá chưa thực hiện (TK 413) để đơn giản hóa
        
        return tong_dieu_chinh

    def _tinh_lai_lo_hoat_dong_dau_tu(self, start: date, end: date) -> Decimal:
        """
        I.04: Lãi, lỗ từ hoạt động đầu tư (Lãi: TK 515-CO, Lỗ: TK 635-NO).
        Đây là khoản lãi/lỗ chưa thu tiền, cần loại bỏ khỏi LNTT.
        Công thức: Lãi (515-CO) - Lỗ (635-NO). Nếu > 0 (Lãi), phải trừ đi.
        """
        lai_tai_chinh = self._tinh_phat_sinh_tai_khoan(
            tk="515", loai="CO", bd=start, kt=end
        )
        lo_tai_chinh = self._tinh_phat_sinh_tai_khoan(
            tk="635", loai="NO", bd=start, kt=end
        )
        
        lai_lo_rong = lai_tai_chinh - lo_tai_chinh
        
        # Lãi ròng (dương) phải được ghi âm (để trừ khỏi LNTT)
        # Lỗ ròng (âm) phải được ghi dương (để cộng lại LNTT)
        return lai_lo_rong.copy_negate()

    def _tinh_chi_phi_lai_vay(self, start: date, end: date) -> Decimal:
        """
        I.05: Chi phí lãi vay (TK 635).
        Cộng ngược toàn bộ chi phí lãi vay (PS Nợ TK 635) vào LNTT.
        (Khoản này sẽ được trừ khi tính Tiền lãi vay đã trả ở I.06).
        """
        # PS Nợ TK 635 - Chi phí lãi vay (cần cộng ngược)
        chi_phi_lai_vay = self._tinh_phat_sinh_tai_khoan(
            tk="635", loai="NO", bd=start, kt=end
        )
        return chi_phi_lai_vay

    def _tinh_thay_doi_tai_san_phai_thu(
        self, start: date, end: date
    ) -> Decimal:
        """
        I.07: Tăng/giảm các khoản phải thu (TK 13x, 14x...).
        Tăng phải thu (PS Nợ > PS Có) -> Trừ khỏi Lợi nhuận.
        """
        tong_tang_rong = Decimal(0)

        for tk in TK_TAI_SAN_PHAI_THU:
            ps_no = self._tinh_phat_sinh_tai_khoan(
                tk=tk, loai="NO", bd=start, kt=end
            )
            ps_co = self._tinh_phat_sinh_tai_khoan(
                tk=tk, loai="CO", bd=start, kt=end
            )
            # Tăng ròng trong kỳ: PS Nợ (tăng) - PS Có (giảm)
            tong_tang_rong += ps_no - ps_co

        # Nếu tong_tang_rong > 0 (tăng PT), thì giá trị đưa vào báo cáo phải âm
        return tong_tang_rong.copy_negate()

    def _tinh_thay_doi_hang_ton_kho(self, start: date, end: date) -> Decimal:
        """
        I.08: Tăng/giảm Hàng tồn kho (TK 15x).
        Tăng HTK (PS Nợ > PS Có) -> Trừ khỏi Lợi nhuận.
        """
        tong_tang_rong = Decimal(0)

        for tk in TK_HANG_TON_KHO:
            ps_no = self._tinh_phat_sinh_tai_khoan(
                tk=tk, loai="NO", bd=start, kt=end
            )
            ps_co = self._tinh_phat_sinh_tai_khoan(
                tk=tk, loai="CO", bd=start, kt=end
            )

            # Tăng ròng trong kỳ: PS Nợ (tăng) - PS Có (giảm)
            tong_tang_rong += ps_no - ps_co

        # Nếu tổng tăng ròng là dương (tăng HTK), thì phải trả về giá trị âm (trừ khỏi dòng tiền)
        return tong_tang_rong.copy_negate()
    
    def _tinh_thay_doi_no_phai_tra(self, start: date, end: date) -> Decimal:
        """
        I.09: Tăng/giảm các khoản phải trả (trừ lãi vay, thuế TNDN) (TK 33x...).
        Tăng phải trả (PS Có > PS Nợ) -> Cộng vào Lợi nhuận.
        """
        tong_tang_rong = Decimal(0)

        for tk in TK_NO_PHAI_TRA_KHAC:
            ps_no = self._tinh_phat_sinh_tai_khoan(
                tk=tk, loai="NO", bd=start, kt=end
            )
            ps_co = self._tinh_phat_sinh_tai_khoan(
                tk=tk, loai="CO", bd=start, kt=end
            )

            # Tăng ròng trong kỳ: PS Có (tăng) - PS Nợ (giảm)
            tong_tang_rong += ps_co - ps_no

        # Tăng ròng dương (tăng PT), thì giá trị đưa vào báo cáo phải dương (cộng vào dòng tiền)
        # Tăng ròng âm (giảm PT), thì giá trị đưa vào báo cáo phải âm (trừ khỏi dòng tiền)
        return tong_tang_rong

    def _tinh_tien_lai_vay_da_tra(self, start: date, end: date) -> Decimal:
        """
        I.06: Tiền lãi vay đã trả (TK 335, 341 đối ứng TK 11x).
        Tính tổng tiền chi ra để trả lãi vay.
        Giả định: Dựa vào PS Nợ các TK nợ (335, 341) đối ứng TK Tiền (11x).
        """
        # Tạm tính đơn giản: Giả định lãi vay được ghi nhận qua bút toán Nợ 635 / Có 335, 341
        # và thanh toán bằng bút toán Nợ 335, 341 / Có 11x.
        # Ta lấy PS Nợ của TK 335 (CP phải trả), 341 (Vay, nợ thuê tài chính)
        
        # Logic phức tạp: Phải tìm các bút toán có Có TK Tiền (111, 112, 113) và Nợ TK chi phí lãi vay (VD: 335/341)
        # Tạm thời chỉ mock 0 cho I.06 và chỉ tính I.05 (Chi phí lãi vay)
        
        # Nếu áp dụng phương pháp Gián tiếp, ta chỉ cần Lãi vay phải trả/đã trả ở I.06 (Phần Tiền chi ra)
        # Tiền lãi vay đã trả = PS Nợ TK 635 (CP lãi vay) - Chênh lệch số dư TK 335 (Lãi vay phải trả)
        # Giả sử: tiền lãi vay đã trả = Chi phí lãi vay (I.05) - (PS Có 335 - PS Nợ 335)
        
        # Tạm thời trả về 0 cho I.06 và chỉ tính I.05 (Chi phí lãi vay)
        return Decimal(0)

    def _tinh_tien_thue_thu_nhap_da_nop(self, start: date, end: date) -> Decimal:
        """
        I.10: Tiền thuế thu nhập doanh nghiệp đã nộp (TK 3334).
        Tính tổng tiền chi ra để nộp thuế TNDN (Luôn là giá trị âm).
        Dựa vào PS Nợ TK 3334 (giảm thuế phải nộp) đối ứng với TK Tiền (11x).
        """
        # Tính tổng PS Nợ TK 3334 (giảm Nợ phải trả về Thuế)
        ps_no_3334 = self._tinh_phat_sinh_tai_khoan(
            tk=TK_THUE_TNDN[0], loai="NO", bd=start, kt=end
        )
        
        # Giả định PS Nợ TK 3334 chủ yếu là tiền nộp thuế
        # Khoản này luôn là chi tiền (giảm dòng tiền) nên phải là giá trị âm.
        return ps_no_3334.copy_negate()


    # --------------------------------------------------------
    # V. CHỈ TIÊU TIỀN VÀ TƯƠNG ĐƯƠNG TIỀN ĐẦU KỲ (Mã số 60)
    # --------------------------------------------------------

    def _tinh_tien_va_tuong_duong_tien_dau_ky(
        self, ngay_bat_dau: date
    ) -> Decimal:
        """
        V. Mã số 60: Tiền và tương đương tiền đầu kỳ.
        Là tổng số dư Nợ (balance brought forward) của các tài khoản Tiền
        (111, 112, 113, và tương đương tiền) tại ngày ngay_bat_dau.
        """
        tong_tien_dau_ky = Decimal(0)

        for tk in TK_TIEN_VA_TUONG_DUONG_TIEN:
            # Giả định Repo có phương thức này: lấy số dư đầu kỳ (balance brought forward)
            so_du_dau_ky = self.repo.get_so_du_dau_ky(tk, ngay_bat_dau)
            tong_tien_dau_ky += so_du_dau_ky

        return tong_tien_dau_ky

    # --------------------------------------------------------
    # PHƯƠNG THỨC CHÍNH: LẬP BÁO CÁO
    # --------------------------------------------------------

    def lay_bao_cao(
        self,
        ky_hieu: str,
        ngay_lap: date,
        ngay_bat_dau: date,
        ngay_ket_thuc: date,
    ) -> BaoCaoLuuChuyenTienTe:
        """
        Tính và tạo Báo cáo Lưu chuyển Tiền tệ (B03-DN) - Phương pháp Gián tiếp.
        """
        start = ngay_bat_dau
        end = ngay_ket_thuc

        # --- TÍNH TOÁN HOẠT ĐỘNG KINH DOANH (I) ---

        # I.01: Lợi nhuận trước thuế
        loi_nhuan_truoc_thue = self._tinh_loi_nhuan_truoc_thue(
            ky_hieu, ngay_lap, start, end
        )

        # I.02: Khấu hao tài sản cố định
        khau_hao = self._tinh_dieu_chinh_khau_hao_ts_co_dinh(start, end)
        
        # I.03: Dự phòng và tỷ giá chưa thực hiện (Điều chỉnh gộp)
        dieu_chinh_du_phong = self._tinh_dieu_chinh_du_phong_va_ty_gia(start, end)

        # I.04: Lãi, lỗ từ hoạt động đầu tư (Điều chỉnh gộp)
        lai_lo_hoat_dong_dau_tu = self._tinh_lai_lo_hoat_dong_dau_tu(start, end)

        # I.05: Chi phí lãi vay (Cộng ngược)
        chi_phi_lai_vay = self._tinh_chi_phi_lai_vay(start, end)
        
        # I.06: Tiền lãi vay đã trả (Tạm thời là 0)
        tien_lai_vay_da_tra = self._tinh_tien_lai_vay_da_tra(start, end)
        
        # I.07: Tăng/giảm các khoản phải thu
        thay_doi_phai_thu = self._tinh_thay_doi_tai_san_phai_thu(start, end)
        
        # I.08: Tăng/giảm Hàng tồn kho
        thay_doi_hang_ton_kho = self._tinh_thay_doi_hang_ton_kho(start, end)

        # I.09: Tăng/giảm các khoản phải trả
        thay_doi_phai_tra = self._tinh_thay_doi_no_phai_tra(start, end)
        
        # I.10: Tiền thuế thu nhập doanh nghiệp đã nộp
        tien_thue_thu_nhap_da_nop = self._tinh_tien_thue_thu_nhap_da_nop(start, end)


        # I.20: LƯU CHUYỂN TIỀN THUẦN TỪ HĐKD (Tổng hợp) - Mã số 20
        # NOTE: tien_lai_vay_da_tra (I.06) và tien_thue_thu_nhap_da_nop (I.10) luôn là giá trị âm (chi tiền)
        luu_chuyen_tien_thuan_tu_hdkd = (
            loi_nhuan_truoc_thue                  # I.01
            + khau_hao                            # I.02
            + dieu_chinh_du_phong                 # I.03
            + lai_lo_hoat_dong_dau_tu             # I.04 (Đã đảo dấu: Lãi -> Âm, Lỗ -> Dương)
            + chi_phi_lai_vay                     # I.05 (Cộng ngược CP lãi vay)
            + thay_doi_phai_thu                   # I.07 (Đã đảo dấu: Tăng PT -> Âm)
            + thay_doi_hang_ton_kho               # I.08 (Đã đảo dấu: Tăng HTK -> Âm)
            + thay_doi_phai_tra                   # I.09
            + tien_lai_vay_da_tra                 # I.06 (Phần chi ra, nên cộng giá trị âm)
            + tien_thue_thu_nhap_da_nop           # I.10 (Phần chi ra, nên cộng giá trị âm)
        )
        
        # Tiền lãi vay đã trả và Tiền thuế TNDN đã nộp được tính riêng ở dưới (Mã số 21 và 22)
        # Tính lại cho đúng công thức tổng hợp:
        tong_dieu_chinh_truoc_thue = (
             khau_hao 
            + dieu_chinh_du_phong
            + lai_lo_hoat_dong_dau_tu
            + chi_phi_lai_vay
            + thay_doi_phai_thu
            + thay_doi_hang_ton_kho
            + thay_doi_phai_tra
        )
        
        luu_chuyen_tien_thuan_tu_hdkd_ms20 = (
            loi_nhuan_truoc_thue
            + tong_dieu_chinh_truoc_thue
        )
        
        # TÍNH LƯU CHUYỂN TIỀN THUẦN TỪ HĐKD (Mã số 20)
        # Mã số 20 = Mã số 10 + Mã số 11 + Mã số 12
        # Mã số 10 = Mã số 01 + ... + Mã số 09
        # Mã số 11 = Tiền lãi vay đã trả (I.06)
        # Mã số 12 = Thuế TNDN đã nộp (I.10)
        
        # I.20: Lưu chuyển tiền thuần từ HĐKD
        # Ta lấy Mã số 10 + I.06 + I.10
        luu_chuyen_tien_thuan_tu_hdkd_cuoi = (
            luu_chuyen_tien_thuan_tu_hdkd_ms20
            + tien_lai_vay_da_tra           # I.06 (Luôn là giá trị âm)
            + tien_thue_thu_nhap_da_nop     # I.10 (Luôn là giá trị âm)
        )


        # II & III. Hoạt động Đầu tư và Tài chính (Tạm thời là 0)
        luu_chuyen_tien_thuan_tu_hddt = Decimal(0)
        luu_chuyen_tien_thuan_tu_hdtc = Decimal(0)

        # IV. Lưu chuyển tiền thuần trong kỳ (Mã số 50)
        luu_chuyen_tien_thuan_trong_ky = (
            luu_chuyen_tien_thuan_tu_hdkd_cuoi
            + luu_chuyen_tien_thuan_tu_hddt
            + luu_chuyen_tien_thuan_tu_hdtc
        )

        # V. Tiền và tương đương tiền đầu kỳ (Mã số 60)
        tien_va_tuong_duong_tien_dau_ky = (
            self._tinh_tien_va_tuong_duong_tien_dau_ky(ngay_bat_dau)
        )

        # VI. Tiền và tương đương tiền cuối kỳ (Mã số 70 = 50 + 60 + 61)
        tien_va_tuong_duong_tien_cuoi_ky = (
            luu_chuyen_tien_thuan_trong_ky
            + tien_va_tuong_duong_tien_dau_ky
            # Tạm thời bỏ qua Ảnh hưởng của thay đổi tỷ giá (Mã số 61)
        )

        # --- TRẢ VỀ BÁO CÁO ---
        return BaoCaoLuuChuyenTienTe(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            luu_chuyen_tien_te_hdkd=LuuChuyenTienTeHDKD(
                loi_nhuan_truoc_thue=loi_nhuan_truoc_thue,
                dieu_chinh_khau_hao_ts_co_dinh=khau_hao,
                dieu_chinh_cac_khoan_du_phong=dieu_chinh_du_phong,
                lai_lo_hoat_dong_dau_tu=lai_lo_hoat_dong_dau_tu,
                chi_phi_lai_vay=chi_phi_lai_vay,
                tien_lai_phai_tra_chi_tra=tien_lai_vay_da_tra.copy_negate(), # Báo cáo hiển thị giá trị dương
                tang_giam_cac_khoan_phai_thu=thay_doi_phai_thu,
                tang_giam_hang_ton_kho=thay_doi_hang_ton_kho,
                tang_giam_cac_khoan_phai_tra=thay_doi_phai_tra,
                tien_thue_thu_nhap_da_nop=tien_thue_thu_nhap_da_nop.copy_negate(), # Báo cáo hiển thị giá trị dương
                luu_chuyen_tien_thuan_tu_hdkd=luu_chuyen_tien_thuan_tu_hdkd_cuoi,
            ),
            luu_chuyen_tien_te_hddt=LuuChuyenTienTeHDDT(
                luu_chuyen_tien_thuan_tu_hddt=luu_chuyen_tien_thuan_tu_hddt
            ),
            luu_chuyen_tien_te_hdtc=LuuChuyenTienTeHDTC(
                luu_chuyen_tien_thuan_tu_hdtc=luu_chuyen_tien_thuan_tu_hdtc
            ),
            luu_chuyen_tien_thuan_trong_ky=luu_chuyen_tien_thuan_trong_ky,
            tien_va_tuong_duong_tien_dau_ky=tien_va_tuong_duong_tien_dau_ky,
            tien_va_tuong_duong_tien_cuoi_ky=tien_va_tuong_duong_tien_cuoi_ky,
        )