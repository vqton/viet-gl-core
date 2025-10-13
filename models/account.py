# gl_core/models/account.py
from enum import Enum
from typing import Dict, List

class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"

class Account:
    def __init__(
        self,
        code: str,
        name: str,
        account_type: AccountType,
        normal_balance: str  # "debit" or "credit"
    ):
        self.code = code
        self.name = name
        self.account_type = account_type
        self.normal_balance = normal_balance

class AccountChart:
    def __init__(self, accounts: Dict[str, Account]):
        self.accounts = accounts  # { "1111": Account(...), ... }

    @classmethod
    def from_yaml(cls, path: str) -> "AccountChart":
        # Sẽ implement sau — giờ chỉ cần stub
        raise NotImplementedError("from_yaml not implemented yet")