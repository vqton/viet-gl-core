# app/application/services/tai_khoan/create_service.py
import logging

from app.application.interfaces.account_repo import AccountRepositoryInterface
from app.application.interfaces.account_validator import TaiKhoanValidator
from app.domain.models.account import TaiKhoan

logger = logging.getLogger(__name__)


class CreateTaiKhoanService:
    """
    [SRP] Chỉ chịu trách nhiệm tạo mới tài khoản.
    """

    def __init__(
        self,
        repo: AccountRepositoryInterface,
        validator: TaiKhoanValidator = None,
    ):
        self.repo = repo
        self.validator = validator

    def execute(self, tai_khoan: TaiKhoan) -> TaiKhoan:
        # 1. Validate (nếu có)
        if self.validator:
            self.validator.validate(tai_khoan)

        # 2. Kiểm tra tài khoản cha (nếu là cấp con)
        if tai_khoan.cap_tai_khoan > 1:
            if not tai_khoan.so_tai_khoan_cha:
                raise ValueError("Tài khoản cấp con phải có tài khoản cha.")
            cha = self.repo.get_by_id(tai_khoan.so_tai_khoan_cha)
            if not cha:
                raise ValueError(
                    f"Tài khoản cha '{tai_khoan.so_tai_khoan_cha}' không tồn tại."
                )

        # 3. Kiểm tra trùng số tài khoản
        if self.repo.get_by_id(tai_khoan.so_tai_khoan):
            raise ValueError(
                f"Số tài khoản '{tai_khoan.so_tai_khoan}' đã tồn tại."
            )

        logger.info(
            f"[TAO_TAI_KHOAN] So: {tai_khoan.so_tai_khoan}, Ten: {tai_khoan.ten_tai_khoan}"
        )
        return self.repo.add(tai_khoan)
