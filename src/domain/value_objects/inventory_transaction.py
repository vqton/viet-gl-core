from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class InventoryTransaction:
    item_sku: str
    quantity: Decimal
    unit_cost: Decimal
    transaction_date: date
    type: str  # "IN" or "OUT"
