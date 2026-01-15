# PATH: D:\tt99acct\source/database/models/entities.py
"""
PATH: source/database/models/entities.py
STATUS: Production-ready
DESCRIPTION: 
    Quản lý danh mục đối tượng pháp lý (Entities) tham gia vào các giao dịch.
    Bao gồm: Khách hàng (Customer), Nhà cung cấp (Vendor), Nhân viên (Employee).
IMPACT REVIEW:
    - Ảnh hưởng đến SyncService: Cần bổ sung logic nạp Entity.
    - Ảnh hưởng đến Vouchers (Sắp tới): Dùng làm khóa ngoại cho các phiếu Thu/Chi.
"""

from typing import Optional
from sqlalchemy import String, Index, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates
from ..base import Base, EnterpriseMixin

class EntityModel(Base, EnterpriseMixin):
    """
    Model Đối tượng (Master Data).
    Tuân thủ MDM: Tax Code là duy nhất, phân loại rõ ràng loại đối tượng.
    """
    __tablename__ = "entities"

    # --- ĐỊNH DANH ---
    id: Mapped[str] = mapped_column(String(20), primary_key=True, comment="Mã đối tượng (Ví dụ: KH001)")
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Tên đối tượng/Công ty")
    
    # --- THÔNG TIN THUẾ & PHÁP LÝ ---
    tax_code: Mapped[Optional[str]] = mapped_column(String(20), index=True, comment="Mã số thuế")
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # --- PHÂN LOẠI (CUSTOMER, VENDOR, EMPLOYEE, OTHER) ---
    entity_type: Mapped[str] = mapped_column(String(20), index=True, default="CUSTOMER")

    # --- PRODUCTION-READY CONSTRAINTS ---
    __table_args__ = (
        CheckConstraint("length(id) >= 2", name="ck_entity_id_length"),
        # Index hỗ trợ tìm kiếm nhanh theo tên hoặc mã số thuế khi lập chứng từ
        Index("ix_entities_name_tax", "name", "tax_code"),
    )

    @validates("tax_code")
    def validate_tax_code(self, key, value):
        # Logic MDM Cleanse: Loại bỏ dấu gạch ngang hoặc khoảng trắng trong MST
        if value:
            return value.replace("-", "").replace(" ", "")
        return value

    def __repr__(self) -> str:
        return f"<Entity(id={self.id}, name={self.name}, type={self.entity_type})>"