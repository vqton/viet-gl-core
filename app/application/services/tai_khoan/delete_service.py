# app/application/services/tai_khoan/delete_service.py
import logging

from app.application.interfaces.account_repo import AccountRepositoryInterface

logger = logging.getLogger(__name__)


class DeleteTaiKhoanService:
    """
    [SRP] Chỉ chịu trách nhiệm xóa tài khoản.
    """

    def __init__(self, repo: AccountRepositoryInterface):
        self.repo = repo

    def execute(self, so_tai_khoan: str) -> bool:
        # 1. Kiểm tra tồn tại
        tai_khoan = self.repo.get_by_id(so_tai_khoan)
        if not tai_khoan:
            raise ValueError(f"Tài khoản '{so_tai_khoan}' không tồn tại.")

        # 2. Kiểm tra phát sinh
        if self.repo.has_transactions(so_tai_khoan):
            raise ValueError(
                f"Tài khoản '{so_tai_khoan}' đã có phát sinh. Không thể xóa."
            )

        logger.info(f"[XOA_TAI_KHOAN] So: {so_tai_khoan}")
        return self.repo.delete(so_tai_khoan)
