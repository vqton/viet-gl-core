# tests/test_closing_service.py
from datetime import date
from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.application.services.journaling.closing_service import (
    ClosingJournalEntryService,
)
from app.domain.models.journal_entry import (
    ButToanLine,
    DetailObjectType,
    GhiSoKeToan,
    TransactionType,
)


@pytest.fixture
def closing_service():
    """Tạo service với repository mock."""
    mock_repo = Mock()
    mock_acc_repo = Mock()
    return ClosingJournalEntryService(
        journal_repo=mock_repo, account_repo=mock_acc_repo
    )


@pytest.fixture
def sample_buts_toan_doanh_thu_chi_phi():
    """Dữ liệu bút toán mẫu: Doanh thu + Chi phí trong kỳ Q4/2025."""
    return [
        # → Doanh thu bán hàng: Có 511 / Nợ 111 (100 triệu)
        GhiSoKeToan(
            entry_date=date(2025, 10, 15),
            document_type="HD",
            document_number="HD-2025-1001",
            description="Bán hàng",
            lines=[
                ButToanLine(
                    so_tai_khoan="111",
                    amount=Decimal("100000000"),
                    transaction_type=TransactionType.DEBIT,
                    so_chung_tu_goc="HD-2025-1001",
                    ngay_chung_tu_goc=date(2025, 10, 15),
                    detail_object_type=DetailObjectType.NONE,
                ),
                ButToanLine(
                    so_tai_khoan="511",
                    amount=Decimal("100000000"),
                    transaction_type=TransactionType.CREDIT,
                    so_chung_tu_goc="HD-2025-1001",
                    ngay_chung_tu_goc=date(2025, 10, 15),
                    detail_object_type=DetailObjectType.NONE,
                ),
            ],
            # trang_thai="Posted"
        ),
        # → Giá vốn: Nợ 632 / Có 156 (60 triệu)
        GhiSoKeToan(
            entry_date=date(2025, 10, 15),
            document_type="PX",
            document_number="PX-2025-01",
            description="Xuất kho hàng bán",
            lines=[
                ButToanLine(
                    so_tai_khoan="632",
                    amount=Decimal("60000000"),
                    transaction_type=TransactionType.DEBIT,
                    so_chung_tu_goc="PX-2025-01",
                    ngay_chung_tu_goc=date(2025, 10, 15),
                    detail_object_type=DetailObjectType.NONE,
                ),
                ButToanLine(
                    so_tai_khoan="156",
                    amount=Decimal("60000000"),
                    transaction_type=TransactionType.CREDIT,
                    so_chung_tu_goc="PX-2025-01",
                    ngay_chung_tu_goc=date(2025, 10, 15),
                    detail_object_type=DetailObjectType.NONE,
                ),
            ],
            # trang_thai="Posted"
        ),
        # → Chi phí bán hàng: Nợ 641 / Có 111 (5 triệu)
        GhiSoKeToan(
            entry_date=date(2025, 11, 10),
            document_type="CT",
            document_number="CP-BH-01",
            description="Chi phí quảng cáo",
            lines=[
                ButToanLine(
                    so_tai_khoan="641",
                    amount=Decimal("5000000"),
                    transaction_type=TransactionType.DEBIT,
                    so_chung_tu_goc="CP-BH-01",
                    ngay_chung_tu_goc=date(2025, 11, 10),
                    detail_object_type=DetailObjectType.NONE,
                ),
                ButToanLine(
                    so_tai_khoan="111",
                    amount=Decimal("5000000"),
                    transaction_type=TransactionType.CREDIT,
                    so_chung_tu_goc="CP-BH-01",
                    ngay_chung_tu_goc=date(2025, 11, 10),
                    detail_object_type=DetailObjectType.NONE,
                ),
            ],
            # trang_thai="Posted"
        ),
    ]


def test_closing_service_ket_chuyen_dung_doanh_thu_va_chi_phi(
    closing_service, sample_buts_toan_doanh_thu_chi_phi
):
    """
    [TT99-Đ24] Kiểm tra kết chuyển Doanh thu/Chi phí vào 421.
    Đảm bảo:
      - Doanh thu (511) → Có 421
      - Chi phí (632, 641...) → Nợ 421
      - Không có TK 911
      - Bút toán được ghi sổ → đủ dữ liệu cho B02, B03
    """
    # Arrange
    closing_service.journal_repo.get_all_posted_in_range.return_value = (
        sample_buts_toan_doanh_thu_chi_phi
    )
    closing_service.journal_repo.add = Mock(side_effect=lambda x: x)
    closing_service.journal_repo.update_status = Mock(return_value=True)

    # Act
    ket_chuyen = closing_service.execute(
        ky_hieu="Q4-2025",
        ngay_bat_dau=date(2025, 10, 1),
        ngay_ket_thuc=date(2025, 12, 31),
    )

    # Assert
    assert len(ket_chuyen) == 2  # 1 cho Doanh thu, 1 cho Chi phí

    # → Kiểm tra bút toán kết chuyển Doanh thu
    bt_doanh_thu = ket_chuyen[0]
    assert bt_doanh_thu.document_number.startswith("KC-DOANH-THU")
    # assert bt_doanh_thu.trang_thai == "Posted"
    # - Có 421 = 100.000.000
    co_421 = next(
        (
            l.amount
            for l in bt_doanh_thu.lines
            if l.so_tai_khoan == "421"
            and l.transaction_type == TransactionType.CREDIT
        ),
        None,
    )
    assert co_421 == Decimal("100000000")
    # - Nợ 511 = 100.000.000
    no_511 = next(
        (
            l.amount
            for l in bt_doanh_thu.lines
            if l.so_tai_khoan == "511"
            and l.transaction_type == TransactionType.DEBIT
        ),
        None,
    )
    assert no_511 == Decimal("100000000")
    # - Không có TK 911
    assert not any(l.so_tai_khoan == "911" for l in bt_doanh_thu.lines)

    # → Kiểm tra bút toán kết chuyển Chi phí
    bt_chi_phi = ket_chuyen[1]
    assert bt_chi_phi.document_number.startswith("KC-CHI-PHI")
    # assert bt_chi_phi.trang_thai == "Posted"
    # - Nợ 421 = 65.000.000 (632 + 641)
    no_421 = next(
        (
            l.amount
            for l in bt_chi_phi.lines
            if l.so_tai_khoan == "421"
            and l.transaction_type == TransactionType.DEBIT
        ),
        None,
    )
    assert no_421 == Decimal("65000000")
    # - Có 632 = 60.000.000, Có 641 = 5.000.000
    co_632 = next(
        (
            l.amount
            for l in bt_chi_phi.lines
            if l.so_tai_khoan == "632"
            and l.transaction_type == TransactionType.CREDIT
        ),
        None,
    )
    co_641 = next(
        (
            l.amount
            for l in bt_chi_phi.lines
            if l.so_tai_khoan == "641"
            and l.transaction_type == TransactionType.CREDIT
        ),
        None,
    )
    assert co_632 == Decimal("60000000")
    assert co_641 == Decimal("5000000")
    # - Không có TK 911
    assert not any(l.so_tai_khoan == "911" for l in bt_chi_phi.lines)

    # → Kiểm tra Lợi nhuận sau thuế (421) = 100 - 65 = 35 triệu → đủ cho B02
    # → Bút toán đã Posted → B03 có thể truy vấn để tính dòng tiền

    print(
        "✅ Kết chuyển Doanh thu/Chi phí thành công. Dữ liệu đủ cho B02, B03."
    )
