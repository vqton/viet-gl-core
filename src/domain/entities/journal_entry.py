from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal
from enum import Enum


class JournalEntryStatus(Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    CLOSED = "closed"
    ADJUSTED = "adjusted"


@dataclass(frozen=True)
class JournalEntry:
    """
    Bút toán kế toán với đầy đủ audit trail và versioning theo TT 99.
    """

    # 🔸 PHẦN 1: Các trường BẮT BUỘC (không có giá trị mặc định)
    account: str
    debit: Decimal
    credit: Decimal
    description: str
    source_document_id: str
    accounting_date: date
    accounting_period_code: str
    created_by: str  # ← Di chuyển lên trên
    created_at: datetime
    approved_by: str
    approved_at: datetime

    # 🔸 PHẦN 2: Các trường TÙY CHỌN (có giá trị mặc định)
    status: JournalEntryStatus = JournalEntryStatus.DRAFT
    original_entry_id: str = ""
    is_reversal: bool = False
    adjustment_reason: str = ""

    def __post_init__(self):
        if self.debit < 0 or self.credit < 0:
            raise ValueError("Số tiền không được âm")
        if self.debit > 0 and self.credit > 0:
            raise ValueError("Không thể vừa Nợ vừa Có")
