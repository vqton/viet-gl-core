# path: app/application/interfaces/account_repo.py
from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.models.account import TaiKhoan


class AccountRepositoryInterface(ABC):
    """
    Interface định nghĩa các thao tác CRUD và truy vấn cho Tài Khoản Kế Toán.
    
    Đây là một phần của lớp Ứng dụng (Application Layer), cung cấp giao diện
    để tương tác với dữ liệu Tài Khoản mà không quan tâm đến chi tiết
    triển khai cơ sở dữ liệu (ví dụ: SQL, NoSQL, In-Memory).
    """

    @abstractmethod
    def add(self, tai_khoan: TaiKhoan) -> TaiKhoan:
        """
        Thêm một tài khoản mới vào hệ thống.

        Args:
            tai_khoan: Domain model TaiKhoan cần thêm.

        Returns:
            TaiKhoan: Tài khoản đã được thêm thành công (thường bao gồm ID được DB gán).
        """
        pass

    @abstractmethod
    def get_by_id(self, so_tai_khoan: str) -> Optional[TaiKhoan]:
        """
        Truy vấn một tài khoản bằng Số Tài Khoản.

        Args:
            so_tai_khoan: Số tài khoản (primary key) cần tìm.

        Returns:
            Optional[TaiKhoan]: Domain model TaiKhoan nếu tìm thấy, ngược lại là None.
        """
        pass

    @abstractmethod
    def update(self, tai_khoan: TaiKhoan) -> TaiKhoan:
        """
        Cập nhật thông tin một tài khoản hiện có.

        Args:
            tai_khoan: Domain model TaiKhoan với thông tin đã cập nhật.

        Returns:
            TaiKhoan: Tài khoản sau khi đã được cập nhật.
            
        Raises:
            ValueError: Nếu tài khoản không tồn tại.
        """
        pass

    @abstractmethod
    def delete(self, so_tai_khoan: str) -> bool:
        """
        Xóa một tài khoản bằng Số Tài Khoản.

        Args:
            so_tai_khoan: Số tài khoản cần xóa.

        Returns:
            bool: True nếu xóa thành công, False nếu tài khoản không tồn tại.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[TaiKhoan]:
        """
        Lấy tất cả các tài khoản hiện có trong hệ thống.

        Returns:
            List[TaiKhoan]: Danh sách các Domain model TaiKhoan.
        """
        pass
    
    @abstractmethod
    def has_children(self, so_tai_khoan: str) -> bool:
        """
        Kiểm tra xem một tài khoản có tài khoản con (chi tiết) hay không.
        
        Đây là quy tắc nghiệp vụ CỐT LÕI (Leaf Account Rule) theo TT99:
        Nếu tài khoản CÓ con, nó là TK tổng hợp và KHÔNG được phép hạch toán.

        Args:
            so_tai_khoan: Số tài khoản cần kiểm tra.

        Returns:
            bool: True nếu tài khoản có tài khoản con, False nếu là tài khoản cấp cuối cùng (Leaf Account).
        """
        pass