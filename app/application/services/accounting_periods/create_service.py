# app/application/services/accounting_periods/create_service.py
import logging

from app.application.interfaces.period_repo import (
    AccountingPeriodRepositoryInterface,
)
from app.domain.models.accounting_period import KyKeToan

logger = logging.getLogger(__name__)


class CreateAccountingPeriodService:
    """
    [SRP] Chỉ chịu trách nhiệm tạo mới kỳ kế toán.
    """

    def __init__(self, repo: AccountingPeriodRepositoryInterface):
        self.repo = repo

    def execute(self, ky: KyKeToan) -> KyKeToan:
        # 1. Kiểm tra trùng tên kỳ
        if self.repo.get_by_ten_ky(ky.ten_ky):
            raise ValueError(f"Kỳ kế toán '{ky.ten_ky}' đã tồn tại.")

        logger.info(
            f"[TAO_KY_KE_TOAN] Ky: {ky.ten_ky}, Ngay: {ky.ngay_bat_dau} → {ky.ngay_ket_thuc}"
        )
        return self.repo.add(ky)
