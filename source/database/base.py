# PATH: D:\tt99acct\source/database/base.py
"""
PATH: source/database/base.py
STATUS: Production-ready
DESCRIPTION: 
    Lớp cơ sở (Base Class) định nghĩa các tiêu chuẩn dữ liệu cho toàn hệ thống.
    Đảm bảo tính nhất quán (Integrity), kiểm soát tranh chấp (Concurrency) 
    và dấu vết kiểm toán (Audit Trail) theo TT99.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func
from sqlalchemy import String, Boolean, Integer

class Base(DeclarativeBase):
    """Giao diện SQLAlchemy 2.0 cho mọi Model"""
    pass

class EnterpriseMixin:
    """
    Mixin cung cấp các tiêu chuẩn Production cho mọi bảng trong hệ thống.
    """
    # --- AUDIT TRAIL: Theo dõi dấu vết theo Thông tư 99 ---
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), comment="Ngày tạo")
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())
    created_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="Người tạo")
    updated_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment="Người sửa")

    # --- DATA INTEGRITY: Bảo vệ dữ liệu lịch sử ---
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="Trạng thái hoạt động (Soft Delete)")
    
    # --- CONCURRENCY: Optimistic Locking cho môi trường Production ---
    # Ngăn chặn ghi đè dữ liệu khi nhiều kế toán làm việc cùng lúc
    version_id: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __mapper_args__ = {
        "version_id_col": version_id
    }