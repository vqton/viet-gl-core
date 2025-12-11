# tests/test_b03_full.py
from datetime import date
from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.application.services.reports.cash_flow_service import CashFlowService
from app.domain.models.journal_entry import (
    ButToanLine,
    DetailObjectType,
    GhiSoKeToan,
    TransactionType,
)


@pytest.fixture
def sample_data():
    """Dữ liệu mẫu cho 1 kỳ kế toán (Q4/2025)"""
    return {
        "start": date(2025, 10, 1),
        "end": date(2025, 12, 31),
        "entries": [
            # → Trả lãi vay: Nợ 335 / Có 111 (5.000.000)
            GhiSoKeToan(
                entry_date=date(2025, 11, 15),
                document_type="CT",
                document_number="LV-001",
                description="Trả lãi vay ngân hàng",
                lines=[
                    ButToanLine(
                        so_tai_khoan="335",
                        amount=Decimal("5000000"),
                        transaction_type=TransactionType.DEBIT,
                        so_chung_tu_goc="HD-LV-001",
                        ngay_chung_tu_goc=date(2025, 11, 15),
                        detail_object_type=DetailObjectType.NONE,
                    ),
                    ButToanLine(
                        so_tai_khoan="111",
                        amount=Decimal("5000000"),
                        transaction_type=TransactionType.CREDIT,
                        so_chung_tu_goc="HD-LV-001",
                        ngay_chung_tu_goc=date(2025, 11, 15),
                        detail_object_type=DetailObjectType.NONE,
                    ),
                ],
            ),
            # → Nộp thuế TNDN: Nợ 3334 / Có 112 (10.000.000)
            GhiSoKeToan(
                entry_date=date(2025, 12, 20),
                document_type="CT",
                document_number="TT-001",
                description="Nộp thuế TNDN quý 4",
                lines=[
                    ButToanLine(
                        so_tai_khoan="3334",
                        amount=Decimal("10000000"),
                        transaction_type=TransactionType.DEBIT,
                        so_chung_tu_goc="HD-TT-001",
                        ngay_chung_tu_goc=date(2025, 12, 20),
                        detail_object_type=DetailObjectType.NONE,
                    ),
                    ButToanLine(
                        so_tai_khoan="112",
                        amount=Decimal("10000000"),
                        transaction_type=TransactionType.CREDIT,
                        so_chung_tu_goc="HD-TT-001",
                        ngay_chung_tu_goc=date(2025, 12, 20),
                        detail_object_type=DetailObjectType.NONE,
                    ),
                ],
            ),
            # → Mua TSCĐ: Nợ 211 / Có 111 (50.000.000)
            GhiSoKeToan(
                entry_date=date(2025, 10, 5),
                document_type="CT",
                document_number="MUA-TSCD-001",
                description="Mua máy móc thiết bị",
                lines=[
                    ButToanLine(
                        so_tai_khoan="211",
                        amount=Decimal("50000000"),
                        transaction_type=TransactionType.DEBIT,
                        so_chung_tu_goc="HD-MUA-001",
                        ngay_chung_tu_goc=date(2025, 10, 5),
                        detail_object_type=DetailObjectType.NONE,
                    ),
                    ButToanLine(
                        so_tai_khoan="111",
                        amount=Decimal("50000000"),
                        transaction_type=TransactionType.CREDIT,
                        so_chung_tu_goc="HD-MUA-001",
                        ngay_chung_tu_goc=date(2025, 10, 5),
                        detail_object_type=DetailObjectType.NONE,
                    ),
                ],
            ),
        ],
    }


def test_b03_dong_tien_dung_theo_tt99(sample_data):
    """[TT99-PL4] Kiểm tra B03-DN tính đúng I.06, I.10, II.21"""
    # Arrange
    mock_repo = Mock()
    mock_repo.get_all_posted_in_range.return_value = sample_data["entries"]
    mock_performance = Mock()
    mock_performance.lay_bao_cao.return_value = Mock(
        tong_loi_nhuan_truoc_thue=Decimal("100000000")
    )

    service = CashFlowService(
        repo=mock_repo, performance_service=mock_performance
    )

    # Act
    b03 = service.lay_bao_cao(
        ky_hieu="Q4-2025",
        ngay_lap=date(2025, 12, 31),
        ngay_bat_dau=sample_data["start"],
        ngay_ket_thuc=sample_data["end"],
    )

    # Assert
    assert b03.luu_chuyen_tien_te_hdkd.tien_chi_tra_lai_vay == Decimal(
        "5000000"
    )  # I.06
    assert b03.luu_chuyen_tien_te_hdkd.tien_thue_thu_nhap_da_nop == Decimal(
        "10000000"
    )  # I.10
    assert (
        b03.luu_chuyen_tien_te_hddt.tien_chi_mua_sam_xay_dung_ts_dai_han
        == Decimal("50000000")
    )  # II.21

    # Kiểm tra tổng lưu chuyển tiền thuần
    luu_chuyen_hdkd = b03.luu_chuyen_tien_te_hdkd.luu_chuyen_tien_thuan_tu_hdkd
    luu_chuyen_hddt = b03.luu_chuyen_tien_te_hddt.luu_chuyen_tien_thuan_tu_hddt
    luu_chuyen_hdtc = b03.luu_chuyen_tien_te_hdtc.luu_chuyen_tien_thuan_tu_hdtc

    assert (
        b03.luu_chuyen_tien_thuan_trong_ky
        == luu_chuyen_hdkd + luu_chuyen_hddt + luu_chuyen_hdtc
    )
