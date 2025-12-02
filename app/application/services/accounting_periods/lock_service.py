# app/application/services/accounting_periods/lock_service.py
import logging
from datetime import date

from app.application.interfaces.period_repo import (
    AccountingPeriodRepositoryInterface,
)
from app.infrastructure.repositories.journal_entry_repository import (
    JournalEntryRepository,
)

logger = logging.getLogger(__name__)


class LockAccountingPeriodService:
    """
    [SRP] Chỉ chịu trách nhiệm khóa kỳ kế toán.
    [TT99-Đ25] Không cho phép khóa kỳ nếu còn bút toán nháp.
    """

    def __init__(
        self,
        period_repo: AccountingPeriodRepositoryInterface,
        je_repo: JournalEntryRepository,
    ):
        self.period_repo = period_repo
        self.je_repo = je_repo

    def execute(self, id: int, nguoi_thuc_hien: str = "System") -> bool:
        ky = self.period_repo.get_by_id(id)
        if not ky:
            raise ValueError(f"Kỳ kế toán với ID {id} không tồn tại.")

        if ky.trang_thai == "Locked":
            raise ValueError(f"Kỳ '{ky.ten_ky}' đã bị khóa rồi.")

        # 1. Kiểm tra bút toán nháp trong kỳ
        draft_entries = self.je_repo.get_draft_entries_by_date_range(
            ky.ngay_bat_dau, ky.ngay_ket_thuc
        )
        if draft_entries:
            so_phieu_list = [e.so_phieu for e in draft_entries]
            raise ValueError(
                f"Không thể khóa kỳ '{ky.ten_ky}'. Vẫn còn {len(draft_entries)} bút toán nháp: "
                f"{', '.join(so_phieu_list[:5])}{'...' if len(so_phieu_list) > 5 else ''}"
            )

        # 2. Cập nhật trạng thái
        self.period_repo.update_trang_thai(id, "Locked")
        logger.info(
            f"[KHOA_KY_THANH_CONG] Ky ID: {id}, Nguoi thuc hien: {nguoi_thuc_hien}"
        )
        return True
