# tests/test_balance_sheet_service.py
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.application.services.balance_sheet_service import BalanceSheetService
from app.domain.models.account import LoaiTaiKhoan, TaiKhoan


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_all_accounts.return_value = [
        TaiKhoan(
            so_tai_khoan="111",
            ten_tai_khoan="Tiền mặt",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
            cap_tai_khoan=1,
        ),
        TaiKhoan(
            so_tai_khoan="331",
            ten_tai_khoan="Phải trả",
            loai_tai_khoan=LoaiTaiKhoan.NO_PHAI_TRA,
            cap_tai_khoan=1,
        ),
        TaiKhoan(
            so_tai_khoan="421",
            ten_tai_khoan="Lợi nhuận",
            loai_tai_khoan=LoaiTaiKhoan.VON_CHU_SO_HUU,
            cap_tai_khoan=1,
        ),
    ]
    repo.get_account_balance.return_value = (
        Decimal(0),
        Decimal(100),
        Decimal(50),
        Decimal(50),
        Decimal(0),
    )
    return repo


@pytest.fixture
def balance_sheet_service(mock_repo):
    return BalanceSheetService(repo=mock_repo)


def test_lay_bao_cao_tinh_hinh_tai_chinh_success(balance_sheet_service):
    """
    [TT99-PL4] Test B01-DN cân đối tài sản = nguồn vốn.
    """
    bao_cao = balance_sheet_service.lay_bao_cao(
        "Năm 2025", date(2025, 12, 31), date(2025, 12, 31)
    )

    assert bao_cao.ngay_lap == date(2025, 12, 31)
    assert bao_cao.ky_hieu == "Năm 2025"
    # Cân đối kế toán
    assert (
        bao_cao.tai_san.tong_cong_tai_san
        == bao_cao.nguon_von.tong_cong_nguon_von
    )
