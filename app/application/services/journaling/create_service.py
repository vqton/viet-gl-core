# app/application/services/journaling/create_service.py
import logging

from app.application.interfaces.account_repo import AccountRepositoryInterface
from app.application.interfaces.journal_entry_repo import (
    JournalEntryRepositoryInterface,
)
from app.application.interfaces.period_repo import (
    AccountingPeriodRepositoryInterface,
)
from app.domain.models.journal_entry import JournalEntry

logger = logging.getLogger(__name__)


class CreateJournalEntryService:
    """
    [SRP] Chỉ chịu trách nhiệm tạo mới bút toán kế toán.
    """

    def __init__(
        self,
        journal_repo: JournalEntryRepositoryInterface,
        account_repo: AccountRepositoryInterface,
        period_service: AccountingPeriodRepositoryInterface,
    ):
        self.journal_repo = journal_repo
        self.account_repo = account_repo
        self.period_service = period_service

    def execute(self, entry: JournalEntry) -> JournalEntry:
        # 1. Kiểm tra khóa sổ
        self.period_service.check_if_period_is_locked(entry.ngay_ct)

        # 2. Kiểm tra tài khoản tồn tại
        for line in entry.lines:
            tai_khoan = self.account_repo.get_by_id(line.so_tai_khoan)
            if not tai_khoan:
                raise ValueError(
                    f"Tài khoản '{line.so_tai_khoan}' không tồn tại."
                )

        logger.info(
            f"[TAO_BUT_TOAN] So phieu: {entry.so_phieu}, Ngay: {entry.ngay_ct}"
        )

        entry.trang_thai = "Draft"
        return self.journal_repo.add(entry)
