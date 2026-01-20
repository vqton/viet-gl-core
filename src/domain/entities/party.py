"""
Module: Party

Đại diện cho đối tượng giao dịch (khách hàng, nhà cung cấp) theo Điều 18 TT 99.

Yêu cầu pháp lý:
- Phải quản lý công nợ chi tiết theo từng đối tượng.
- Phải phân biệt loại hình để xác định nghĩa vụ thuế.
"""

from dataclasses import dataclass
from enum import Enum

class PartyType(Enum):
    """Loại hình đối tượng theo quy định thuế."""
    BUSINESS = "doanh_nghiep"     # MST 10/14 số
    INDIVIDUAL = "ca_nhan"        # MST cá nhân 12 số
    HOUSEHOLD = "ho_kinh_doanh"

@dataclass(frozen=True)
class Party:
    """
    Đối tượng giao dịch (khách hàng hoặc nhà cung cấp).

    Attributes:
        code (str): Mã nội bộ.
        name (str): Tên đầy đủ.
        tax_code (str): Mã số thuế (phải hợp lệ theo loại hình).
        party_type (PartyType): Loại hình pháp lý.
        address (str): Địa chỉ liên hệ.
    """
    code: str
    name: str
    tax_code: str
    party_type: PartyType
    address: str