# app/application/services/tai_khoan/update_service.py
from app.application.interfaces.account_repo import AccountRepositoryInterface
from app.domain.models.account import TaiKhoan


class UpdateTaiKhoanService:
    """
    [SRP] Chỉ chịu trách nhiệm cập nhật tài khoản kế toán.
    """

    def __init__(self, repo: AccountRepositoryInterface):
        self.repo = repo

    def execute(self, tai_khoan_moi: TaiKhoan) -> TaiKhoan:
        # 1. Kiểm tra tài khoản cha (nếu là cấp con)
        if tai_khoan_moi.cap_tai_khoan > 1 and tai_khoan_moi.so_tai_khoan_cha:
            cha = self.repo.get_by_id(tai_khoan_moi.so_tai_khoan_cha)
            if not cha:
                raise ValueError(
                    f"Tài khoản cha '{tai_khoan_moi.so_tai_khoan_cha}' không tồn tại."
                )

        # 2. Gọi repo để cập nhật
        return self.repo.update(tai_khoan_moi)
