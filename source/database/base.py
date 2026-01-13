from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()


class EnterpriseMixin:
    """
    Bộ khung Enterprise: Kiểm soát vết (Audit) + Chống ghi đè (Versioning)
    """

    # 1. Audit Columns
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    updated_by = Column(String, nullable=True)

    # 2. Concurrency Control (Optimistic Locking)
    # SQLAlchemy sẽ tự động tăng số này mỗi khi row được UPDATE
    version_id = Column(Integer, default=1, nullable=False)

    # Cấu hình để SQLAlchemy tự vận hành cơ chế Versioning
    __mapper_args__ = {"version_id_col": version_id}
