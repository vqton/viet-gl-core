from sqlalchemy import Column, String, Boolean, JSON, ForeignKey
from source.database.foundation import BaseSchema

class Customer(BaseSchema):
    __tablename__ = "customers"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    tax_code = Column(String, index=True)
    address = Column(String)
    
    # Đặc thù CRM & Finance
    is_active = Column(Boolean, default=True)
    default_receivable_acc = Column(String, ForeignKey("accounts.id"))
    
    # Metadata: Lưu credit_limit, sales_pic, payment_terms...
    crm_info = Column(JSON)