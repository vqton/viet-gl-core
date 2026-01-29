"""
Module: Cash Transaction DTO

DTO cho giao dịch tiền mặt/tiền gửi.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum


class CashTransactionType(Enum):
    """Loại giao dịch tiền."""

    CASH_IN = "cash_in"  # Thu tiền mặt
    CASH_OUT = "cash_out"  # Chi tiền mặt
    BANK_IN = "bank_in"  # Thu tiền gửi
    BANK_OUT = "bank_out"  # Chi tiền gửi


@dataclass
class CashTransactionDTO:
    """
    Dữ liệu giao dịch tiền từ UI/API.

    Attributes:
        transaction_number (str): Số chứng từ.
        transaction_date (date): Ngày giao dịch.
        transaction_type (CashTransactionType): Loại giao dịch.
        amount (Decimal): Số tiền.
        description (str): Diễn giải.
        related_document_id (str): ID chứng từ liên quan (hóa đơn, phiếu chi...).
        currency (str): Loại tiền tệ (mặc định VND).
    """

    transaction_number: str
    transaction_date: date
    transaction_type: CashTransactionType
    amount: Decimal
    description: str
    related_document_id: str = ""
    currency: str = "VND"
