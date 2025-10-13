# tests/test_reporting.py
import pytest
from decimal import Decimal
from pathlib import Path

from gl_core.models import AccountChart, Ledger, JournalEntry, JournalLine
from gl_core.services import generate_balance_sheet, generate_income_statement


@pytest.fixture
def sample_ledger():
    coa = AccountChart.from_yaml(
        str(Path(__file__).parent.parent / "gl_core" / "config" / "tt133_coa.yaml")
    )
    ledger = Ledger(coa)
    
    # Ghi sổ: bán hàng thu tiền mặt
    entry1 = JournalEntry(
        date="2025-04-01",
        lines=[
            JournalLine("1111", debit=Decimal("10000000")),  # Tiền Việt Nam
            JournalLine("5111", credit=Decimal("10000000")),  # Doanh thu bán hàng
        ]
    )
    # Ghi giá vốn
    entry2 = JournalEntry(
        date="2025-04-02",
        lines=[
            JournalLine("632", debit=Decimal("3000000")),  # Giá vốn hàng bán
            JournalLine("156", credit=Decimal("3000000")),  # Hàng hóa
        ]
    )
    ledger.post(entry1)
    ledger.post(entry2)
    return ledger


def test_generate_balance_sheet(sample_ledger):
    config_path = Path(__file__).parent.parent / "gl_core" / "config" / "reports" / "b01_dnn.yaml"
    
    report = generate_balance_sheet(sample_ledger, str(config_path), period="2025-Q1")
    
    assert report["report_type"] == "B01-DNN"
    assert "A. TÀI SẢN NGẮN HẠN" in report["data"]
    
    # Kiểm tra dòng tiền (đã cập nhật cấu hình để dùng 1111)
    cash_line = report["data"]["A. TÀI SẢN NGẮN HẠN"].get("1. Tiền và các khoản tương đương tiền")
    assert cash_line == Decimal("10000000")


def test_generate_income_statement(sample_ledger):
    config_path = Path(__file__).parent.parent / "gl_core" / "config" / "reports" / "b02_dnn.yaml"
    
    report = generate_income_statement(sample_ledger, str(config_path), period="2025-Q1")
    
    assert report["report_type"] == "B02-DNN"
    # Kiểm tra doanh thu (đã cập nhật cấu hình để dùng 5111)
    revenue = report["data"]["Doanh thu"].get("Doanh thu bán hàng và cung cấp dịch vụ")
    assert revenue == Decimal("10000000")
    
    # Kiểm tra giá vốn
    cost = report["data"]["Giá vốn"].get("Giá vốn hàng bán")
    assert cost == Decimal("3000000")