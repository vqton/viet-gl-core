from sqlalchemy import Column, String, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from source.database.foundation import BaseSchema

class Employee(BaseSchema):
    """Danh mục Nhân viên - HR & Payroll"""
    __tablename__ = "employees"

    id = Column(String, primary_key=True) # Mã nhân viên
    name = Column(String, nullable=False)
    email = Column(String)
    phone = Column(String)
    department = Column(String, index=True)
    position = Column(String)

    is_active = Column(Boolean, default=True)

    # Tài khoản tạm ứng/lương mặc định (thường là 141, 334)
    default_advance_acc_id = Column(String, ForeignKey("accounts.id"))
    default_account = relationship("Account")

    # Lưu id_card, dependents, salary_base, social_insurance... từ JSON
    metadata_info = Column(JSON)

    def __repr__(self):
        return f"<Employee(id={self.id}, name={self.name})>"