# app/application/interfaces/report_repo.py
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import List, Tuple

from app.domain.models.account import TaiKhoan
from app.domain.models.journal_entry import JournalEntry


class ReportRepositoryInterface(ABC):
    """
    [DIP] Interface cho các repository dùng trong báo cáo.
    Tách biệt với AccountRepository để SRP rõ ràng.
    """

    @abstractmethod
    def get_all_posted_in_range(
        self, start: date, end: date
    ) -> List[JournalEntry]:
        """
        Lấy tất cả các bút toán đã ghi sổ trong khoảng thời gian.
        """
        pass

    @abstractmethod
    def get_all_accounts(self) -> List[TaiKhoan]:
        """
        Trả về toàn bộ danh sách tài khoản kế toán.
        """
        pass

    @abstractmethod
    def get_opening_balance(self, so_tai_khoan: str, ngay: date) -> Decimal:
        """
        Lấy số dư đầu kỳ của TK tại ngày chỉ định.
        """
        pass

    @abstractmethod
    def get_account_balance(
        self, so_tai_khoan: str, start: date, end: date
    ) -> Tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
        """
        Trả về: (SDĐK Nợ, PS Nợ, PS Có, SDCK Nợ, SDCK Có)
        """
        pass
