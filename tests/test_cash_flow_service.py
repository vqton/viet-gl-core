# tests/test_cash_flow_service.py
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.application.services.cash_flow_service import CashFlowService


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    return repo


@pytest.fixture
def cash_flow_service(mock_repo):
    return CashFlowService(repo=mock_repo)


def test_lay_bao_cao_luu_chuyen_tien_te_success(cash_flow_service):
    """
    [TT99-PL4] Test B03-DN theo phương pháp gián tiếp.
    """
    bao_cao = cash_flow_service.lay_bao_cao(
        "Năm 2025", date(2025, 12, 31), date(2025, 1, 1), date(2025, 12, 31)
    )

    assert bao_cao.ky_hieu == "Năm 2025"
    assert bao_cao.luu_chuyen_tien_thuan_trong_ky == Decimal(
        "50000000"
    )  # mock
