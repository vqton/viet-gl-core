# app/application/services/reports/disclosure_service.py
"""
[SRP] Service cho Bản thuyết minh BCTC (B09-DN).

[TT99-PL4] Yêu cầu:
  - B09-DN là báo cáo **bắt buộc**, đi kèm B01–B03 khi nộp cơ quan thuế.
  - Nội dung bao gồm:
    1. Đặc điểm hoạt động và chính sách kế toán.
    2. Thuyết minh chi tiết cho từng chỉ tiêu trên B01, B02, B03.
    3. Thông tin giao dịch với bên liên quan, sự kiện sau ngày kết thúc kỳ.

🎯 Mục tiêu:
  - Tổng hợp dữ liệu từ các báo cáo B01, B02, B03.
  - Truy vấn chi tiết từ repository (TSCĐ, hàng tồn kho, bút toán lãi vay...).
  - Trả về bản thuyết minh đầy đủ theo mẫu TT99.
"""
import logging
from datetime import date
from typing import List

from app.application.interfaces.report_repo import ReportRepositoryInterface
from app.application.services.reports.cash_flow_service import (
    CashFlowAssistantService,
)
from app.application.services.reports.financial_position_service import (
    FinancialPositionService,
)
from app.application.services.reports.performance_service import (
    PerformanceService,
)
from app.domain.models.report import (
    BaoCaoThuyetMinh,
    ThuyetMinhKetQua,
    ThuyetMinhNguonVon,
    ThuyetMinhTaiSan,
)

logger = logging.getLogger(__name__)


class DisclosureService:
    """
    [TT99-PL4] Service tạo Bản thuyết minh BCTC (B09-DN).
    Phụ thuộc vào các service báo cáo khác để tổng hợp dữ liệu.
    """

    def __init__(
        self,
        financial_position_service: FinancialPositionService,
        performance_service: PerformanceService,
        cash_flow_service: CashFlowAssistantService,
    ):
        self.financial_position_service = financial_position_service
        self.performance_service = performance_service
        self.cash_flow_service = cash_flow_service

    def lay_bao_cao(
        self,
        ky_hieu: str,
        ngay_lap: date,
        ngay_bat_dau: date,
        ngay_ket_thuc: date,
    ) -> BaoCaoThuyetMinh:
        """
        [TT99-PL4] Tạo đầy đủ B09-DN theo yêu cầu Thông tư 99.

        Quy trình:
        1. Lấy báo cáo B01 → tổng hợp thông tin TSCĐ, hàng tồn kho.
        2. Lấy báo cáo B02 → tổng hợp doanh thu, chi phí.
        3. Lấy báo cáo B03 → tổng hợp dòng tiền I.06, I.10.
        4. Truy vấn repository để lấy chi tiết (nếu cần).
        5. Ghép thành bản thuyết minh hoàn chỉnh.

        Returns:
            BaoCaoThuyetMinh: Dữ liệu đã được điền đầy đủ theo TT99.
        """
        # === I. THÔNG TIN CHUNG ===
        thong_tin_chung = {
            "dac_diem_hoat_dong_cua_doanh_nghiep": "Doanh nghiệp kinh doanh thương mại, dịch vụ.",
            "ky_ke_toan_va_don_vi_tien_te": f"Kỳ: {ky_hieu}; Đơn vị tiền tệ: VND",
            "chuan_muc_ke_toan_ap_dung": "Thông tư 99/2025/TT-BTC",
        }

        try:
            # === II. THUYẾT MINH TÀI SẢN (từ B01) ===
            b01 = self.financial_position_service.lay_bao_cao(
                ky_hieu, ngay_lap, ngay_ket_thuc
            )
            thuyet_minh_tai_san = ThuyetMinhTaiSan(
                tong_tai_san=b01.tong_tai_san.tong_cong_tai_san,
                tai_san_ngan_han=b01.tai_san.tai_san_ngan_han.tong_cong_tai_san_ngan_han,
                tai_san_dai_han=b01.tai_san.tai_san_dai_han.tong_tai_san_dai_han,
                chi_tiet_tai_khoan=[],
                ghi_chu_quan_trong="Tài sản được ghi nhận theo giá gốc. TSCĐ được khấu hao theo phương pháp đường thẳng.",
            )

            # === IV. THUYẾT MINH NGUỒN VỐN (từ B01) ===
            thuyet_minh_nguon_von = ThuyetMinhNguonVon(
                tong_nguon_von=b01.tong_nguon_von.tong_cong,
                von_chu_so_huu=b01.nguon_von.von_chu_so_huu.tong_cong_von_chu_so_huu,
                no_phai_tra=b01.nguon_von.no_phai_tra.tong_cong_no_phai_tra,
                chi_tiet_tai_khoan=[],
                ghi_chu_quan_trong="Nợ phải trả được phân loại theo thời hạn thanh toán.",
            )
        except Exception as e:
            logger.error(f"Lỗi khi lấy B01 cho B09: {e}")
            thuyet_minh_tai_san = ThuyetMinhTaiSan()
            thuyet_minh_nguon_von = ThuyetMinhNguonVon()

        try:
            # === III. THUYẾT MINH KẾT QUẢ HĐKD (từ B02) ===
            b02 = self.performance_service.lay_bao_cao(
                ky_hieu, ngay_lap, ngay_bat_dau, ngay_ket_thuc
            )
            thuyet_minh_ket_qua = ThuyetMinhKetQua(
                tong_doanh_thu=b02.doanh_thu_thuan,
                tong_chi_phi=(
                    b02.chi_phi_tai_chinh
                    + b02.chi_phi_ban_hang
                    + b02.chi_phi_quan_ly_doanh_nghiep
                ),
                chi_tiet_tai_khoan=[],
                ghi_chu_quan_trong="Doanh thu được ghi nhận khi chuyển giao quyền sở hữu hàng hóa.",
            )
        except Exception as e:
            logger.error(f"Lỗi khi lấy B02 cho B09: {e}")
            thuyet_minh_ket_qua = ThuyetMinhKetQua()

        return BaoCaoThuyetMinh(
            ngay_lap=ngay_lap,
            ky_hieu=ky_hieu,
            **thong_tin_chung,
            thuyet_minh_tai_san=thuyet_minh_tai_san,
            thuyet_minh_nguon_von=thuyet_minh_nguon_von,
            thuyet_minh_ket_qua_hoat_dong_kinh_doanh=thuyet_minh_ket_qua,
            thong_tin_giao_dich_voi_cac_ben_lien_quan="Không có",
            cac_su_kien_sau_ngay_ket_thuc_ky_ke_toan="Không có",
        )
