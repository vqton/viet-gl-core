"""
Module: Accounting Policy DTO

DTO cho chính sách kế toán doanh nghiệp.

Yêu cầu pháp lý:
- Phải lưu phương pháp tính giá vốn đã đăng ký
- Phải ghi nhận thời điểm áp dụng
"""

from dataclasses import dataclass
from enum import Enum

class ValuationMethod(Enum):
    """Các phương pháp tính giá vốn theo TT 99."""
    FIFO = "fifo"
    WEIGHTED_AVERAGE = "weighted_average"
    SPECIFIC_IDENTIFICATION = "specific_identification"

@dataclass
class AccountingPolicyDTO:
    """
    Chính sách kế toán hiện tại của doanh nghiệp.
    
    Attributes:
        inventory_valuation_method (ValuationMethod): Phương pháp tính giá vốn.
        effective_date (str): Ngày áp dụng (YYYY-MM-DD).
        is_locked (bool): Đã khóa sổ → không được đổi chính sách.
    """
    inventory_valuation_method: ValuationMethod
    effective_date: str
    is_locked: bool = False