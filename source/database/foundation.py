# Path: source/database/foundation.py
"""
Foundation Module.

Thiết lập nền tảng ORM, cấu hình kết nối Database và các Mixins dùng chung
để đảm bảo tính nhất quán về Audit Trail (Vết kiểm toán) và Concurrency Control.
"""

from datetime import datetime
from sqlalchemy import create_engine, String, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# URL kết nối duy nhất: Tập trung dữ liệu về một file duy nhất
DB_URL = "sqlite:///D:/TT99ACCT/data/finance.db"
engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    """Lớp cơ sở (Base) cho tất cả các Model trong hệ thống."""
    pass

class EnterpriseMixin:
    """
    Mixin cung cấp các trường chuẩn doanh nghiệp cho mục đích kiểm soát và bảo mật.
    
    Attributes:
        version_id (int): Triển khai Optimistic Locking. Mỗi lần UPDATE, số version sẽ tự tăng. 
                         Nếu hai người cùng sửa một lúc, người lưu sau sẽ thất bại nếu version đã thay đổi.
        created_at (datetime): Thời điểm khởi tạo bản ghi lần đầu.
        updated_at (datetime): Thời điểm bản ghi được cập nhật lần cuối cùng.
        created_by (str): Định danh người dùng thực hiện tạo bản ghi (User ID).
        updated_by (str): Định danh người dùng thực hiện chỉnh sửa bản ghi cuối cùng.
    """
    # Concurrency Control
    version_id: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Audit Trail (Vết kiểm toán)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by: Mapped[str] = mapped_column(String(50), nullable=True)
    updated_by: Mapped[str] = mapped_column(String(50), nullable=True)

    __mapper_args__ = {
        "version_id_col": version_id 
    }