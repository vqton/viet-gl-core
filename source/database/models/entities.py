"""
PATH: D:/TT99ACCT/source/database/models/entities.py
"""

from sqlalchemy import Column, String, Boolean, Integer, CheckConstraint, Index
from ..base import Base, EnterpriseMixin


class EntityModel(Base, EnterpriseMixin):
    __tablename__ = "entities"

    # Khóa chính cứng với độ dài giới hạn để tối ưu Index
    entity_id = Column(String(50), primary_key=True)

    # Thông tin định danh
    name = Column(String(255), nullable=False)
    tax_code = Column(
        String(20), unique=True, index=True
    )  # Cấm trùng MST trên toàn hệ thống
    address = Column(String(500))

    # Phân loại và trạng thái
    entity_type = Column(String(20), index=True)  # KH, NCC, NV, OTHER
    entity_group = Column(String(50), index=True)  # VIP, NỘI BỘ, CHI NHÁNH...

    # Quản trị rủi ro tài chính
    credit_limit = Column(Integer, default=0)  # Hạn mức nợ tối đa
    is_active = Column(Boolean, default=True, index=True)
    is_deleted = Column(Boolean, default=False, index=True)  # Soft Delete

    # Ràng buộc mức Database (Cơ bắp Enterprise)
    __table_args__ = (
        CheckConstraint("credit_limit >= 0", name="check_credit_limit_positive"),
        Index("idx_entity_lookup", "entity_type", "is_active", "is_deleted"),
    )

    def __repr__(self):
        return f"<Entity(id='{self.entity_id}', name='{self.name}', type='{self.entity_type}')>"
