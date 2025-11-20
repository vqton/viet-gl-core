# File: app/application/services/tai_khoan_service.py

from typing import List, Optional
from app.domain.models.account import TaiKhoan as TaiKhoanDomain
from app.infrastructure.repositories.account_repository import AccountRepository

class TaiKhoanService:
    def __init__(self, repository: AccountRepository):
        self.repository = repository

    def tao_tai_khoan(self, tai_khoan_domain: TaiKhoanDomain) -> TaiKhoanDomain:
        """
        Tạo mới một tài khoản.
        - Kiểm tra hợp lệ đã được thực hiện trong Domain Entity.
        - Kiểm tra tài khoản cha có tồn tại không (nếu là cấp con).
        - Gọi Repository để lưu vào DB.
        """
        # Nếu là tài khoản cấp con, kiểm tra tài khoản cha có tồn tại
        if tai_khoan_domain.cap_tai_khoan > 1 and tai_khoan_domain.so_tai_khoan_cha:
            cha = self.repository.get_by_id(tai_khoan_domain.so_tai_khoan_cha)
            if not cha:
                raise ValueError(f"Tài khoản cha '{tai_khoan_domain.so_tai_khoan_cha}' không tồn tại.")

        # Gọi Repository để thêm vào DB
        return self.repository.add(tai_khoan_domain)

    def lay_tai_khoan_theo_so(self, so_tai_khoan: str) -> Optional[TaiKhoanDomain]:
        """
        Lấy thông tin tài khoản theo số tài khoản.
        """
        return self.repository.get_by_id(so_tai_khoan)

    def lay_danh_sach_tai_khoan(self) -> List[TaiKhoanDomain]:
        """
        Lấy danh sách tất cả tài khoản.
        """
        return self.repository.get_all()

    # (Có thể thêm các phương thức khác như cap_nhat_tai_khoan, xoa_tai_khoan nếu cần)