# File: app/infrastructure/models/sql_account.py
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship # Import relationship nếu cần sau này
from sqlalchemy.types import Enum as SQLEnum # Import SQLEnum để ánh xạ enum Python
from app.domain.models.account import LoaiTaiKhoan # Import enum từ Domain

Base = declarative_base()

class SQLAccount(Base):
    """
    ORM Model đại diện cho bảng 'accounts' trong cơ sở dữ liệu,
    ánh xạ tới Entity Domain 'TaiKhoan'.
    """
    __tablename__ = 'accounts'

    # Cột chính (Primary Key)
    so_tai_khoan = Column(String(20), primary_key=True, index=True) # Khóa chính, đánh index để tìm nhanh

    # Các cột khác
    ten_tai_khoan = Column(String(256), nullable=False) # Tên tài khoản, không cho phép null
    loai_tai_khoan = Column(SQLEnum(LoaiTaiKhoan), nullable=False) # Loại tài khoản, dùng SQLEnum
    cap_tai_khoan = Column(Integer, nullable=False, default=1) # Cấp tài khoản (1, 2, 3), default là 1
    # Cột tham chiếu đến tài khoản cha (self-referencing foreign key)
    so_tai_khoan_cha = Column(String(20), ForeignKey('accounts.so_tai_khoan'), nullable=True) # Cho phép null nếu là cấp 1
    la_tai_khoan_tong_hop = Column(Boolean, nullable=False, default=True) # Mặc định là True

    # Relationship (nếu cần) có thể được định nghĩa ở đây
    # Ví dụ: quan hệ cha-con, hoặc các dòng chi tiết liên quan đến tài khoản này
    # children = relationship("SQLAccount", back_populates="parent") # Self-referencing relationship
    # parent = relationship("SQLAccount", remote_side=[so_tai_khoan], back_populates="children")

    # (Tùy chọn) Phương thức để chuyển từ Domain Entity sang ORM Model
    # @classmethod
    # def from_domain(cls, tai_khoan_domain: TaiKhoan):
    #     return cls(
    #         so_tai_khoan=tai_khoan_domain.so_tai_khoan,
    #         ten_tai_khoan=tai_khoan_domain.ten_tai_khoan,
    #         loai_tai_khoan=tai_khoan_domain.loai_tai_khoan,
    #         cap_tai_khoan=tai_khoan_domain.cap_tai_khoan,
    #         so_tai_khoan_cha=tai_khoan_domain.so_tai_khoan_cha,
    #         la_tai_khoan_tong_hop=tai_khoan_domain.la_tai_khoan_tong_hop
    #     )

    # (Tùy chọn) Phương thức để chuyển từ ORM Model sang Domain Entity
    # def to_domain(self) -> TaiKhoan:
    #     from app.domain.models.account import TaiKhoan # Import muộn để tránh circular import
    #     return TaiKhoan(
    #         so_tai_khoan=self.so_tai_khoan,
    #         ten_tai_khoan=self.ten_tai_khoan,
    #         loai_tai_khoan=self.loai_tai_khoan,
    #         cap_tai_khoan=self.cap_tai_khoan,
    #         so_tai_khoan_cha=self.so_tai_khoan_cha,
    #         la_tai_khoan_tong_hop=self.la_tai_khoan_tong_hop
    #     )
