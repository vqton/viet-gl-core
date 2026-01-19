# Path: source/database/models/ledger.py
"""
MODULE: ledger.py
PURPOSE: Định nghĩa bảng Sổ cái (General Ledger) - "Xương sống" của dữ liệu kế toán.
Lưu trữ toàn bộ các phát sinh kinh tế (bút toán) và liên kết các đối tác liên quan.
"""

from sqlalchemy import Column, String, Float, ForeignKey, Date, Integer, JSON
from sqlalchemy.orm import relationship
from source.database.foundation import BaseSchema

class GeneralLedger(BaseSchema):
    """
    Model đại diện cho Sổ cái kế toán (General Ledger).

    Mỗi bản ghi trong bảng này tương ứng với một dòng định khoản (Nợ hoặc Có).
    Sử dụng kỹ thuật Polymorphic Mapping đơn giản để liên kết linh hoạt với 
    Khách hàng (Customer), Nhà cung cấp (Vendor) hoặc Nhân viên (Employee).

    Attributes:
        id (int): Khóa chính tự tăng.
        transaction_date (Date): Ngày hạch toán (Ngày ghi sổ).
        voucher_no (str): Số chứng từ gốc (Số phiếu thu, phiếu chi, hóa đơn).
        description (str): Diễn giải nội dung nghiệp vụ.
        account_id (str): Khóa ngoại liên kết tới Hệ thống tài khoản (accounts).
        partner_id (str): Mã định danh của đối tượng liên quan (Không dùng FK cứng).
        partner_type (str): Phân loại đối tượng (CUSTOMER, VENDOR, EMPLOYEE).
        debit (float): Số tiền phát sinh bên Nợ.
        credit (float): Số tiền phát sinh bên Có.
        currency (str): Loại tiền tệ (Mặc định: VND).
        tags (JSON): Lưu trữ các thẻ phân loại bổ sung (vùng miền, dự án, v.v.).
    """
    __tablename__ = "general_ledger"

    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Thông tin chứng từ
    transaction_date = Column(Date, nullable=False, index=True)
    voucher_no = Column(String, index=True)  # Số hiệu chứng từ gốc
    description = Column(String)             # Diễn giải chi tiết nghiệp vụ

    # Định khoản Nợ/Có
    account_id = Column(String, ForeignKey("accounts.id"), nullable=False, index=True)
    
    # Quản lý đối tượng công nợ linh hoạt
    partner_id = Column(String, index=True, nullable=True) 
    partner_type = Column(String, index=True, nullable=True) # VD: 'CUSTOMER', 'VENDOR', 'EMPLOYEE'

    # Giá trị giao dịch
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)
    currency = Column(String, default="VND")

    # Thông tin mở rộng cho báo cáo quản trị
    tags = Column(JSON) 

    # Thiết lập mối quan hệ với bảng Tài khoản
    account = relationship("Account")

    def __repr__(self):
        """Trả về đại diện chuỗi của bút toán để phục vụ logging/debugging."""
        return f"<Ledger(Date={self.transaction_date}, Acc={self.account_id}, Debit={self.debit}, Credit={self.credit})>"