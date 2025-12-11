# tests/test_b03_dong_tien.py
from datetime import date
from decimal import Decimal

import pytest

from app.application.services.reports.cash_flow_service import CashFlowService
from app.domain.models.journal_entry import (
    ButToanLine,
    DetailObjectType,
    GhiSoKeToan,
    TransactionType,
)


@pytest.fixture
def mock_repo(mocker):
    repo = mocker.Mock()
    # Tạo bút toán mẫu: Nợ 335 (lãi vay) / Có 111 (tiền)
    bto_lai_vay = GhiSoKeToan(
        entry_date=date(2025, 12, 10),
        document_type="CT",
        document_number="LV-001",
        description="Trả lãi vay",
        lines=[
            ButToanLine(
                account_number="335",
                amount=Decimal("5000000"),
                transaction_type=TransactionType.DEBIT,
                so_chung_tu_goc="HD-LV-001",
                ngay_chung_tu_goc=date(2025, 12, 10),
                detail_object_type=DetailObjectType.NONE,
            ),
            ButToanLine(
                account_number="111",
                amount=Decimal("5000000"),
                transaction_type=TransactionType.CREDIT,
                so_chung_tu_goc="HD-LV-001",
                ngay_chung_tu_goc=date(2025, 12, 10),
                detail_object_type=DetailObjectType.NONE,
            ),
        ],
    )
    # Tạo bút toán: Nợ 3334 (thuế TNDN) / Có 112 (tiền)
    bto_thue_tndn = GhiSoKeToan(
        entry_date=date(2025, 12, 15),
        document_type="CT",
        document_number="TT-001",
        description="Nộp thuế TNDN",
        lines=[
            ButToanLine(
                account_number="3334",
                amount=Decimal("10000000"),
                transaction_type=TransactionType.DEBIT,
                so_chung_tu_goc="HD-TT-001",
                ngay_chung_tu_goc=date(2025, 12, 15),
                detail_object_type=DetailObjectType.NONE,
            ),
            ButToanLine(
                account_number="112",
                amount=Decimal("10000000"),
                transaction_type=TransactionType.CREDIT,
                so_chung_tu_goc="HD-TT-001",
                ngay_chung_tu_goc=date(2025, 12, 15),
                detail_object_type=DetailObjectType.NONE,
            ),
        ],
    )
    repo.get_all_posted_in_range.return_value = [bto_lai_vay, bto_thue_tndn]
    return repo


def test_b03_tien_lai_vay_da_tra(mock_repo):
    # Arrange
    service = CashFlowService(
        repo=mock_repo, performance_service=mocker.Mock()
    )

    # Act
    b03 = service.lay_bao_cao(
        "Q4-2025", date(2025, 12, 31), date(2025, 10, 1), date(2025, 12, 31)
    )

    # Assert
    assert b03.luu_chuyen_tien_te_hdkd.tien_chi_tra_lai_vay == Decimal(
        "5000000"
    )


def test_b03_tien_thue_thu_nhap_da_nop(mock_repo):
    # Arrange
    service = CashFlowService(
        repo=mock_repo, performance_service=mocker.Mock()
    )

    # Act
    b03 = service.lay_bao_cao(
        "Q4-2025", date(2025, 12, 31), date(2025, 10, 1), date(2025, 12, 31)
    )

    # Assert
    assert b03.luu_chuyen_tien_te_hdkd.tien_thue_thu_nhap_da_nop == Decimal(
        "10000000"
    )
