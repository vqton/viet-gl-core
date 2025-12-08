# path: app/application/services/tai_khoan/update_service.py
from app.application.interfaces.account_repo import AccountRepositoryInterface
from app.application.interfaces.account_validator import TaiKhoanValidator
from app.domain.models.account import TaiKhoan


class UpdateTaiKhoanService:
    """
    [SRP] Chỉ chịu trách nhiệm cập nhật tài khoản kế toán.
    """

    def __init__(
        self,
        repo: AccountRepositoryInterface,
        validator: TaiKhoanValidator = None,
    ):
        self.repo = repo
        self.validator = validator  # Thêm validator

    def execute(self, tai_khoan_moi: TaiKhoan) -> TaiKhoan:
        """
        Thực thi việc cập nhật Tài khoản.

        Args:
            tai_khoan_moi: Domain model TaiKhoan với thông tin đã cập nhật.

        Returns:
            TaiKhoan: Tài khoản sau khi đã được cập nhật.

        Raises:
            ValueError: Nếu Tài khoản không hợp lệ hoặc Tài khoản cha không tồn tại.
        """

        # 1. Xác thực (Quy tắc Cốt lõi)
        if self.validator:
            self.validator.validate(tai_khoan_moi)

        # 2. Kiểm tra nghiệp vụ phối hợp: Tài khoản cha phải tồn tại (nếu có)
        if tai_khoan_moi.cap_tai_khoan > 1 and tai_khoan_moi.so_tai_khoan_cha:
            cha = self.repo.get_by_id(tai_khoan_moi.so_tai_khoan_cha)
            if not cha:
                raise ValueError(
                    f"Tài khoản cha '{tai_khoan_moi.so_tai_khoan_cha}' không tồn tại."
                )

        # 3. Kiểm tra Tài khoản có tồn tại để cập nhật không
        if not self.repo.get_by_id(tai_khoan_moi.so_tai_khoan):
            raise ValueError(
                f"Tài khoản cần cập nhật '{tai_khoan_moi.so_tai_khoan}' không tồn tại."
            )

        # 4. Gọi repo để cập nhật
        return self.repo.update(tai_khoan_moi)
