# tests/test_account_chart.py
import pytest
from pathlib import Path

from models.account import AccountChart

def test_load_tt133_coa():
    coa = AccountChart.from_yaml("config/tt133_coa.yaml")
    
    # Kiểm tra số lượng tài khoản (ít nhất 30)
    assert len(coa.accounts) >= 30
    
    # Kiểm tra tài khoản cụ thể
    cash = coa.get("1111")
    assert cash.name == "Tiền Việt Nam"
    assert cash.account_type.value == "asset"
    assert cash.normal_balance == "debit"
    
    revenue = coa.get("5111")
    assert revenue.normal_balance == "credit"

def test_invalid_yaml_path():
    with pytest.raises(FileNotFoundError):
        AccountChart.from_yaml("non_existent.yaml")