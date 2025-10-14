# gl_core/models/ledger.py
import logging
from collections import defaultdict
from decimal import Decimal
from typing import Dict, List

from .account import AccountChart
from .journal import JournalEntry
from ..rules import validate_journal_entry

# Tạo logger cho module này
logger = logging.getLogger(__name__)

class Ledger:
    def __init__(self, chart_of_accounts: AccountChart):
        self.chart = chart_of_accounts
        self.balances: Dict[str, Dict[str, Decimal]] = defaultdict(
            lambda: {"debit": Decimal(0), "credit": Decimal(0)}
        )
        self.entries: List[JournalEntry] = []

    def post(self, entry: JournalEntry):
        logger.info(f"Posting journal entry: {entry.date} - {len(entry.lines)} lines")
        validate_journal_entry(entry, self.chart.accounts)

        for line in entry.lines:
            old_bal = self.balances[line.account_code].copy()
            logger.debug(f"Before update {line.account_code}: D={old_bal['debit']}, C={old_bal['credit']}")
            self.balances[line.account_code]["debit"] += line.debit
            self.balances[line.account_code]["credit"] += line.credit
            new_bal = self.balances[line.account_code].copy()
            logger.debug(f"After update {line.account_code}: D={new_bal['debit']}, C={new_bal['credit']}")

        self.entries.append(entry)
        logger.info(f"Successfully posted entry. Total entries: {len(self.entries)}")

    def get_balance(self, account_code: str) -> Dict[str, Decimal]:
        balance = self.balances[account_code].copy()
        logger.debug(f"Balance requested for {account_code}: D={balance['debit']}, C={balance['credit']}")
        return balance

    def get_net_balance(self, account_code: str) -> Decimal:
        balance = self.get_balance(account_code)
        acc = self.chart.get(account_code)
        if acc.normal_balance == "debit":
            net = balance["debit"] - balance["credit"]
        else:
            net = balance["credit"] - balance["debit"]
        logger.debug(f"Net balance for {account_code}: {net}")
        return net

    def get_trial_balance(self) -> Dict[str, Dict[str, Decimal]]:
        logger.info("Trial balance requested")
        return {acc: self.get_balance(acc) for acc in self.balances}