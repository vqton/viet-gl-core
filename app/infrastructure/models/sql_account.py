# File: app/infrastructure/models/sql_account.py
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum as SQLEnum

from app.infrastructure.base import Base
from app.domain.models.account import LoaiTaiKhoan   # enum, KHÔNG phải entity


class SQLAccount(Base):
    """
    ORM Model đại diện bảng 'accounts'.
    """
    __tablename__ = "accounts"

    # Primary key
    so_tai_khoan = Column(String(20), primary_key=True, index=True)

    # Columns
    ten_tai_khoan = Column(String(256), nullable=False)
    loai_tai_khoan = Column(SQLEnum(LoaiTaiKhoan), nullable=False)
    cap_tai_khoan = Column(Integer, nullable=False, default=1)

    so_tai_khoan_cha = Column(String(20), ForeignKey("accounts.so_tai_khoan"), nullable=True)
    la_tai_khoan_tong_hop = Column(Boolean, nullable=False, default=True)

    # Self relationship (optional)
    parent = relationship("SQLAccount", remote_side=[so_tai_khoan], backref="children")

    def __repr__(self):
        return f"<SQLAccount {self.so_tai_khoan} - {self.ten_tai_khoan}>"
