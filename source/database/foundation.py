from sqlalchemy import Column, DateTime, String, Integer, create_all
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.sql import func

Base = declarative_base()

class AuditMixin:
    """Tự động hóa hoàn toàn việc truy vết dữ liệu"""
    created_at = Column(DateTime, server_default=func.now(), index=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by = Column(String, default="SYSTEM")
    updated_by = Column(String, default="SYSTEM")
    version_id = Column(Integer, default=1, nullable=False)

    @declared_attr
    def __mapper_args__(cls):
        return {"version_id_col": cls.version_id}

class BaseSchema(Base, AuditMixin):
    __abstract__ = True