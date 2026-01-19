# Path: source/database/models/ledger.py
"""
General Ledger Model Module.

Lưu trữ nhật ký chung và các bút toán chi tiết (Sổ cái). Đây là bảng dữ liệu
quan trọng nhất, là cơ sở để kết xuất tất cả các báo cáo tài chính.
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from source.database.foundation import Base, EnterpriseMixin

class GeneralLedger(Base, EnterpriseMixin):
    """
    Model lưu trữ chi tiết từng dòng bút toán (Entry).
    
    Attributes:
        id (int): Định danh duy nhất cho mỗi dòng nghiệp vụ.
        transaction_date (datetime): Ngày hạch toán thực tế.
        voucher_no (str): Số chứng từ gốc (Số phiếu thu, phiếu chi, hóa đơn...).
        description (str): Diễn giải nội dung kinh tế của nghiệp vụ.
        account_id (str): Tài khoản đối ứng (Liên kết đến bảng accounts).
        debit (float): Số tiền phát sinh bên Nợ.
        credit (float): Số tiền phát sinh bên Có.
        partner_id (str): Đối tượng chi tiết (Liên kết đến bảng entities) dùng cho quản lý công nợ.
    """
    __tablename__ = "general_ledger"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    transaction_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, index=True)
    voucher_no: Mapped[str] = mapped_column(String(50), index=True)
    description: Mapped[str] = mapped_column(String(500))
    
    account_id: Mapped[str] = mapped_column(String(20), ForeignKey("accounts.id"))
    debit: Mapped[float] = mapped_column(Float, default=0.0)
    credit: Mapped[float] = mapped_column(Float, default=0.0)
    
    partner_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("entities.id"), nullable=True)

    def __repr__(self):
        return f"<Ledger {self.voucher_no}: {self.account_id} Dr:{self.debit} Cr:{self.credit}>"