# app/application/services/journaling/posting_service.py
"""
[SRP] Service chịu trách nhiệm ghi sổ (post) bút toán kế toán.

📋 TT99/2025/TT-BTC:
- Điều 24: Ghi sổ kép (cân bằng Nợ = Có).
- Điều 25: Không ghi sổ vào kỳ đã khóa.
- Phụ lục I: Bút toán phải có chứng từ gốc.

🎯 Mục tiêu:
- Chỉ xử lý logic "đổi trạng thái Draft → Posted".
- Kiểm tra khóa sổ trước khi ghi.
- Không thay đổi số phát sinh tài khoản (chỉ thay đổi trạng thái).
"""
import logging
from datetime import date
from typing import Optional

from app.application.interfaces.accounting_period_service import (
    AccountingPeriodServiceInterface,
)
from app.application.interfaces.journal_entry_repo import (
    JournalEntryRepositoryInterface,
)
from app.domain.models.journal_entry import JournalEntry

logger = logging.getLogger(__name__)


class PostingJournalEntryService:
    """
    [SRP] Chỉ chịu trách nhiệm ghi sổ (Post) bút toán kế toán.
    """

    def __init__(
        self,
        repo: JournalEntryRepositoryInterface,
        period_service: AccountingPeriodServiceInterface,
    ):
        self.repo = repo
        self.period_service = period_service

    def execute(self, id: int) -> JournalEntry:
        """
        Ghi sổ bút toán: chuyển trạng thái từ 'Draft' → 'Posted'.

        Args:
            id: ID của bút toán cần ghi sổ.

        Returns:
            Bút toán sau khi đã được ghi sổ.

        Raises:
            ValueError: Nếu bút toán không tồn tại, đã ghi sổ, hoặc kỳ bị khóa.
        """
        entry = self.repo.get_by_id(id)
        if not entry:
            raise ValueError(f"Bút toán với ID {id} không tồn tại.")

        if entry.trang_thai == "Posted":
            raise ValueError(f"Bút toán ID {id} đã được ghi sổ rồi.")

        if entry.trang_thai == "Locked":
            raise ValueError(
                f"Bút toán ID {id} đã bị khóa, không thể thay đổi trạng thái."
            )

        # Kiểm tra khóa sổ
        self.period_service.check_if_period_is_locked(entry.ngay_ct)

        # Kiểm tra chứng từ gốc (nếu có yêu cầu strict)
        for line in entry.lines:
            if not line.so_chung_tu_goc or not line.ngay_chung_tu_goc:
                logger.warning(
                    f"[CHUNG_TU_THIEU] Bút toán {entry.so_phieu} có dòng không có chứng từ gốc."
                )

        # Cập nhật trạng thái
        entry.trang_thai = "Posted"
        updated_entry = self.repo.update_status(id, "Posted")

        logger.info(
            f"[GHI_SO_THANH_CONG] Bút toán {id} ({entry.so_phieu}) đã được ghi sổ."
        )
        return updated_entry

    def unpost(self, id: int) -> JournalEntry:
        entry = self.repo.get_by_id(id)
        if not entry:
            raise ValueError(f"Bút toán với ID {id} không tồn tại.")
        if entry.trang_thai == "Draft":
            raise ValueError("Bút toán đã ở trạng thái Draft.")
        if entry.trang_thai == "Locked":
            raise ValueError("Bút toán đã bị khóa.")

        # Kiểm tra khóa sổ
        self.period_service.check_if_period_is_locked(entry.ngay_ct)

        entry.trang_thai = "Draft"
        return self.repo.update_status(id, "Draft")
