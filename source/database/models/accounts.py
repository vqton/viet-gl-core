from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from source.database.foundation import BaseSchema

class Account(BaseSchema):
    """Hệ thống tài khoản kế toán chuẩn"""
    __tablename__ = "accounts"

    id = Column(String, primary_key=True) # Số hiệu TK (e.g., '111', '112')
    name = Column(String, nullable=False)
    
    # Cấu trúc cây
    parent_id = Column(String, ForeignKey("accounts.id"), nullable=True)
    
    # Tính chất tài khoản
    acc_type = Column(String) # ASSET, LIABILITY, EQUITY, REVENUE, EXPENSE
    nature = Column(String)   # DEBIT (Dư Nợ), CREDIT (Dư Có), BOTH (Lưỡng tính)

    # Quan hệ cha-con nội bộ
    children = relationship("Account", backref="parent", remote_side=[id])

    def __repr__(self):
        return f"<Account(id={self.id}, name={self.name})>"