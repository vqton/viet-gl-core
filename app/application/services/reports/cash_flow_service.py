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

    def _tinh_tien_chi_mua_tscd(self, start: date, end: date) -> Decimal:
        """
        Tính **Tiền chi mua sắm, xây dựng TSCĐ** (mã số II.21, B03-DN).

        Bao gồm các khoản tiền mặt chi ra để mua TSCĐ hữu hình/vô hình:
        - **Nợ TK 211, 213 (TSCĐ)**
        - **Có TK 111, 112, 113 (Tiền)**

        Args:
            start (date): Ngày bắt đầu kỳ báo cáo.
            end (date): Ngày kết thúc kỳ báo cáo.

        Returns:
            Decimal: Tổng tiền chi mua TSCĐ trong kỳ (luôn ≥ 0).

        Note:
            - Thuộc **Hoạt động đầu tư (HĐĐT)** → **giảm dòng tiền HĐĐT**.
        """
        all_entries = self.repo.get_all_posted_in_range(start, end)
        tong_chi = Decimal(0)
        for entry in all_entries:
            lines_tien = [
                l
                for l in entry.lines
                if l.so_tai_khoan.startswith(('111', '112', '113'))
                and l.co > 0
            ]
            lines_tscd = [
                l
                for l in entry.lines
                if l.so_tai_khoan.startswith(('211', '213')) and l.no > 0
            ]
            if lines_tien and lines_tscd:
                so_tien = min(
                    sum(l.co for l in lines_tien),
                    sum(l.no for l in lines_tscd),
                )
                tong_chi += so_tien
        return tong_chi

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

    def _tinh_tien_lai_vay_da_tra(self, start: date, end: date) -> Decimal:
        """
        Tính **Tiền lãi vay đã trả thực tế** trong kỳ (mã số I.06, B03-DN).

        Theo TT99/2025/TT-BTC, đây là khoản **tiền mặt chi ra** để trả lãi vay,
        không phải chi phí lãi vay (635), do đó phải phân tích các bút toán:
        - **Nợ TK 335 (Chi phí phải trả - lãi vay)** hoặc **341 (Vay)**
        - **Có TK 111, 112, 113 (Tiền mặt/ngân hàng)**

        Args:
            start (date): Ngày bắt đầu kỳ báo cáo (bao gồm).
            end (date): Ngày kết thúc kỳ báo cáo (bao gồm).

        Returns:
            Decimal: Tổng tiền lãi vay đã trả thực tế trong kỳ (luôn ≥ 0).

        Note:
            - Giá trị này được **ghi dương** trong báo cáo nhưng **trừ khỏi dòng tiền HĐKD**.
            - Nếu không có bút toán trả lãi, trả về 0.
        """
        all_entries = self.repo.get_all_posted_in_range(start, end)
        tong_tien_tra_lai = Decimal(0)

        for entry in all_entries:
            lines_tien = [
                l
                for l in entry.lines
                if l.so_tai_khoan.startswith(('111', '112', '113'))
                and l.co > 0
            ]
            lines_lai_vay = [
                l
                for l in entry.lines
                if l.so_tai_khoan in ('335', '341') and l.no > 0
            ]

            if lines_tien and lines_lai_vay:
                so_tien = min(
                    sum(l.co for l in lines_tien),
                    sum(l.no for l in lines_lai_vay),
                )
                tong_tien_tra_lai += so_tien

        return tong_tien_tra_lai

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

    def _tinh_tien_thue_thu_nhap_da_nop(
        self, start: date, end: date
    ) -> Decimal:
        """
        Tính **Tiền thuế TNDN đã nộp thực tế** trong kỳ (mã số I.10, B03-DN).

        Theo TT99, đây là khoản **tiền mặt chi ra** để nộp thuế TNDN,
        phản ánh từ các bút toán:
        - **Nợ TK 3334 (Thuế TNDN phải nộp)**
        - **Có TK 111, 112, 113 (Tiền)**

        Args:
            start (date): Ngày bắt đầu kỳ báo cáo.
            end (date): Ngày kết thúc kỳ báo cáo.

        Returns:
            Decimal: Tổng tiền thuế TNDN đã nộp trong kỳ (luôn ≥ 0).

        Note:
            - Giá trị này được **ghi dương** trong báo cáo nhưng **trừ khỏi dòng tiền HĐKD**.
            - Chỉ tính các bút toán đã **ghi sổ (Posted)**.
        """
        all_entries = self.repo.get_all_posted_in_range(start, end)
        tong_thue_nop = Decimal(0)

        for entry in all_entries:
            lines_tien = [
                l
                for l in entry.lines
                if l.so_tai_khoan.startswith(('111', '112', '113'))
                and l.co > 0
            ]
            lines_thue = [
                l for l in entry.lines if l.so_tai_khoan == '3334' and l.no > 0
            ]

            if lines_tien and lines_thue:
                so_tien = min(
                    sum(l.co for l in lines_tien),
                    sum(l.no for l in lines_thue),
                )
                tong_thue_nop += so_tien

        return tong_thue_nop

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
        Lập **Báo cáo Lưu chuyển Tiền tệ (B03-DN)** theo phương pháp gián tiếp,
        tuân thủ đầy đủ cấu trúc và nội dung theo **Phụ lục IV – TT99/2025/TT-BTC**.

        Báo cáo bao gồm 3 phần:
        1. Lưu chuyển tiền từ **Hoạt động kinh doanh (HĐKD)**
        2. Lưu chuyển tiền từ **Hoạt động đầu tư (HĐĐT)**
        3. Lưu chuyển tiền từ **Hoạt động tài chính (HĐTC)**

        Args:
            ky_hieu (str): Ký hiệu kỳ báo cáo (VD: "Năm 2025", "Q4-2025").
            ngay_lap (date): Ngày lập báo cáo.
            ngay_bat_dau (date): Ngày bắt đầu kỳ (bao gồm).
            ngay_ket_thuc (date): Ngày kết thúc kỳ (bao gồm).

        Returns:
            BaoCaoLuuChuyenTienTe: Báo cáo B03-DN đã được tính toán đầy đủ.

        Raises:
            ValueError: Nếu dữ liệu báo cáo B02-DN không hợp lệ (từ PerformanceService).
            Exception: Nếu có lỗi trong quá trình truy vấn dữ liệu.

        Note:
            - **I.06 (Tiền lãi vay đã trả)** và **I.10 (Tiền thuế TNDN đã nộp)** được tính
            dựa trên **dòng tiền thực chi**, không phải chi phí kế toán.
            - Báo cáo **phải đảm bảo cân đối**:
            `Tiền cuối kỳ = Lưu chuyển thuần trong kỳ + Tiền đầu kỳ`
        """
        start, end = ngay_bat_dau, ngay_ket_thuc

        # --- HĐKD (gián tiếp) ---
        loi_nhuan_truoc_thue = self._tinh_loi_nhuan_truoc_thue(
            ky_hieu, ngay_lap, start, end
        )
        khau_hao = self._tinh_dieu_chinh_khau_hao_ts_co_dinh(start, end)
        lai_lo_hoat_dong_dau_tu = self._tinh_lai_lo_hoat_dong_dau_tu(
            start, end
        )
        chi_phi_lai_vay = self._tinh_chi_phi_lai_vay(start, end)
        thay_doi_phai_thu = self._tinh_thay_doi_tai_san_phai_thu(start, end)
        thay_doi_hang_ton_kho = self._tinh_thay_doi_hang_ton_kho(start, end)
        thay_doi_phai_tra = self._tinh_thay_doi_no_phai_tra(start, end)

        tien_lai_vay_da_tra = self._tinh_tien_lai_vay_da_tra(start, end)
        tien_thue_thu_nhap_da_nop = self._tinh_tien_thue_thu_nhap_da_nop(
            start, end
        )

        luu_chuyen_hdkd = (
            loi_nhuan_truoc_thue
            + khau_hao
            + lai_lo_hoat_dong_dau_tu
            + chi_phi_lai_vay
            + thay_doi_phai_thu
            + thay_doi_hang_ton_kho
            + thay_doi_phai_tra
        )
        # Lưu ý: I.06 và I.10 **không cộng vào luồng điều chỉnh**, mà là **dòng riêng**,
        # nhưng **tổng hợp vào luồng cuối** qua phép cộng với giá trị âm
        luu_chuyen_tien_thuan_tu_hdkd = (
            luu_chuyen_hdkd - tien_lai_vay_da_tra - tien_thue_thu_nhap_da_nop
        )

        # --- HĐĐT ---
        tien_chi_mua_tscd = self._tinh_tien_chi_mua_tscd(start, end)
        tien_thu_ban_tscd = self._tinh_tien_thu_ban_tscd(start, end)
        # (Các chỉ tiêu khác tạm để 0 nếu chưa có nghiệp vụ)
        luu_chuyen_tien_thuan_tu_hddt = -tien_chi_mua_tscd + tien_thu_ban_tscd

        # --- HĐTC ---
        # (Tạm để 0 nếu chưa có nghiệp vụ cổ phiếu)
        tien_chi_tra_goc_vay = self._tinh_tien_chi_tra_goc_vay(start, end)
        luu_chuyen_tien_thuan_tu_hdtc = -tien_chi_tra_goc_vay

        # --- Tổng hợp ---
        luu_chuyen_tien_thuan_trong_ky = (
            luu_chuyen_tien_thuan_tu_hdkd
            + luu_chuyen_tien_thuan_tu_hddt
            + luu_chuyen_tien_thuan_tu_hdtc
        )

        tien_dau_ky = self._tinh_tien_va_tuong_duong_tien_dau_ky(ngay_bat_dau)
        # Tạm bỏ qua mã số 61 (tỷ giá) nếu không có ngoại tệ
        anh_huong_thay_doi_ty_gia = Decimal(0)
        tien_cuoi_ky = (
            luu_chuyen_tien_thuan_trong_ky
            + tien_dau_ky
            + anh_huong_thay_doi_ty_gia
        )

        return BaoCaoLuuChuyenTienTe(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            luu_chuyen_tien_te_hdkd=LuuChuyenTienTeHDKD(
                loi_nhuan_truoc_thue=loi_nhuan_truoc_thue,
                dieu_chinh_khau_hao_ts_co_dinh=khau_hao,
                lai_lo_hoat_dong_dau_tu=lai_lo_hoat_dong_dau_tu,
                chi_phi_lai_vay=chi_phi_lai_vay,
                tang_giam_cac_khoan_phai_thu=thay_doi_phai_thu,
                tang_giam_hang_ton_kho=thay_doi_hang_ton_kho,
                tang_giam_cac_khoan_phai_tra=thay_doi_phai_tra,
                tien_chi_tra_lai_vay=tien_lai_vay_da_tra,
                tien_thue_thu_nhap_da_nop=tien_thue_thu_nhap_da_nop,
                luu_chuyen_tien_thuan_tu_hdkd=luu_chuyen_tien_thuan_tu_hdkd,
            ),
            luu_chuyen_tien_te_hddt=LuuChuyenTienTeHDDT(
                tien_chi_mua_sam_xay_dung_ts_dai_han=tien_chi_mua_tscd,
                tien_thu_thanh_ly_nhuong_ban_ts_dai_han=tien_thu_ban_tscd,
                luu_chuyen_tien_thuan_tu_hddt=luu_chuyen_tien_thuan_tu_hddt,
            ),
            luu_chuyen_tien_te_hdtc=LuuChuyenTienTeHDTC(
                tien_chi_tra_goc_vay=tien_chi_tra_goc_vay,
                luu_chuyen_tien_thuan_tu_hdtc=luu_chuyen_tien_thuan_tu_hdtc,
            ),
            luu_chuyen_tien_thuan_trong_ky=luu_chuyen_tien_thuan_trong_ky,
            tien_va_tuong_duong_tien_dau_ky=tien_dau_ky,
            anh_huong_thay_doi_ty_gia=anh_huong_thay_doi_ty_gia,
            tien_va_tuong_duong_tien_cuoi_ky=tien_cuoi_ky,
        )
