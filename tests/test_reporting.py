# tests/test_reporting.py
"""
Test suite for reporting module (B01-DNN, B02-DNN)
- Tests integration between Ledger, Report generation, and YAML config
- Covers before/after year-end closing
- Validates formulas in reports
- Uses controlled data for reliability
"""
import pytest
from decimal import Decimal
from pathlib import Path

from gl_core.services import generate_balance_sheet, generate_income_statement
from gl_core.services.closing import close_year
from gl_core.models import Ledger, JournalEntry, JournalLine, AccountChart


@pytest.fixture
def sample_coa():
    """
    Load COA from YAML for test
    """
    config_path = Path(__file__).parent.parent / "gl_core" / "config" / "tt133_coa.yaml"
    return AccountChart.from_yaml(str(config_path))


@pytest.fixture
def ledger_with_revenue_and_expense(sample_coa):
    """
    Create a ledger with sample revenue and expense data
    """
    ledger = Ledger(sample_coa)

    # Ghi doanh thu: 10,000,000
    ledger.post(JournalEntry(
        date="2025-04-01",
        lines=[
            JournalLine("1111", debit=Decimal("10000000")),  # Tiền mặt
            JournalLine("5111", credit=Decimal("10000000")), # Doanh thu bán hàng
        ]
    ))

    # Ghi giá vốn: 3,000,000
    ledger.post(JournalEntry(
        date="2025-04-02",
        lines=[
            JournalLine("632", debit=Decimal("3000000")),  # Giá vốn hàng bán
            JournalLine("156", credit=Decimal("3000000")), # Hàng hóa
        ]
    ))

    # Ghi chi phí bán hàng: 1,000,000
    ledger.post(JournalEntry(
        date="2025-04-03",
        lines=[
            JournalLine("641", debit=Decimal("1000000")),  # Chi phí bán hàng
            JournalLine("1111", credit=Decimal("1000000")), # Tiền mặt
        ]
    ))

    # Ghi chi phí QLDN: 500,000
    ledger.post(JournalEntry(
        date="2025-04-04",
        lines=[
            JournalLine("642", debit=Decimal("500000")),   # Chi phí QLDN
            JournalLine("1111", credit=Decimal("500000")), # Tiền mặt
        ]
    ))

    return ledger


@pytest.fixture
def ledger_after_closing(ledger_with_revenue_and_expense):
    """
    Same ledger but after year-end closing
    """
    close_year(ledger_with_revenue_and_expense, 2025)
    return ledger_with_revenue_and_expense


def test_generate_balance_sheet_before_closing(ledger_with_revenue_and_expense):
    """
    Test B01-DNN report before year-end closing
    """
    config_path = Path(__file__).parent.parent / "gl_core" / "config" / "reports" / "b01_dnn.yaml"
    report = generate_balance_sheet(ledger_with_revenue_and_expense, str(config_path), period="2025-Q1")

    assert report["report_type"] == "B01-DNN"
    assert report["period"] == "2025-Q1"

    # Check cash amount
    cash_section = report["data"]["A. TÀI SẢN NGẮN HẠN"]
    cash_line = cash_section.get("1. Tiền và các khoản tương đương tiền")
    assert cash_line == Decimal("8500000")  # 10M - 1M - 0.5M

    # Check inventory decrease
    inventory_line = cash_section.get("4. Hàng tồn kho")
    assert inventory_line == Decimal("-3000000")  # Negative because credit > debit


def test_generate_income_statement_before_closing(ledger_with_revenue_and_expense):
    """
    Test B02-DNN report before year-end closing
    """
    config_path = Path(__file__).parent.parent / "gl_core" / "config" / "reports" / "b02_dnn.yaml"
    report = generate_income_statement(ledger_with_revenue_and_expense, str(config_path), period="2025-Q1")

    assert report["report_type"] == "B02-DNN"
    assert report["period"] == "2025-Q1"

    # Check revenue
    revenue_section = report["data"]["Doanh thu"]
    revenue_line = revenue_section.get("Doanh thu bán hàng và cung cấp dịch vụ")
    assert revenue_line == Decimal("10000000")

    # Check cost of goods sold
    cost_section = report["data"]["Giá vốn"]
    cost_line = cost_section.get("Giá vốn hàng bán")
    assert cost_line == Decimal("3000000")

    # Check gross profit (computed by formula)
    gross_section = report["data"]["Lợi nhuận gộp"]
    gross_line = gross_section.get("Lợi nhuận gộp về bán hàng và cung cấp dịch vụ")
    expected_gross = Decimal("10000000") - Decimal("3000000")
    assert gross_line == expected_gross

    # Check operating expenses
    operating_section = report["data"]["Chi phí"]
    sales_expense = operating_section.get("Chi phí bán hàng")
    admin_expense = operating_section.get("Chi phí quản lý doanh nghiệp")
    assert sales_expense == Decimal("1000000")
    assert admin_expense == Decimal("500000")

    # Check net profit from operations
    net_op_section = report["data"]["Lợi nhuận thuần từ HĐKD"]
    net_op_line = net_op_section.get("Lợi nhuận thuần từ hoạt động kinh doanh")
    expected_net_op = expected_gross - Decimal("1000000") - Decimal("500000")
    assert net_op_line == expected_net_op


