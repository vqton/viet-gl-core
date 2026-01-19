from sqlalchemy import Column, String, Float, ForeignKey, Date, Integer, JSON
from sqlalchemy.orm import relationship
from source.database.foundation import BaseSchema

class GeneralLedger(BaseSchema):
    """
    Sổ cái (General Ledger) - Nơi lưu trữ mọi bút toán hạch toán.
    Kết nối Hệ thống tài khoản với các đối tác (Customer, Vendor, Employee).
    """
    __tablename__ = "general_ledger"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Thông tin chứng từ
    transaction_date = Column(Date, nullable=False, index=True)
    voucher_no = Column(String, index=True)  # Số số phiếu thu/chi, hóa đơn
    description = Column(String)             # Diễn giải nghiệp vụ

    # Định khoản Nợ/Có
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False, index=True)
    
    # Định danh đối tượng (Polymorphic-like Relationship)
    # Vì Ledger có thể liên kết với Khách hàng, NCC hoặc NV nên ta dùng cặp ID + Type
    partner_id = Column(String, index=True, nullable=True) 
    partner_type = Column(String, index=True, nullable=True) # 'CUSTOMER', 'VENDOR', 'EMPLOYEE'

    # Số tiền hạch toán
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    currency = Column(String, default="VND")

    # Metadata bổ sung (Dùng để lưu thông tin đặc thù của giao dịch nếu cần)
    tags = Column(JSON) 

    # Quan hệ với bảng Tài khoản
    account = relationship("Account")

    def __repr__(self):
        return f"<Ledger(Date={self.transaction_date}, Acc={self.account_id}, Debit={self.debit}, Credit={self.credit})>"