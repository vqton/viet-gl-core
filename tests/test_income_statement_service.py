# tests/test_income_statement_service.py
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from app.application.services.income_statement_service import (
    IncomeStatementService,
)


@pytest.fixture
def mock_repo():
    repo = MagicMock()
    repo.get_all_accounts.return_value = [...]
    repo.get_account_balance.return_value = (
        Decimal(0),
        Decimal(100),
        Decimal(80),
        Decimal(0),
        Decimal(0),
    )
    return repo


@pytest.fixture
def income_statement_service(mock_repo):
    return IncomeStatementService(repo=mock_repo)


def test_lay_bao_cao_ket_qua_hdkd_success(income_statement_service):
    """
    [TT99-PL4] Test B02-DN tính đúng doanh thu, chi phí, lợi nhuận.
    """
    bao_cao = income_statement_service.lay_bao_cao(
        "Năm 2025", date(2025, 12, 31), date(2025, 1, 1), date(2025, 12, 31)
    )

    assert bao_cao.ky_hieu == "Năm 2025"
    assert bao_cao.doanh_thu_ban_hang == Decimal("80")
    assert bao_cao.loi_nhuan_sau_thue > Decimal("0")
