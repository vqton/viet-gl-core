"""
Module: AccountingPeriod

Đại diện cho kỳ kế toán theo Điều 13 Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Doanh nghiệp phải tổ chức kế toán theo kỳ kế toán.
- Kỳ kế toán năm không quá 12 tháng.
"""

from dataclasses import dataclass
from datetime import date

@dataclass(frozen=True)
class AccountingPeriod:
    """
    Kỳ kế toán (tháng, quý, năm).

    Attributes:
        code (str): Mã kỳ (ví dụ: "2026-Q2").
        start_date (date): Ngày bắt đầu kỳ.
        end_date (date): Ngày kết thúc kỳ.
        is_closed (bool): Trạng thái đã khóa sổ hay chưa.
    """
    code: str
    start_date: date
    end_date: date
    is_closed: bool = False