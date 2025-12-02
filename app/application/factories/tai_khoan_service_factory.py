# app/application/factories/tai_khoan_service_factory.py
from app.application.interfaces.account_repo import AccountRepositoryInterface
from app.application.interfaces.account_validator import TaiKhoanValidator
from app.application.services.tai_khoan.create_service import (
    CreateTaiKhoanService,
)
from app.application.services.tai_khoan.delete_service import (
    DeleteTaiKhoanService,
)
from app.application.services.tai_khoan.query_service import (
    QueryTaiKhoanService,
)
from app.application.services.tai_khoan.update_service import (
    UpdateTaiKhoanService,
)


class TaiKhoanServiceFactory:
    """
    [DIP] Factory để tạo các service nhỏ theo yêu cầu.
    Tránh việc một class làm quá nhiều việc.
    """

    def __init__(
        self,
        repo: AccountRepositoryInterface,
        validator: TaiKhoanValidator = None,
    ):
        self.repo = repo
        self.validator = validator

    def create_create_service(self) -> CreateTaiKhoanService:
        return CreateTaiKhoanService(repo=self.repo, validator=self.validator)

    def create_update_service(self) -> UpdateTaiKhoanService:
        return UpdateTaiKhoanService(repo=self.repo)

    def create_delete_service(self) -> DeleteTaiKhoanService:
        return DeleteTaiKhoanService(repo=self.repo)

    def create_query_service(self) -> QueryTaiKhoanService:
        return QueryTaiKhoanService(repo=self.repo)
