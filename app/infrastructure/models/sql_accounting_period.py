# File: app/infrastructure/models/sql_accounting_period.py

from sqlalchemy import Column, Integer, String, Date, DateTime
from app.infrastructure.base import Base # Giả sử Base được định nghĩa ở đây hoặc import từ đúng nơi

class SQLAccountingPeriod(Base):
    """
    ORM Model đại diện cho bảng 'accounting_periods'.
    """
    __tablename__ = 'accounting_periods'

    id = Column(Integer, primary_key=True, index=True)
    ten_ky = Column(String(100), nullable=False, unique=True) # Tên kỳ phải là duy nhất
    ngay_bat_dau = Column(Date, nullable=False)
    ngay_ket_thuc = Column(Date, nullable=False)
    trang_thai = Column(String(20), nullable=False, default="Open") # "Open", "Locked"
    ghi_chu = Column(String(512), nullable=True)
    # created_at = Column(DateTime, default=datetime.utcnow)
    # updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)