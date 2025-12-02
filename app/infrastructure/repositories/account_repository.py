from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.models.account import TaiKhoan as TaiKhoanDomain
from app.infrastructure.models.sql_account import SQLAccount


class AccountRepository:
    """
    [Nghiệp vụ] Repository chịu trách nhiệm quản lý việc lưu trữ và truy xuất các đối tượng TaiKhoan
    (Sơ đồ tài khoản) từ cơ sở dữ liệu.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session

    def add(self, tai_khoan_domain: TaiKhoanDomain) -> TaiKhoanDomain:
        """
        [Nghiệp vụ] Thêm một tài khoản mới vào DB.
        - Chuyển đổi Domain Entity thành ORM Model.
        - Lưu vào DB.
        """
        # Chuyển đổi từ Domain Entity sang ORM Model
        sql_account = SQLAccount(
            so_tai_khoan=tai_khoan_domain.so_tai_khoan,
            ten_tai_khoan=tai_khoan_domain.ten_tai_khoan,
            loai_tai_khoan=tai_khoan_domain.loai_tai_khoan,
            cap_tai_khoan=tai_khoan_domain.cap_tai_khoan,
            so_tai_khoan_cha=tai_khoan_domain.so_tai_khoan_cha,
            la_tai_khoan_tong_hop=tai_khoan_domain.la_tai_khoan_tong_hop,
        )
        self.db_session.add(sql_account)
        self.db_session.commit()
        self.db_session.refresh(
            sql_account
        )  # Cập nhật lại đối tượng từ DB (chủ yếu cho các trường auto-generated nếu có)
        # Trả về Domain Entity (tương tự như input, vì không có ID tự tăng)
        return tai_khoan_domain

    def get_by_id(self, so_tai_khoan: str) -> Optional[TaiKhoanDomain]:
        """
        [Nghiệp vụ] Lấy thông tin tài khoản theo số tài khoản (Key chính).
        """
        sql_account = (
            self.db_session.query(SQLAccount)
            .filter(SQLAccount.so_tai_khoan == so_tai_khoan)
            .first()
        )
        if not sql_account:
            return None
        # Chuyển đổi từ ORM Model sang Domain Entity
        return TaiKhoanDomain(
            so_tai_khoan=sql_account.so_tai_khoan,
            ten_tai_khoan=sql_account.ten_tai_khoan,
            loai_tai_khoan=sql_account.loai_tai_khoan,
            cap_tai_khoan=sql_account.cap_tai_khoan,
            so_tai_khoan_cha=sql_account.so_tai_khoan_cha,
            la_tai_khoan_tong_hop=sql_account.la_tai_khoan_tong_hop,
        )

    def get_all(self) -> List[TaiKhoanDomain]:
        """
        [Nghiệp vụ] Lấy danh sách tất cả tài khoản trong sơ đồ.
        """
        sql_accounts = self.db_session.query(SQLAccount).all()
        # Ánh xạ danh sách ORM Model thành danh sách Domain Entity
        return [
            TaiKhoanDomain(
                so_tai_khoan=acc.so_tai_khoan,
                ten_tai_khoan=acc.ten_tai_khoan,
                loai_tai_khoan=acc.loai_tai_khoan,
                cap_tai_khoan=acc.cap_tai_khoan,
                so_tai_khoan_cha=acc.so_tai_khoan_cha,
                la_tai_khoan_tong_hop=acc.la_tai_khoan_tong_hop,
            )
            for acc in sql_accounts
        ]
