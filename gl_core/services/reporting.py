# gl_core/services/reporting.py
import yaml
from decimal import Decimal
from pathlib import Path
from typing import Dict, Any

from gl_core.models import Ledger


def generate_balance_sheet(
    ledger: Ledger,
    report_config_path: str,
    period: str = "Unknown"
) -> Dict[str, Any]:
    """
    Sinh báo cáo Bảng cân đối kế toán (B01-DNN).
    
    Args:
        ledger: Ledger đã có dữ liệu
        report_config_path: Đường dẫn file YAML cấu hình báo cáo
        period: Kỳ báo cáo (ví dụ: "2025-Q1")
    
    Returns:
        Dict báo cáo theo cấu trúc B01-DNN
    """
    with open(report_config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    balances = ledger.get_trial_balance()
    report = {
        "report_type": config["report"],
        "report_name": config["name"],
        "period": period,
        "data": {}
    }

    for section in config["structure"]:
        section_name = section["group"]
        section_data = {}
        for line in section["lines"]:
            label = line["label"]
            total = Decimal(0)
            for acc_code in line["accounts"]:
                bal = balances.get(acc_code, {"debit": Decimal(0), "credit": Decimal(0)})
                # Tính số dư theo loại tài khoản
                if line["sign"] == "debit":
                    total += bal["debit"] - bal["credit"]
                else:  # credit
                    total += bal["credit"] - bal["debit"]
            # Chỉ hiển thị nếu có số
            if total != Decimal(0):
                section_data[label] = total
        report["data"][section_name] = section_data

    return report


def generate_income_statement(
    ledger: Ledger,
    report_config_path: str,
    period: str = "Unknown"
) -> Dict[str, Any]:
    """
    Sinh báo cáo Kết quả hoạt động kinh doanh (B02-DNN).
    """
    # Tương tự như trên, chỉ thay đổi cấu hình
    with open(report_config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    balances = ledger.get_trial_balance()
    report = {
        "report_type": config["report"],
        "report_name": config["name"],
        "period": period,
        "data": {}
    }

    for section in config["structure"]:
        section_name = section["group"]
        section_data = {}
        for line in section["lines"]:
            label = line["label"]
            total = Decimal(0)
            for acc_code in line["accounts"]:
                bal = balances.get(acc_code, {"debit": Decimal(0), "credit": Decimal(0)})
                # Doanh thu (credit) và chi phí (debit)
                if line["sign"] == "credit":
                    total += bal["credit"] - bal["debit"]
                else:  # debit
                    total += bal["debit"] - bal["credit"]
            if total != Decimal(0):
                section_data[label] = total
        report["data"][section_name] = section_data

    return report