# gl_core/models/period.py
from datetime import date
from typing import Optional


class AccountingPeriod:
    def __init__(self, start_date: date, end_date: date, year: int, quarter: Optional[int] = None):
        self.start_date = start_date
        self.end_date = end_date
        self.year = year
        self.quarter = quarter  # 1, 2, 3, 4 hoặc None nếu là năm
        self.is_locked = False
        self.locked_by: Optional[str] = None  # Người khoá
        self.locked_at: Optional[date] = None  # Thời gian khoá

    def contains_date(self, check_date: date) -> bool:
        return self.start_date <= check_date <= self.end_date

    def lock(self, user: str):
        if self.is_locked:
            raise ValueError(f"Period {self.start_date} - {self.end_date} is already locked.")
        self.is_locked = True
        self.locked_by = user
        self.locked_at = date.today()

    def unlock(self, user: str):
        # Có thể có logic cho người có quyền cao hơn
        raise NotImplementedError("Unlocking a period requires special authorization.")