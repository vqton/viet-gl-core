"""
Module: SalesAccountingRule

Luật hạch toán bán hàng theo Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Ghi nhận doanh thu tại thời điểm giao hàng (Điều 19)
- Xử lý hàng khuyến mãi (Hướng dẫn TK 511)
- Ghi nhận giá vốn thực tế (TK 632)
"""

from typing import List
from datetime import datetime, date
from decimal import Decimal
from domain.entities.journal_entry import JournalEntry
from domain.value_objects.sales_invoice import SalesInvoice
from domain.services.inventory_valuation_service import InventoryValuationService
from domain.services.coa_validator import is_valid_account, is_debit_allowed, is_credit_allowed

def apply_sales_rule(
    invoice: SalesInvoice,
    inventory_transactions: List,
    document_id: str,
    accounting_date: date,
    created_by: str,
    created_at: datetime
) -> List[JournalEntry]:
    """
    Áp dụng luật hạch toán bán hàng theo TT 99.

    Args:
        invoice (SalesInvoice): Hóa đơn bán hàng.
        inventory_transactions (List): Giao dịch tồn kho liên quan.
        document_id (str): ID chứng từ gốc.
        accounting_date (date): Ngày ghi sổ.
        created_by (str): Người lập.
        created_at (datetime): Thời điểm tạo.

    Returns:
        List[JournalEntry]: Danh sách bút toán hợp lệ.

    Note:
        - Tự động tính giá vốn theo FIFO.
        - Kiểm tra tính hợp lệ của tài khoản trước khi tạo bút toán.
    """
    # Tính giá vốn thực tế
    total_quantity = sum(item.quantity for item in invoice.line_items)
    cogs = InventoryValuationService.calculate_cogs_fifo(inventory_transactions, total_quantity)

    # Kiểm tra tài khoản hợp lệ
    if not all(is_valid_account(acc) for acc in ["131", "5111", "33311", "632", "156"]):
        raise ValueError("Phát hiện tài khoản không hợp lệ trong COA")

    entries = []

    total_with_vat = invoice.total_amount + invoice.vat_amount

    # 1. Phải thu
    entries.append(JournalEntry(
        account="131", debit=total_with_vat, credit=Decimal('0'),
        description=f"Phải thu KH: {invoice.buyer_name}",
        source_document_id=document_id,
        accounting_date=accounting_date,
        created_by=created_by,
        created_at=created_at
    ))

    # 2. Doanh thu
    entries.append(JournalEntry(
        account="5111", debit=Decimal('0'), credit=invoice.revenue,
        description="Doanh thu bán hàng hóa",
        source_document_id=document_id,
        accounting_date=accounting_date,
        created_by=created_by,
        created_at=created_at
    ))

    # 3. Thuế GTGT
    entries.append(JournalEntry(
        account="33311", debit=Decimal('0'), credit=invoice.vat_amount,
        description="Thuế GTGT đầu ra",
        source_document_id=document_id,
        accounting_date=accounting_date,
        created_by=created_by,
        created_at=created_at
    ))

    # 4. Giá vốn
    entries.append(JournalEntry(
        account="632", debit=cogs, credit=Decimal('0'),
        description="Giá vốn hàng bán",
        source_document_id=document_id,
        accounting_date=accounting_date,
        created_by=created_by,
        created_at=created_at
    ))

    # 5. Xuất kho
    entries.append(JournalEntry(
        account="156", debit=Decimal('0'), credit=cogs,
        description="Xuất kho hàng hóa",
        source_document_id=document_id,
        accounting_date=accounting_date,
        created_by=created_by,
        created_at=created_at
    ))

    return entries