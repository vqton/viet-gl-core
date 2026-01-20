"""
Module: COAValidator

Validator kiểm tra tính hợp lệ của tài khoản kế toán theo Phụ lục II TT 99.

Yêu cầu pháp lý:
- Không được sử dụng tài khoản ngoài hệ thống (Điều 11 TT 99)
- Không được ghi Nợ vào TK doanh thu, Có vào TK tài sản (trừ hao mòn, dự phòng)
"""

import json
from pathlib import Path
from decimal import Decimal

# Tải COA một lần khi module được import
COA_PATH = Path(__file__).parent.parent / "rules" / "coa_99_full.json"
with open(COA_PATH, encoding="utf-8") as f:
    COA = json.load(f)

def is_valid_account(account_code: str) -> bool:
    """
    Kiểm tra tài khoản có tồn tại trong hệ thống TT 99 không.

    Args:
        account_code (str): Mã tài khoản (ví dụ: "5111").

    Returns:
        bool: True nếu hợp lệ.
    """
    return account_code in COA

def is_debit_allowed(account_code: str) -> bool:
    """
    Kiểm tra có được ghi Nợ vào tài khoản này không.

    Args:
        account_code (str): Mã tài khoản.

    Returns:
        bool: True nếu được phép ghi Nợ.
    """
    if not is_valid_account(account_code):
        return False
    account_type = COA[account_code]["type"]
    # Doanh thu và thu nhập khác chỉ ghi Có
    if account_type in ("revenue", "other_revenue"):
        return False
    return True

def is_credit_allowed(account_code: str) -> bool:
    """
    Kiểm tra có được ghi Có vào tài khoản này không.

    Args:
        account_code (str): Mã tài khoản.

    Returns:
        bool: True nếu được phép ghi Có.
    """
    if not is_valid_account(account_code):
        return False
    account_type = COA[account_code]["type"]
    # Tài sản (trừ hao mòn, dự phòng) chỉ ghi Nợ
    if account_type == "asset" and not account_code.startswith(("214", "229", "159")):
        return False
    return True