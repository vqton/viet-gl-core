# tests/test_services.py
from datetime import date
from decimal import Decimal
from unittest.mock import Mock

import pytest

from app.application.services.journaling_service import JournalingService
from app.domain.models.account import LoaiTaiKhoan, TaiKhoan
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine


def test_ket_chuyen_cuoi_ky_khong_dung_tk_911():
    """
    [TT99-Đ24] Kết chuyển không sử dụng tài khoản 911.
    Kết chuyển trực tiếp từ Doanh thu/Chi phí → 421.
    """
    mock_je_repo = Mock()
    mock_acc_repo = Mock()
    mock_period_service = Mock()

    service = JournalingService(
        mock_je_repo, mock_acc_repo, mock_period_service
    )

    # Mock dữ liệu bút toán: Doanh thu 100, Chi phí 60
    mock_je_repo.get_all_posted_in_range.return_value = [
        JournalEntry(
            so_phieu="BH-2025",  # 👈 THÊM DÒNG NÀY
            ngay_ct=date(2025, 12, 31),  # 👈 THÊM DÒNG NÀY
            lines=[
                JournalEntryLine(
                    so_tai_khoan="511", no=Decimal("0"), co=Decimal("100")
                ),
                JournalEntryLine(
                    so_tai_khoan="632", no=Decimal("60"), co=Decimal("0")
                ),
            ],
        )
    ]

    # Mock tài khoản tồn tại
    mock_acc_repo.get_by_id.side_effect = lambda x: {
        "511": TaiKhoan("511", "Doanh thu", LoaiTaiKhoan.DOANH_THU, 1),
        "632": TaiKhoan("632", "Giá vốn", LoaiTaiKhoan.CHI_PHI, 1),
        "421": TaiKhoan("421", "Lợi nhuận", LoaiTaiKhoan.VON_CHU_SO_HUU, 1),
    }.get(x)

    # Mock add bút toán kết chuyển
    def mock_add(entry):
        entry.id = 1001
        entry.trang_thai = "Draft"
        return entry

    mock_je_repo.add.side_effect = mock_add

    # Gọi kết chuyển
    ket_chuyen = service.ket_chuyen_cuoi_ky("Năm 2025", date(2025, 12, 31))

    # Kiểm tra: Không có TK 911
    for bt in ket_chuyen:
        for line in bt.lines:
            assert line.so_tai_khoan != "911"

    # Kiểm tra: Kết chuyển vào 421
    assert ket_chuyen[0].lines[0].so_tai_khoan == "511"  # Nợ 511
    assert ket_chuyen[0].lines[1].so_tai_khoan == "421"  # Có 421
