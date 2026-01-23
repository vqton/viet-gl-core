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
from src.domain.entities.journal_entry import JournalEntry

# Tải COA một lần khi module được import
COA_PATH = Path(__file__).parent.parent / "rules" / "coa_99.json"
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

def validate_journal_entry(entry: JournalEntry) -> bool:
    """
    Kiểm tra tính hợp lệ của bút toán kế toán theo Thông tư 99/2025/TT-BTC.
    
    Yêu cầu pháp lý:
    - Điều 11 TT 99: Sử dụng đúng hệ thống tài khoản
    - Hướng dẫn kết cấu Nợ/Có theo loại tài khoản
    
    Args:
        entry (JournalEntry): Bút toán cần kiểm tra.
        
    Returns:
        bool: True nếu bút toán hợp lệ, False nếu vi phạm.
        
    Các kiểm tra:
        1. Tài khoản có tồn tại trong COA
        2. Tài khoản doanh thu/thu nhập chỉ được ghi Có
        3. Tài khoản tài sản (trừ hao mòn, dự phòng) chỉ được ghi Nợ
    """
    # Kiểm tra 1: Tài khoản có tồn tại không
    if not is_valid_account(entry.account):
        return False
        
    # Lấy loại tài khoản từ COA
    account_type = COA[entry.account]["type"]
    
    # Kiểm tra 2: Tài khoản doanh thu/thu nhập khác chỉ được ghi Có
    if account_type in ("revenue", "other_revenue") and entry.debit > 0:
        return False
        
    # Kiểm tra 3: Tài sản (trừ hao mòn, dự phòng) chỉ được ghi Nợ
    if account_type == "asset" and entry.credit > 0:
        # Các tài khoản được phép ghi Có (hao mòn, dự phòng)
        if not entry.account.startswith(("214", "229", "159")):
            return False
            
    return True