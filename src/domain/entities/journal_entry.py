"""
Module: JournalEntry

Đại diện cho một bút toán kế toán hợp lệ theo Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Mỗi bút toán phải có chứng từ gốc (Điều 12 TT 99)
- Phải ghi nhận theo ngày phát sinh (Điều 13 TT 99)
- Phải lưu vết người lập, thời gian (Điều 27 TT 99)
"""

from dataclasses import dataclass
from datetime import datetime, date
from decimal import Decimal

@dataclass(frozen=True)
class JournalEntry:
    """
    Bút toán kế toán bất biến, có audit trail đầy đủ.

    Attributes:
        account (str): Mã tài khoản theo Phụ lục II TT 99.
        debit (Decimal): Số tiền Nợ (>= 0).
        credit (Decimal): Số tiền Có (>= 0).
        description (str): Diễn giải nghiệp vụ.
        source_document_id (str): ID chứng từ gốc (hóa đơn, phiếu kho...).
        accounting_date (date): Ngày ghi sổ kế toán.
        created_by (str): ID người lập (bắt buộc theo Điều 27 TT 99).
        created_at (datetime): Thời điểm tạo bút toán.
        adjustment_reason (str): Lý do điều chỉnh (nếu có).

    Raises:
        ValueError: Nếu số tiền âm hoặc vừa Nợ vừa Có.
    """
    account: str
    debit: Decimal
    credit: Decimal
    description: str
    source_document_id: str
    accounting_date: date
    created_by: str
    created_at: datetime
    adjustment_reason: str = ""

    def __post_init__(self):
        if self.debit < 0 or self.credit < 0:
            raise ValueError("Số tiền không được âm")
        if self.debit > 0 and self.credit > 0:
            raise ValueError("Không thể vừa Nợ vừa Có")