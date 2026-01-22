"""
Module: Party

Đại diện cho đối tượng giao dịch (khách hàng, nhà cung cấp) theo Điều 18 TT 99.

Yêu cầu pháp lý:
- Phải quản lý công nợ chi tiết theo từng đối tượng.
- Phải phân biệt loại hình để xác định nghĩa vụ thuế.
- Phải có thông tin người đại diện (Thông tư 78/2021/TT-BTC).
"""

from dataclasses import dataclass
from enum import Enum
import re


class PartyType(Enum):
    """Loại hình đối tượng theo quy định thuế."""

    BUSINESS = "doanh_nghiep"  # MST 10/14 số
    INDIVIDUAL = "ca_nhan"  # MST cá nhân 12 số
    HOUSEHOLD = "ho_kinh_doanh"  # MST 10 số


class PartyStatus(Enum):
    """Trạng thái hoạt động của đối tượng."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    TERMINATED = "terminated"


@dataclass(frozen=True)
class Party:
    """
    Đối tượng giao dịch (khách hàng hoặc nhà cung cấp).

    Attributes:
        code (str): Mã nội bộ duy nhất (ví dụ: KH001, NCC001).
        name (str): Tên đầy đủ của tổ chức/cá nhân.
        tax_code (str): Mã số thuế (phải hợp lệ theo loại hình).
        party_type (PartyType): Loại hình pháp lý.
        address (str): Địa chỉ đăng ký kinh doanh/thường trú.
        representative_name (str): Họ và tên người đại diện pháp luật.
        representative_title (str): Chức danh người đại diện (Giám đốc, Chủ hộ...).
        bank_account_name (str): Tên chủ tài khoản ngân hàng.
        bank_account_number (str): Số tài khoản ngân hàng.
        bank_name (str): Tên ngân hàng.
        status (PartyStatus): Trạng thái hoạt động.
    """

    code: str
    name: str
    tax_code: str
    party_type: PartyType
    address: str
    representative_name: str
    representative_title: str
    bank_account_name: str = ""
    bank_account_number: str = ""
    bank_name: str = ""
    status: PartyStatus = PartyStatus.ACTIVE

    def __post_init__(self):
        """Validate MST theo loại hình — bắt buộc theo Luật Quản lý Thuế."""
        if self.party_type == PartyType.BUSINESS:
            if not re.fullmatch(r"^\d{10}$|^\d{14}$", self.tax_code):
                raise ValueError("MST doanh nghiệp phải có 10 hoặc 14 chữ số")
        elif self.party_type == PartyType.INDIVIDUAL:
            if not re.fullmatch(r"^\d{12}$", self.tax_code):
                raise ValueError("MST cá nhân phải có 12 chữ số")
        elif self.party_type == PartyType.HOUSEHOLD:
            if not re.fullmatch(r"^\d{10}$", self.tax_code):
                raise ValueError("MST hộ kinh doanh phải có 10 chữ số")
