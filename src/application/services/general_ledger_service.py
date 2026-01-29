"""
Module: General Ledger Service

Tổng hợp Sổ cái từ bút toán kế toán theo Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Điều 27 TT 99: Sổ cái phải phản ánh đầy đủ các nghiệp vụ kinh tế phát sinh
- Phải đảm bảo cân đối giữa Tài sản và Nguồn vốn
- Số liệu Sổ cái là cơ sở để lập báo cáo tài chính

Trách nhiệm:
- Tính số dư đầu kỳ, phát sinh trong kỳ, số dư cuối kỳ
- Cung cấp dữ liệu cho FinancialReportService
"""

from decimal import Decimal
from typing import Dict, List, NamedTuple
from src.domain.entities.journal_entry import JournalEntry
from src.application.interfaces.i_journal_entry_repository import (
    IJournalEntryRepository,
)


class AccountBalance(NamedTuple):
    """
    Kết quả tổng hợp tài khoản.

    Attributes:
        account (str): Mã tài khoản
        opening_balance (Decimal): Số dư đầu kỳ
        debit_turnover (Decimal): Phát sinh Nợ
        credit_turnover (Decimal): Phát sinh Có
        closing_balance (Decimal): Số dư cuối kỳ (dương = Nợ, âm = Có)
    """

    account: str
    opening_balance: Decimal
    debit_turnover: Decimal
    credit_turnover: Decimal
    closing_balance: Decimal


class GeneralLedgerService:
    """
    Service tổng hợp Sổ cái.

    Attributes:
        journal_entry_repo (IJournalEntryRepository): Truy xuất bút toán
    """

    def __init__(self, journal_entry_repo: IJournalEntryRepository):
        self.journal_entry_repo = journal_entry_repo

    def get_account_balance(self, account: str, period: str) -> AccountBalance:
        """
        Tính số dư tài khoản cho kỳ kế toán.

        Args:
            account (str): Mã tài khoản (ví dụ: "111", "131", "5111")
            period (str): Kỳ kế toán (ví dụ: "2026-Q2")

        Returns:
            AccountBalance: Kết quả tổng hợp
        """
        # Lấy toàn bộ bút toán của tài khoản trong kỳ
        entries = self.journal_entry_repo.find_by_account(account, period)

        # Tính phát sinh
        debit_turnover = sum(entry.debit for entry in entries)
        credit_turnover = sum(entry.credit for entry in entries)

        # Giả định số dư đầu kỳ = 0 (có thể mở rộng sau)
        opening_balance = Decimal("0")

        # Tính số dư cuối kỳ
        # Quy ước: Dư Nợ (+), Dư Có (-)
        if account.startswith(("1", "2")):  # Tài sản, Chi phí
            closing_balance = opening_balance + debit_turnover - credit_turnover
        elif account.startswith(
            ("3", "4", "5", "6", "7", "8", "9")
        ):  # Nguồn vốn, Doanh thu
            closing_balance = opening_balance + credit_turnover - debit_turnover
        else:
            closing_balance = debit_turnover - credit_turnover

        return AccountBalance(
            account=account,
            opening_balance=opening_balance,
            debit_turnover=debit_turnover,
            credit_turnover=credit_turnover,
            closing_balance=closing_balance,
        )

    def get_trial_balance(self, period: str) -> Dict[str, AccountBalance]:
        """
        Lấy bảng cân đối phát sinh cho kỳ kế toán.

        Args:
            period (str): Kỳ kế toán

        Returns:
            Dict[str, AccountBalance]: Tổng hợp tất cả tài khoản
        """
        # Lấy toàn bộ bút toán trong kỳ
        all_entries = self.journal_entry_repo.get_all_entries(period)

        # Lấy danh sách tài khoản duy nhất
        accounts = set(entry.account for entry in all_entries)

        # Tổng hợp từng tài khoản
        trial_balance = {}
        for account in accounts:
            balance = self.get_account_balance(account, period)
            trial_balance[account] = balance

        return trial_balance

    def verify_accounting_equation(self, period: str) -> bool:
        """
        Kiểm tra cân đối kế toán: Tổng Tài sản = Tổng Nguồn vốn.

        Returns:
            bool: True nếu cân đối
        """
        trial_balance = self.get_trial_balance(period)

        total_assets = Decimal("0")  # Nhóm 1, 2
        total_equity = Decimal("0")  # Nhóm 3, 4, 5, 6, 7, 8, 9

        for account, balance in trial_balance.items():
            if account.startswith(("1", "2")):
                total_assets += balance.closing_balance
            else:
                total_equity += balance.closing_balance

        return abs(total_assets - total_equity) < Decimal("0.01")  # Sai số làm tròn
