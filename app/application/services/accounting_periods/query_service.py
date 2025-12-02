# app/application/services/accounting_periods/query_service.py
import logging
from datetime import date
from typing import List, Optional

from app.application.interfaces.period_repo import (
    AccountingPeriodRepositoryInterface,
)
from app.domain.models.accounting_period import KyKeToan

logger = logging.getLogger(__name__)


class QueryAccountingPeriodService:
    """
    [SRP] Chỉ chịu trách nhiệm truy vấn kỳ kế toán (READ).
    """

    def __init__(self, repo: AccountingPeriodRepositoryInterface):
        self.repo = repo

    def lay_ky_theo_id(self, id: int) -> Optional[KyKeToan]:
        return self.repo.get_by_id(id)

    def lay_ky_theo_ngay(self, ngay: date) -> Optional[KyKeToan]:
        return self.repo.get_by_date(ngay)

    def lay_tat_ca_ky(self) -> List[KyKeToan]:
        return self.repo.get_all()

    def kiem_tra_ky_da_khoa(self, id: int) -> bool:
        ky = self.repo.get_by_id(id)
        return ky.trang_thai == "Locked" if ky else False
