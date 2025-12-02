# app/application/interfaces/account_repo.py
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models.account import TaiKhoan


class AccountRepositoryInterface(ABC):
    """
    [DIP] Interface cho repository tài khoản.
    Service không phụ thuộc vào implementation cụ thể.
    """

    @abstractmethod
    def add(self, tai_khoan: TaiKhoan) -> TaiKhoan:
        pass

    @abstractmethod
    def get_by_id(self, so_tai_khoan: str) -> Optional[TaiKhoan]:
        pass

    @abstractmethod
    def get_all(self) -> List[TaiKhoan]:
        pass

    @abstractmethod
    def update(self, tai_khoan: TaiKhoan) -> TaiKhoan:
        pass

    @abstractmethod
    def delete(self, so_tai_khoan: str) -> bool:
        pass

    @abstractmethod
    def has_transactions(self, so_tai_khoan: str) -> bool:
        """
        Kiểm tra tài khoản có phát sinh hay không (dùng cho xóa).
        """
        pass
