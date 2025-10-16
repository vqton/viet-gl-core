# gl_core/cli/main.py
import argparse
import json
import logging
from pathlib import Path
from decimal import Decimal

from gl_core.models import AccountChart, Ledger, JournalEntry, JournalLine
from gl_core.services import generate_balance_sheet, generate_income_statement, close_year


def setup_logging(level: str):
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def decimal_serializer(obj):
    """
    Serializer to convert Decimal to string for JSON output.
    """
    if isinstance(obj, Decimal):
        return str(obj)  # Use str to preserve precision
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def load_ledger_with_coa():
    """
    Load the ledger with the Chart of Accounts (COA).
    """
    coa_path = Path(__file__).parent.parent / "config" / "tt133_coa.yaml"
    coa = AccountChart.from_yaml(str(coa_path))
    return Ledger(coa)


def post_journal(args):
    ledger = load_ledger_with_coa()

    with open(args.file, "r", encoding="utf-8") as f:
        data = json.load(f)

    lines = [
        JournalLine(
            account_code=line["account_code"],
            debit=Decimal(str(line.get("debit", 0))),
            credit=Decimal(str(line.get("credit", 0)))
        )
        for line in data["lines"]
    ]
    entry = JournalEntry(date=data["date"], lines=lines, description=data.get("description", ""))

    ledger.post(entry)
    print(f"✅ Ghi sổ thành công: {entry.date}")


def generate_report(args):
    ledger = load_ledger_with_coa()

    # Loại bỏ dữ liệu mẫu, chỉ sử dụng dữ liệu thực tế từ ledger
    if args.type == "B01-DNN":
        config_path = Path(__file__).parent.parent / "config" / "reports" / "b01_dnn.yaml"
        report = generate_balance_sheet(ledger, str(config_path), period=args.period)
    elif args.type == "B02-DNN":
        config_path = Path(__file__).parent.parent / "config" / "reports" / "b02_dnn.yaml"
        report = generate_income_statement(ledger, str(config_path), period=args.period)
    else:
        print("❌ Loại báo cáo không hỗ trợ")
        return

    # Sử dụng serializer để chuyển Decimal sang string
    print(json.dumps(report, ensure_ascii=False, indent=2, default=decimal_serializer))


def close_year_cli(args):
    ledger = load_ledger_with_coa()

    # Loại bỏ dữ liệu mẫu, chỉ sử dụng dữ liệu thực tế từ ledger
    print(f"🔄 Đang kết chuyển năm {args.year}...")
    closing_entry = close_year(ledger, int(args.year))
    print(f"✅ Kết chuyển hoàn tất. Ghi sổ: {len(closing_entry.lines)} dòng.")


def main():
    parser = argparse.ArgumentParser(description="CLI tool cho GL engine Việt Nam")
    
    # Thêm subparsers
    subparsers = parser.add_subparsers(dest="command", help="Các lệnh hỗ trợ")

    # Lệnh ghi sổ
    post_parser = subparsers.add_parser("post", help="Ghi bút toán")
    post_parser.add_argument("--file", required=True, help="Đường dẫn file JSON chứa journal")
    post_parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Mức log")

    # Lệnh sinh báo cáo
    report_parser = subparsers.add_parser("report", help="Sinh báo cáo tài chính")
    report_parser.add_argument("--type", required=True, choices=["B01-DNN", "B02-DNN"], help="Loại báo cáo")
    report_parser.add_argument("--period", required=True, help="Kỳ báo cáo (ví dụ: 2025-Q1)")
    report_parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Mức log")

    # Lệnh kết chuyển cuối năm
    close_parser = subparsers.add_parser("close-year", help="Kết chuyển cuối năm")
    close_parser.add_argument("--year", required=True, help="Năm cần kết chuyển")
    close_parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"], help="Mức log")

    args = parser.parse_args()

    # Cấu hình logging dựa trên đối số của từng lệnh
    setup_logging(getattr(args, 'log_level', 'INFO'))

    if args.command == "post":
        post_journal(args)
    elif args.command == "report":
        generate_report(args)
    elif args.command == "close-year":
        close_year_cli(args)
    else:
        parser.print_help()