"""
Module: Debt Creation DTO

DTO cho việc tạo công nợ mới.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

@dataclass
class DebtCreationDTO:
    """
    Dữ liệu tạo công nợ từ nghiệp vụ.
    
    Attributes:
        party_id (str): Mã đối tượng (KH/NCC).
        party_name (str): Tên đối tượng.
        party_tax_code (str): MST đối tượng.
        document_id (str): ID chứng từ gốc (hóa đơn, phiếu mua...).
        document_type (str): Loại chứng từ ("SALES", "PURCHASE").
        amount (Decimal): Số tiền công nợ.
        due_date (date): Hạn thanh toán.
        currency (str): Loại tiền tệ (mặc định VND).
    """
    party_id: str
    party_name: str
    party_tax_code: str
    document_id: str
    document_type: str
    amount: Decimal
    due_date: date
    currency: str = "VND"