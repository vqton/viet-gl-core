"""DTO cho hóa đơn bán hàng."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import List
from src.domain.value_objects.sales_invoice import SalesLineItem


@dataclass
class SalesInvoiceDTO:
    invoice_number: str
    invoice_date: date
    seller_tax_code: str
    buyer_name: str
    buyer_tax_code: str
    line_items: List[SalesLineItem]
    vat_rate: Decimal = Decimal("0.1")