def test_generate_income_statement_after_closing(ledger_after_closing):
    """
    Test B02-DNN report after year-end closing
    After closing, revenue/expense accounts should be zero, profit moved to 421
    """
    config_path = Path(__file__).parent.parent / "gl_core" / "config" / "reports" / "b02_dnn.yaml"
    report = generate_income_statement(ledger_after_closing, str(config_path), period="2025-Q1")

    assert report["report_type"] == "B02-DNN"
    assert report["period"] == "2025-Q1"

    # After closing, revenue/expense accounts should have net balance = 0
    # So they should not appear in the report (because total = 0)
    revenue_section = report["data"]["Doanh thu"]
    revenue_line = revenue_section.get("Doanh thu bán hàng và cung cấp dịch vụ")
    
    # The line should not exist in the report because total is 0
    assert revenue_line is None

    cost_section = report["data"]["Giá vốn"]
    cost_line = cost_section.get("Giá vốn hàng bán")
    assert cost_line is None

    # Check that profit is reflected in equity (in B01-DNN)
    # Here we check that the profit was calculated correctly before closing
    # Since we can't compute from closed accounts, we rely on the fact that closing was correct


def test_generate_balance_sheet_after_closing(ledger_after_closing):
    """
    Test B01-DNN report after year-end closing
    Check that profit is reflected in equity
    """
    config_path = Path(__file__).parent.parent / "gl_core" / "config" / "reports" / "b01_dnn.yaml"
    report = generate_balance_sheet(ledger_after_closing, str(config_path), period="2025-Q1")

    assert report["report_type"] == "B01-DNN"
    assert report["period"] == "2025-Q1"

    # Check that profit is reflected in equity (421)
    equity_section = report["data"]["D. VỐN CHỦ SỞ HỮU"]
    retained_earnings = equity_section.get("22. Lợi nhuận sau thuế chưa phân phối")
    
    # Expected profit: 10M - 3M - 1M - 0.5M = 5.5M
    expected_profit = Decimal("5500000")
    assert retained_earnings == expected_profit


def test_report_config_validation():
    """
    Test that report config files are valid YAML and have expected structure
    """
    import yaml
    
    b01_path = Path(__file__).parent.parent / "gl_core" / "config" / "reports" / "b01_dnn.yaml"
    b02_path = Path(__file__).parent.parent / "gl_core" / "config" / "reports" / "b02_dnn.yaml"

    with open(b01_path, 'r', encoding='utf-8') as f:
        b01_config = yaml.safe_load(f)
    with open(b02_path, 'r', encoding='utf-8') as f:
        b02_config = yaml.safe_load(f)

    # Validate structure
    assert "report" in b01_config
    assert "structure" in b01_config
    assert b01_config["report"] == "B01-DNN"

    assert "report" in b02_config
    assert "structure" in b02_config
    assert b02_config["report"] == "B02-DNN"


def test_formula_calculation_in_income_statement(ledger_with_revenue_and_expense):
    """
    Test that formulas in B02-DNN are computed correctly
    e.g., Gross Profit = Revenue - COGS
    """
    config_path = Path(__file__).parent.parent / "gl_core" / "config" / "reports" / "b02_dnn.yaml"
    report = generate_income_statement(ledger_with_revenue_and_expense, str(config_path), period="2025-Q1")

    # Extract values used in formula
    revenue = report["data"]["Doanh thu"]["Doanh thu bán hàng và cung cấp dịch vụ"]
    cogs = report["data"]["Giá vốn"]["Giá vốn hàng bán"]
    gross_profit = report["data"]["Lợi nhuận gộp"]["Lợi nhuận gộp về bán hàng và cung cấp dịch vụ"]

    # Verify formula: Gross = Revenue - COGS
    assert gross_profit == revenue - cogs

    # Check net profit from operations
    sales_expense = report["data"]["Chi phí"]["Chi phí bán hàng"]
    admin_expense = report["data"]["Chi phí"]["Chi phí quản lý doanh nghiệp"]
    net_op = report["data"]["Lợi nhuận thuần từ HĐKD"]["Lợi nhuận thuần từ hoạt động kinh doanh"]

    expected_net_op = gross_profit - sales_expense - admin_expense
    assert net_op == expected_net_op


@pytest.mark.performance
def test_report_generation_performance(ledger_with_revenue_and_expense):
    """
    Test that report generation is fast enough
    """
    import time
    
    config_path = Path(__file__).parent.parent / "gl_core" / "config" / "reports" / "b02_dnn.yaml"
    
    # Load config một lần
    import yaml
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Mock hàm load config để tránh đọc file nhiều lần
    from unittest.mock import patch
    with patch('gl_core.services.reporting.yaml.safe_load', return_value=config):
        start_time = time.time()
        for _ in range(100):  # Generate report 100 times
            generate_income_statement(ledger_with_revenue_and_expense, str(config_path), period="2025-Q1")
        end_time = time.time()
    
    duration = end_time - start_time
    assert duration < 1.0  # Should complete in under 1 second for 100 reports