"""
PATH: D:/TT99ACCT/tests/test_accounting.py
"""

import random
import pytest
from datetime import datetime
from source.services.accounting_service import ACC_SERVICE


def test_unbalanced_voucher():
    """TC-01: Kiểm tra chứng từ không cân (Nợ != Có)"""
    entries = [
        {"account_id": "131", "debit": 1000, "credit": 0, "entity_id": "KH_001"},
        {"account_id": "511", "debit": 0, "credit": 500},  # Cố tình làm lệch
    ]
    status, msg = ACC_SERVICE.post_voucher(
        "PK", "TEST_LỆCH", datetime.now(), "Test", entries
    )

    assert status is False
    assert "không cân" in msg.lower()


def test_invalid_account_id():
    """TC-02: Kiểm tra tài khoản không có trong danh mục Master"""
    entries = [{"account_id": "9999", "debit": 100, "credit": 100}]
    status, msg = ACC_SERVICE.post_voucher(
        "PK", "TEST_TK", datetime.now(), "Test", entries
    )

    assert status is False
    assert "không tồn tại" in msg.lower()


def test_trial_balance_consistency():
    """TC-A03: Kiểm tra tính cân đối tuyệt đối của Bảng cân đối phát sinh"""
    # 1. Tạo dữ liệu ngẫu nhiên nhưng phải cân đối
    for i in range(10):
        amount = random.randint(1000, 1000000)
        v_no = f"TEST_TB_{i}"
        entries = [
            {
                "account_id": "111",
                "debit": amount,
                "credit": 0,
                "description": "Thu tiền",
            },
            {
                "account_id": "511",
                "debit": 0,
                "credit": amount,
                "description": "Doanh thu",
            },
        ]
        ACC_SERVICE.post_voucher("PT", v_no, datetime.now(), f"Test TB {i}", entries)

    # 2. Gọi hàm lõi để lấy Trial Balance
    tb = ACC_SERVICE.get_trial_balance()

    # 3. QA Assertions
    assert tb["is_balanced"] is True, "Bảng cân đối phát sinh bị lệch Nợ/Có!"
    assert tb["grand_total_debit"] == tb["grand_total_credit"]
    print(f"\n[QA Check] Tổng phát sinh Nợ: {tb['grand_total_debit']:,.0f}")
    print(f"[QA Check] Tổng phát sinh Có: {tb['grand_total_credit']:,.0f}")


def test_trial_balance_data_structure():
    """TC-A04: Kiểm tra cấu trúc dữ liệu trả về của Trial Balance"""
    tb = ACC_SERVICE.get_trial_balance()

    assert "details" in tb
    assert isinstance(tb["details"], list)
    if len(tb["details"]) > 0:
        first_row = tb["details"][0]
        assert "account_id" in first_row
        assert "debit" in first_row
        assert "credit" in first_row
