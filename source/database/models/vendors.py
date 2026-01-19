from sqlalchemy import Column, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from source.database.foundation import BaseSchema

class Vendor(BaseSchema):
    """Danh mục Nhà cung cấp - Procurement & Payables"""
    __tablename__ = "vendors"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    tax_code = Column(String, index=True)
    address = Column(String)
    email = Column(String)
    phone = Column(String)
    
    is_active = Column(Boolean, default=True)

    # Tài khoản công nợ mặc định (thường là 331)
    default_payable_acc_id = Column(String, ForeignKey("accounts.id"))
    default_account = relationship("Account")

    # Lưu bank_info, payment_terms, lead_time... từ JSON
    metadata_info = Column(JSON)

    def __repr__(self):
        return f"<Vendor(id={self.id}, name={self.name})>"