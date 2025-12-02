# app/application/interfaces/account_validator.py
from abc import ABC, abstractmethod

from app.domain.models.account import TaiKhoan as TaiKhoanDomain


class TaiKhoanValidator(ABC):
    @abstractmethod
    def validate(self, tai_khoan: TaiKhoanDomain) -> None:
        """
        Kiểm tra tài khoản có hợp lệ không.
        Nếu không hợp lệ, ném ValueError.
        """
        pass
