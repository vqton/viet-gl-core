# gl_core/models/ledger.py
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from .account import AccountChart
from .journal import JournalEntry
from ..rules import validate_journal_entry
from .period import AccountingPeriod


class Ledger:
    """
    General Ledger - nơi ghi nhận tất cả các giao dịch kế toán.
    Không phụ thuộc vào DB - toàn bộ dữ liệu nằm trong memory.
    """
    def __init__(self, chart_of_accounts: AccountChart, periods: Dict[str, AccountingPeriod] = None):
        self.chart = chart_of_accounts
        # { account_code: { "debit": Decimal, "credit": Decimal } }
        self.balances: Dict[str, Dict[str, Decimal]] = defaultdict(
            lambda: {"debit": Decimal(0), "credit": Decimal(0)}
        )
        self.entries: List[JournalEntry] = []  # để audit sau này

        # PSE ADDS: Support for Accounting Periods
        self.periods = periods or {}  # { "2025-Q1": AccountingPeriod(...) }

    def post(self, entry: JournalEntry):
        """
        Ghi nhận một bút toán vào sổ cái.
        """
        # 1. Validate trước khi ghi (cân đối, tài khoản tồn tại...)
        validate_journal_entry(entry, self.chart.accounts)

        # 2. PSE ADDS: Check if the entry date is in a locked period
        entry_date = datetime.strptime(entry.date, "%Y-%m-%d").date()
        period_key = self._get_period_key(entry_date) # Ví dụ: "2025-Q1"
        if period_key in self.periods:
            period = self.periods[period_key]
            if period.is_locked:
                raise ValueError(
                    f"Cannot post to a locked period: {period_key}. "
                    f"Locked by {period.locked_by} on {period.locked_at}."
                )

        # 3. Cập nhật số dư
        for line in entry.lines:
            old_bal = self.balances[line.account_code].copy()
            print(f"DEBUG LEDGER: Before update - {line.account_code}: D={old_bal['debit']}, C={old_bal['credit']}")
            self.balances[line.account_code]["debit"] += line.debit
            self.balances[line.account_code]["credit"] += line.credit
            new_bal = self.balances[line.account_code].copy()
            print(f"DEBUG LEDGER: After update - {line.account_code}: D={new_bal['debit']}, C={new_bal['credit']}")

        # 4. Lưu lại entry
        self.entries.append(entry)

    def get_balance(self, account_code: str) -> Dict[str, Decimal]:
        """
        Lấy số dư hiện tại của tài khoản (Nợ/Có riêng biệt).
        """
        if account_code not in self.balances:
            return {"debit": Decimal(0), "credit": Decimal(0)}
        return self.balances[account_code].copy()

    def get_net_balance(self, account_code: str) -> Decimal:
        """
        Lấy số dư ròng (Nợ - Có hoặc Có - Nợ tùy loại tài khoản).
        """
        balance = self.get_balance(account_code)
        acc = self.chart.get(account_code)
        if acc.normal_balance == "debit":
            # Tài sản, chi phí: số dư ròng = Nợ - Có
            return balance["debit"] - balance["credit"]
        else:
            # Nguồn vốn, doanh thu: số dư ròng = Có - Nợ
            return balance["credit"] - balance["debit"]

    def get_trial_balance(self) -> Dict[str, Dict[str, Decimal]]:
        """
        Trả về toàn bộ số dư tài khoản hiện tại.
        """
        return {acc: self.get_balance(acc) for acc in self.balances}

    # PSE ADDS: Helper to determine period key from date
    def _get_period_key(self, entry_date) -> str:
        # Ví dụ đơn giản: "YYYY-QX"
        year = entry_date.year
        quarter = (entry_date.month - 1) // 3 + 1
        return f"{year}-Q{quarter}"