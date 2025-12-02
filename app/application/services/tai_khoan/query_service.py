# app/application/services/tai_khoan/query_service.py
"""
[SRP] Service chỉ chịu trách nhiệm truy vấn tài khoản (read-only).
Không thay đổi dữ liệu.
"""
from typing import List, Optional

from app.application.interfaces.account_repo import AccountRepositoryInterface
from app.domain.models.account import TaiKhoan


class QueryTaiKhoanService:
    def __init__(self, repo: AccountRepositoryInterface):
        self.repo = repo

    def lay_tai_khoan_theo_so(self, so_tai_khoan: str) -> Optional[TaiKhoan]:
        return self.repo.get_by_id(so_tai_khoan)

    def lay_tat_ca_tai_khoan(self) -> List[TaiKhoan]:
        return self.repo.get_all()
