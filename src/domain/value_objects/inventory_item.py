from dataclasses import dataclass

@dataclass(frozen=True)
class InventoryItem:
    sku: str
    name: str
    unit: str
    warehouse: str