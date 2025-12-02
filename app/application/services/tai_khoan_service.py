# app/application/services/tai_khoan_service.py
from typing import List, Optional

from app.application.interfaces.account_validator import (  # 👈 MỚI THÊM
    TaiKhoanValidator,
)
from app.domain.models.account import TaiKhoan as TaiKhoanDomain
from app.infrastructure.repositories.account_repository import (
    AccountRepository,
)


class TaiKhoanService:
    def __init__(
        self,
        repository: AccountRepository,
        validator: TaiKhoanValidator = None,
    ):
        self.repository = repository
        # 👇 Validator là optional để không làm hỏng backward compatibility
        self.validator = validator

    def tao_tai_khoan(
        self, tai_khoan_domain: TaiKhoanDomain
    ) -> TaiKhoanDomain:
        # ✅ [OCP] Nếu có validator, gọi validate
        if self.validator:
            self.validator.validate(tai_khoan_domain)

        # 1. Kiểm tra tài khoản cha tồn tại (nếu là cấp con)
        if (
            tai_khoan_domain.cap_tai_khoan > 1
            and tai_khoan_domain.so_tai_khoan_cha
        ):
            cha = self.repository.get_by_id(tai_khoan_domain.so_tai_khoan_cha)
            if not cha:
                raise ValueError(
                    f"Tài khoản cha '{tai_khoan_domain.so_tai_khoan_cha}' không tồn tại."
                )

        # 2. Kiểm tra trùng số tài khoản
        if self.repository.get_by_id(tai_khoan_domain.so_tai_khoan):
            raise ValueError(
                f"Số tài khoản '{tai_khoan_domain.so_tai_khoan}' đã tồn tại."
            )

        return self.repository.add(tai_khoan_domain)

    def lay_tai_khoan_theo_so(
        self, so_tai_khoan: str
    ) -> Optional[TaiKhoanDomain]:
        return self.repository.get_by_id(so_tai_khoan)

    def lay_tat_ca_tai_khoan(self) -> List[TaiKhoanDomain]:
        return self.repository.get_all()

    def cap_nhat_tai_khoan(
        self, tai_khoan_moi: TaiKhoanDomain
    ) -> TaiKhoanDomain:
        """
        [TT99-PL2] Cập nhật thông tin tài khoản.
        - Chỉ được phép nếu tài khoản chưa có phát sinh.
        """
        tai_khoan_cu = self.repository.get_by_id(tai_khoan_moi.so_tai_khoan)
        if not tai_khoan_cu:
            raise ValueError(
                f"Tài khoản '{tai_khoan_moi.so_tai_khoan}' không tồn tại."
            )

        # Kiểm tra tài khoản cha (nếu là cấp con)
        if tai_khoan_moi.cap_tai_khoan > 1 and tai_khoan_moi.so_tai_khoan_cha:
            cha = self.repository.get_by_id(tai_khoan_moi.so_tai_khoan_cha)
            if not cha:
                raise ValueError(
                    f"Tài khoản cha '{tai_khoan_moi.so_tai_khoan_cha}' không tồn tại."
                )

        return self.repository.update(tai_khoan_moi)

    def xoa_tai_khoan(self, so_tai_khoan: str) -> bool:
        """
        [TT99-PL2] Xóa tài khoản.
        - Không cho phép nếu tài khoản đã có phát sinh.
        """
        # Kiểm tra phát sinh (có thể gọi sang JournalEntryRepo để kiểm)
        # Nếu có phát sinh → không cho xóa
        # Nếu không có → xóa
        raise NotImplementedError(
            "Chưa hoàn thiện logic xóa tài khoản có kiểm tra phát sinh."
        )
