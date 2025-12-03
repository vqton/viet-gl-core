# app/application/interfaces/accounting_period_service.py
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from app.domain.models.accounting_period import KyKeToan


class AccountingPeriodServiceInterface(ABC):
    """
    [TT99-Đ25] Interface cho service quản lý kỳ kế toán.
    Dùng để đảm bảo DIP trong JournalingService.
    """

    @abstractmethod
    def check_if_period_is_locked(self, ngay: date) -> bool:
        """
        Kiểm tra xem ngày chứng từ có thuộc kỳ đã khóa không.
        """
        pass

    @abstractmethod
    def lay_ky_ke_toan_theo_ngay(self, ngay: date) -> Optional[KyKeToan]:
        """
        Lấy kỳ kế toán theo ngày.
        """
        pass
