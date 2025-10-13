# gl_core/models/account.py
import yaml
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Dict, Any

class AccountType(str, Enum):
    ASSET = "asset"
    LIABILITY = "liability"
    EQUITY = "equity"
    REVENUE = "revenue"
    EXPENSE = "expense"
    CONTRA_ASSET = "contra_asset"  # Ví dụ: Hao mòn, Dự phòng
    TEMPORARY = "temporary"        # Ví dụ: Tài khoản kết chuyển 911

class Account:
    __slots__ = ("code", "name", "account_type", "normal_balance")
    
    def __init__(
        self,
        code: str,
        name: str,
        account_type: AccountType,
        normal_balance: str,  # "debit" or "credit"
    ):
        if normal_balance not in ("debit", "credit"):
            raise ValueError(f"normal_balance must be 'debit' or 'credit', got '{normal_balance}'")
        
        self.code = code
        self.name = name
        self.account_type = account_type
        self.normal_balance = normal_balance

    def __repr__(self):
        return f"Account(code='{self.code}', name='{self.name}', type={self.account_type}, balance='{self.normal_balance}')"


class AccountChart:
    __slots__ = ("accounts",)
    
    def __init__(self, accounts: Dict[str, Account]):
        if not accounts:
            raise ValueError("Account chart cannot be empty")
        self.accounts = accounts

    @classmethod
    def from_yaml(cls, path: str) -> "AccountChart":
        """
        Load Chart of Accounts from a YAML file.
        
        Expected YAML format:
          <account_code>:
            name: "Account Name"
            type: "asset|liability|equity|revenue|expense|contra_asset|temporary"
            normal_balance: "debit|credit"
        
        Args:
            path (str): Path to YAML file
            
        Returns:
            AccountChart: Loaded chart of accounts
            
        Raises:
            FileNotFoundError: If file does not exist
            ValueError: If YAML format is invalid
            yaml.YAMLError: If YAML syntax is broken
        """
        yaml_path = Path(path)
        if not yaml_path.exists():
            raise FileNotFoundError(f"COA file not found: {path}")
        
        try:
            with open(yaml_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML syntax in {path}: {e}")

        if not isinstance(data, dict):
            raise ValueError(f"COA file must contain a mapping at root, got {type(data)}")

        accounts = {}
        for code, attrs in data.items():
            # Ensure code is string (YAML số 111 → int, but we want "111")
            str_code = str(code)
            
            if not isinstance(attrs, dict):
                raise ValueError(f"Account '{str_code}' must be a mapping, got {type(attrs)}")
            
            # Validate required fields
            for field in ("name", "type", "normal_balance"):
                if field not in attrs:
                    raise ValueError(f"Account '{str_code}' missing required field: '{field}'")
            
            try:
                acc_type = AccountType(attrs["type"])
            except ValueError:
                valid_types = [t.value for t in AccountType]
                raise ValueError(
                    f"Invalid account type '{attrs['type']}' for account '{str_code}'. "
                    f"Valid types: {valid_types}"
                )
            
            account = Account(
                code=str_code,
                name=str(attrs["name"]),
                account_type=acc_type,
                normal_balance=str(attrs["normal_balance"]).lower()
            )
            accounts[str_code] = account

        return cls(accounts)

    def get(self, code: str) -> Account:
        """Get account by code. Raise KeyError if not found."""
        return self.accounts[code]

    def __contains__(self, code: str) -> bool:
        return code in self.accounts

    def __repr__(self):
        return f"AccountChart(accounts={list(self.accounts.keys())})"