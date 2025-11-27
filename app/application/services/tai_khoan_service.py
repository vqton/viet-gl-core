from typing import List, Optional
from app.domain.models.account import TaiKhoan as TaiKhoanDomain
from app.infrastructure.repositories.account_repository import AccountRepository

class TaiKhoanService:
    """
    [Nghiệp vụ] Service quản lý Sơ đồ tài khoản (Chart of Accounts).
    Chịu trách nhiệm cho việc tạo, truy vấn, và duy trì tính toàn vẹn cấp bậc của tài khoản.
    """
    def __init__(self, repository: AccountRepository):
        self.repository = repository

    def tao_tai_khoan(self, tai_khoan_domain: TaiKhoanDomain) -> TaiKhoanDomain:
        """
        [Nghiệp vụ] Tạo mới một tài khoản.
        - Kiểm tra hợp lệ Domain (trong Entity).
        - [Ràng buộc cấp bậc] Kiểm tra tài khoản cha có tồn tại không (nếu là tài khoản cấp con).
        - Gọi Repository để lưu vào DB.
        """
        # Nếu là tài khoản cấp con, kiểm tra tài khoản cha có tồn tại
        if tai_khoan_domain.cap_tai_khoan > 1 and tai_khoan_domain.so_tai_khoan_cha:
            cha = self.repository.get_by_id(tai_khoan_domain.so_tai_khoan_cha)
            if not cha:
                raise ValueError(f"Tài khoản cha '{tai_khoan_domain.so_tai_khoan_cha}' không tồn tại.")
        # [Ràng buộc Tồn tại] Kiểm tra tài khoản không được trùng số
        if self.repository.get_by_id(tai_khoan_domain.so_tai_khoan):
             raise ValueError(f"Số tài khoản '{tai_khoan_domain.so_tai_khoan}' đã tồn tại.")

        # Gọi Repository để thêm vào DB
        return self.repository.add(tai_khoan_domain)

    def lay_tai_khoan_theo_so(self, so_tai_khoan: str) -> Optional[TaiKhoanDomain]:
        """
        Lấy thông tin tài khoản theo số tài khoản.
        """
        return self.repository.get_by_id(so_tai_khoan)

    def lay_tat_ca_tai_khoan(self) -> List[TaiKhoanDomain]:
        """
        Lấy danh sách tất cả tài khoản trong sơ đồ.
        """
        return self.repository.get_all()