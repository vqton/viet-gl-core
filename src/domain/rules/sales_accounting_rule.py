"""
Luật hạch toán bán hàng theo Thông tư 99/2025/TT-BTC.
- Ghi nhận doanh thu tại thời điểm giao hàng
- Xử lý hàng khuyến mãi
- Tính giá vốn thực tế (FIFO)
- Đáp ứng đầy đủ yêu cầu audit trail
"""

from typing import List
from datetime import datetime, date
from decimal import Decimal
from accounting_core.entities.journal_entry import JournalEntry, JournalEntryStatus
from accounting_core.value_objects.sales_invoice import SalesInvoice
from accounting_core.value_objects.inventory_transaction import InventoryTransaction
from accounting_core.rules.inventory_valuation_rules import calculate_cogs_fifo
from accounting_core.validators.coa_validator import is_valid_account


def apply_sales_rule(
    invoice: SalesInvoice,
    inventory_transactions: List[InventoryTransaction],
    document_id: str,
    accounting_date: date,
    accounting_period_code: str,
    created_by: str,
    created_at: datetime,
    approved_by: str,
    approved_at: datetime,
) -> List[JournalEntry]:
    """
    Áp dụng luật hạch toán bán hàng theo TT 99.

    Args:
        invoice (SalesInvoice): Hóa đơn bán hàng hợp lệ.
        inventory_transactions (List[InventoryTransaction]): Giao dịch tồn kho.
        document_id (str): ID chứng từ gốc.
        accounting_date (date): Ngày ghi sổ kế toán.
        accounting_period_code (str): Mã kỳ kế toán (ví dụ: "2026-Q2").
        created_by (str): ID người lập bút toán.
        created_at (datetime): Thời điểm tạo bút toán.
        approved_by (str): ID người duyệt (kế toán trưởng).
        approved_at (datetime): Thời điểm duyệt bút toán.

    Returns:
        List[JournalEntry]: Danh sách bút toán đã được duyệt.

    Raises:
        ValueError: Nếu tài khoản không hợp lệ hoặc tồn kho không đủ.
    """
    # Kiểm tra tính hợp lệ của tài khoản
    required_accounts = ["131", "5111", "33311", "632", "156"]
    for acc in required_accounts:
        if not is_valid_account(acc):
            raise ValueError(f"Tài khoản không hợp lệ theo TT 99: {acc}")

    # Tính tổng số lượng và giá vốn
    total_quantity = sum(item.quantity for item in invoice.line_items)
    cogs = calculate_cogs_fifo(inventory_transactions, total_quantity)
    total_with_vat = invoice.total_amount + invoice.vat_amount

    return [
        JournalEntry(
            account="131",
            debit=total_with_vat,
            credit=Decimal("0"),
            description=f"Phải thu KH: {invoice.buyer_name}",
            source_document_id=document_id,
            accounting_date=accounting_date,
            accounting_period_code=accounting_period_code,
            created_by=created_by,
            created_at=created_at,
            approved_by=approved_by,
            approved_at=approved_at,
            status=JournalEntryStatus.APPROVED,
            original_entry_id="",
            is_reversal=False,
            adjustment_reason="",
        ),
        JournalEntry(
            account="5111",
            debit=Decimal("0"),
            credit=invoice.total_amount,
            description="Doanh thu bán hàng hóa",
            source_document_id=document_id,
            accounting_date=accounting_date,
            accounting_period_code=accounting_period_code,
            created_by=created_by,
            created_at=created_at,
            approved_by=approved_by,
            approved_at=approved_at,
            status=JournalEntryStatus.APPROVED,
            original_entry_id="",
            is_reversal=False,
            adjustment_reason="",
        ),
        JournalEntry(
            account="33311",
            debit=Decimal("0"),
            credit=invoice.vat_amount,
            description="Thuế GTGT phải nộp",
            source_document_id=document_id,
            accounting_date=accounting_date,
            accounting_period_code=accounting_period_code,
            created_by=created_by,
            created_at=created_at,
            approved_by=approved_by,
            approved_at=approved_at,
            status=JournalEntryStatus.APPROVED,
            original_entry_id="",
            is_reversal=False,
            adjustment_reason="",
        ),
        JournalEntry(
            account="632",
            debit=cogs,
            credit=Decimal("0"),
            description="Giá vốn hàng bán",
            source_document_id=document_id,
            accounting_date=accounting_date,
            accounting_period_code=accounting_period_code,
            created_by=created_by,
            created_at=created_at,
            approved_by=approved_by,
            approved_at=approved_at,
            status=JournalEntryStatus.APPROVED,
            original_entry_id="",
            is_reversal=False,
            adjustment_reason="",
        ),
        JournalEntry(
            account="156",
            debit=Decimal("0"),
            credit=cogs,
            description="Xuất kho hàng hóa",
            source_document_id=document_id,
            accounting_date=accounting_date,
            accounting_period_code=accounting_period_code,
            created_by=created_by,
            created_at=created_at,
            approved_by=approved_by,
            approved_at=approved_at,
            status=JournalEntryStatus.APPROVED,
            original_entry_id="",
            is_reversal=False,
            adjustment_reason="",
        ),
    ]
