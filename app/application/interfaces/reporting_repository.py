# app/application/interfaces/reporting_repository.py
from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import List, Tuple

from app.domain.models.account import TaiKhoan
from app.domain.models.journal_entry import JournalEntry


class ReportingRepository(ABC):
    """
    Interface định nghĩa các phương thức truy vấn dữ liệu phục vụ báo cáo tài chính.
    Tuân thủ TT99/2025/TT-BTC.
    """

    @abstractmethod
    def get_all_posted_entries_in_range(
        self, start: date, end: date
    ) -> List[JournalEntry]:
        """
        Lấy tất cả bút toán đã ghi sổ trong khoảng thời gian.
        """
        pass

    @abstractmethod
    def get_all_accounts(self) -> List[TaiKhoan]:
        """
        Lấy tất cả tài khoản trong hệ thống (theo Phụ lục II TT99).
        """
        pass

    @abstractmethod
    def get_opening_balance(self, so_tai_khoan: str, ngay: date) -> Decimal:
        """
        Lấy số dư đầu kỳ của một tài khoản tại một ngày.
        """
        pass

    @abstractmethod
    def get_account_balance(
        self, so_tai_khoan: str, ngay_bat_dau: date, ngay_ket_thuc: date
    ) -> Tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
        """
        Trả về: (SDĐK, PS Nợ, PS Có, SDCK Nợ, SDCK Có)
        """
        pass
