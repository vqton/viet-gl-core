# app/application/interfaces/period_repo.py
from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from app.domain.models.accounting_period import KyKeToan


class AccountingPeriodRepositoryInterface(ABC):
    @abstractmethod
    def add(self, ky: KyKeToan) -> KyKeToan:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[KyKeToan]:
        pass

    @abstractmethod
    def get_by_ten_ky(self, ten_ky: str) -> Optional[KyKeToan]:
        pass

    @abstractmethod
    def get_by_date(self, ngay: date) -> Optional[KyKeToan]:
        pass

    @abstractmethod
    def get_all(self) -> List[KyKeToan]:
        pass

    @abstractmethod
    def update_trang_thai(self, id: int, trang_thai: str) -> KyKeToan:
        pass
