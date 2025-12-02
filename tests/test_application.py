# tests/test_application.py
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.application.services.journaling_service import JournalingService
from app.application.services.reporting_service import ReportingService
from app.domain.models.account import LoaiTaiKhoan, TaiKhoan
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine


@pytest.fixture
def mock_journaling_service():
    mock_je_repo = MagicMock()
    mock_acc_repo = MagicMock()
    mock_period_service = MagicMock()
    return JournalingService(mock_je_repo, mock_acc_repo, mock_period_service)


def test_ket_chuyen_khong_dung_tk_911(mock_journaling_service):
    """Điều 24 TT99: Kết chuyển TRỰC TIẾP Doanh thu/Chi phí → 421, KHÔNG dùng TK 911."""
    # Mock: Doanh thu 100M, Chi phí 60M
    mock_journaling_service.repository.get_all_posted_in_range.return_value = [
        JournalEntry(
            lines=[
                JournalEntryLine(so_tai_khoan="511", co=Decimal("100000000")),
                JournalEntryLine(so_tai_khoan="632", no=Decimal("60000000")),
            ]
        )
    ]
    mock_journaling_service.account_repository.get_by_id.side_effect = (
        lambda x: TaiKhoan(
            so_tai_khoan=x,
            ten_tai_khoan="Test",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
            cap_tai_khoan=1,
        )
    )

    ket_chuyen = mock_journaling_service.ket_chuyen_cuoi_ky(
        "Năm 2025", date(2025, 12, 31)
    )

    # Kiểm tra: Không có dòng nào dùng TK 911
    for entry in ket_chuyen:
        for line in entry.lines:
            assert line.so_tai_khoan != "911"
