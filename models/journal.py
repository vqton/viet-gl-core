# gl_core/models/journal.py
from decimal import Decimal
from typing import List

class JournalLine:
    def __init__(self, account_code: str, debit: Decimal = Decimal(0), credit: Decimal = Decimal(0)):
        if debit > 0 and credit > 0:
            raise ValueError("A journal line cannot have both debit and credit")
        if debit < 0 or credit < 0:
            raise ValueError("Amounts must be non-negative")
        self.account_code = account_code
        self.debit = debit
        self.credit = credit

class JournalEntry:
    def __init__(self, date: str, lines: List[JournalLine], description: str = ""):
        if not lines:
            raise ValueError("Journal entry must have at least one line")
        self.date = date
        self.lines = lines
        self.description = description