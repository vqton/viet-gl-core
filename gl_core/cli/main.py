# gl_core/cli/main.py
import argparse
import json
from pathlib import Path
from decimal import Decimal

from gl_core.models import AccountChart, Ledger, JournalEntry, JournalLine
from gl_core.services import generate_balance_sheet, generate_income_statement


def load_ledger_with_coa():
    coa_path = Path(__file__).parent.parent / "config" / "tt133_coa.yaml"
    coa = AccountChart.from_yaml(str(coa_path))
    return Ledger(coa)


def post_journal(args):
    ledger = load_ledger_with_coa()

    # Load journal từ file
    with open(args.file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Parse journal
    lines = [
        JournalLine(
            account_code=line["account_code"],
            debit=Decimal(str(line.get("debit", 0))),
            credit=Decimal(str(line.get("credit", 0)))
        )
        for line in data["lines"]
    ]
    entry = JournalEntry(date=data["date"], lines=lines, description=data.get("description", ""))

    # Ghi vào ledger
    ledger.post(entry)
    print(f"✅ Ghi sổ thành công: {entry.date}")


def generate_report(args):
    ledger = load_ledger_with_coa()

    # Ghi một số dữ liệu mẫu để test
    from gl_core.models import JournalEntry, JournalLine
    from decimal import Decimal

    # Ghi sổ mẫu
    entry1 = JournalEntry(
        date="2025-04-01",
        lines=[
            JournalLine("1111", debit=Decimal("10000000")),
            JournalLine("5111", credit=Decimal("10000000")),
        ]
    )
    entry2 = JournalEntry(
        date="2025-04-02",
        lines=[
            JournalLine("632", debit=Decimal("3000000")),
            JournalLine("156", credit=Decimal("3000000")),
        ]
    )
    ledger.post(entry1)
    ledger.post(entry2)

    if args.type == "B01-DNN":
        config_path = Path(__file__).parent.parent / "config" / "reports" / "b01_dnn.yaml"
        report = generate_balance_sheet(ledger, str(config_path), period=args.period)
    elif args.type == "B02-DNN":
        config_path = Path(__file__).parent.parent / "config" / "reports" / "b02_dnn.yaml"
        report = generate_income_statement(ledger, str(config_path), period=args.period)
    else:
        print("❌ Loại báo cáo không hỗ trợ")
        return

    print(json.dumps(report, ensure_ascii=False, indent=2))


def close_year(args):
    print(f"🔄 Đang kết chuyển năm {args.year}...")
    # Sẽ hoàn thiện sau
    print("✅ Kết chuyển hoàn tất (chưa thực hiện logic)")


def main():
    parser = argparse.ArgumentParser(description="CLI tool cho GL engine Việt Nam")
    subparsers = parser.add_subparsers(dest="command", help="Các lệnh hỗ trợ")

    # Lệnh ghi sổ
    post_parser = subparsers.add_parser("post", help="Ghi bút toán")
    post_parser.add_argument("--file", required=True, help="Đường dẫn file JSON chứa journal")

    # Lệnh sinh báo cáo
    report_parser = subparsers.add_parser("report", help="Sinh báo cáo tài chính")
    report_parser.add_argument("--type", required=True, choices=["B01-DNN", "B02-DNN"], help="Loại báo cáo")
    report_parser.add_argument("--period", required=True, help="Kỳ báo cáo (ví dụ: 2025-Q1)")

    # Lệnh kết chuyển cuối năm
    close_parser = subparsers.add_parser("close-year", help="Kết chuyển cuối năm")
    close_parser.add_argument("--year", required=True, help="Năm cần kết chuyển")

    args = parser.parse_args()

    if args.command == "post":
        post_journal(args)
    elif args.command == "report":
        generate_report(args)
    elif args.command == "close-year":
        close_year(args)
    else:
        parser.print_help()