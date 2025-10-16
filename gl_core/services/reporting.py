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
    with open(report_config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    balances = ledger.get_trial_balance()
    report = {
        "report_type": config["report"],
        "report_name": config["name"],
        "period": period,
        "data": {},
        "calculated": {}  # Dùng để lưu kết quả công thức
    }

    # Duyệt cấu trúc báo cáo
    for section in config["structure"]:
        section_name = section["group"]
        section_data = {}
        for line in section["lines"]:
            label = line["label"]
            code = line.get("code", "")
            if "formula" in line:
                # Đây là dòng công thức, chưa tính ngay
                section_data[label] = {"formula": line["formula"]}
            else:
                # Đây là dòng dữ liệu từ tài khoản
                total = Decimal(0)
                for acc_code in line["accounts"]:
                    bal = balances.get(acc_code, {"debit": Decimal(0), "credit": Decimal(0)})
                    if line["sign"] == "credit":
                        # Doanh thu: số dương = Có - Nợ
                        total += bal["credit"] - bal["debit"]
                    else:  # debit
                        # Chi phí: số dương = Nợ - Có
                        total += bal["debit"] - bal["credit"]
                if total != Decimal(0):
                    section_data[label] = total
                    if code:
                        report["calculated"][code] = total
        report["data"][section_name] = section_data

    # Tính lại các dòng có công thức
    for section_name, section_data in report["data"].items():
        for label, value in section_data.items():
            if isinstance(value, dict) and "formula" in value:
                formula = value["formula"]
                # Thay thế mã số bằng giá trị thực tế
                calc_value = _evaluate_formula(formula, report["calculated"])
                # Cập nhật lại vào report
                report["data"][section_name][label] = calc_value
                # Cập nhật vào calculated nếu có mã số
                for line in config["structure"]:
                    for l in line["lines"]:
                        if l.get("label") == label and l.get("code"):
                            report["calculated"][l["code"]] = calc_value

    return report


def _evaluate_formula(formula: str, values: Dict[str, Decimal]) -> Decimal:
    """
    Tính toán công thức từ các mã số (ví dụ: "01 - 02")
    """
    # Thay thế mã số bằng giá trị
    formula_eval = formula
    for code, value in values.items():
        formula_eval = formula_eval.replace(code, str(value))
    # Tính toán
    try:
        return Decimal(str(eval(formula_eval)))
    except:
        return Decimal("0")  # Tránh lỗi nếu công thức sai