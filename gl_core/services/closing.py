# gl_core/services/closing.py
from decimal import Decimal
from typing import Dict

from gl_core.models import Ledger, JournalEntry, JournalLine
from gl_core.models.account import AccountType


def close_year(ledger: Ledger, year: int) -> JournalEntry:
    """
    Kết chuyển cuối năm: doanh thu, chi phí → tài khoản 421.
    """
    balances = ledger.get_trial_balance()
    closing_lines = []

    # Tính tổng doanh thu và chi phí
    total_revenue = Decimal(0)
    revenue_accounts = []

    total_expense = Decimal(0)
    expense_accounts = []

    for acc_code, balance in balances.items():
        acc = ledger.chart.get(acc_code)
        if acc.account_type == AccountType.REVENUE:
            net_amount = balance["credit"] - balance["debit"]
            if net_amount > 0:
                total_revenue += net_amount
                revenue_accounts.append((acc_code, net_amount))

        elif acc.account_type == AccountType.EXPENSE:
            net_amount = balance["debit"] - balance["credit"]
            if net_amount > 0:
                total_expense += net_amount
                expense_accounts.append((acc_code, net_amount))

    # Kết chuyển doanh thu: Nợ tài khoản doanh thu, Có 421
    for acc_code, amount in revenue_accounts:
        closing_lines.append(JournalLine(acc_code, debit=amount))

    # Kết chuyển chi phí: Có tài khoản chi phí, Nợ 421
    for acc_code, amount in expense_accounts:
        closing_lines.append(JournalLine(acc_code, credit=amount))

    # Tính lợi nhuận sau thuế
    profit = total_revenue - total_expense

    if profit > 0:
        # Lợi nhuận: Có 421
        closing_lines.append(JournalLine("421", credit=profit))
    elif profit < 0:
        # Lỗ: Nợ 421
        closing_lines.append(JournalLine("421", debit=abs(profit)))

    if not closing_lines:
        raise ValueError(f"No revenue or expense accounts to close for year {year}")

    print("DEBUG: Closing lines:", [(line.account_code, line.debit, line.credit) for line in closing_lines])

    # Tạo bút toán kết chuyển
    closing_entry = JournalEntry(
        date=f"{year}-12-31",
        lines=closing_lines,
        description=f"Kết chuyển cuối năm {year}"
    )

    # Ghi vào ledger
    ledger.post(closing_entry)

    return closing_entry