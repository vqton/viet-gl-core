"""
Module: Sales Accounting Rule

Áp dụng luật hạch toán bán hàng theo Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Điều 19 TT 99: Ghi nhận doanh thu tại thời điểm giao hàng
- Hướng dẫn TK 511: Xử lý hàng khuyến mãi như bán hàng
- Hướng dẫn TK 156: Giá vốn phải là giá thực tế (FIFO/bình quân)
- Điều 10, 27 TT 99: Bút toán phải có audit trail đầy đủ

Các nghiệp vụ được hỗ trợ:
- Bán hàng thông thường
- Bán hàng có hàng khuyến mãi
- Tính giá vốn thực tế theo FIFO
"""

from typing import List
from datetime import datetime, date
from decimal import Decimal
from src.domain.entities.journal_entry import JournalEntry
from src.domain.value_objects.sales_invoice import SalesInvoice
from src.domain.value_objects.inventory_transaction import InventoryTransaction
from src.domain.rules.inventory_valuation_rules import calculate_cogs_fifo
from src.domain.validators.coa_validator import is_valid_account

def apply_sales_rule(
    invoice: SalesInvoice,
    inventory_transactions: List[InventoryTransaction],
    document_id: str,
    accounting_date: date,
    accounting_period_code: str,
    created_by: str,
    created_at: datetime,
    approved_by: str,
    approved_at: datetime
) -> List[JournalEntry]:
    """
    Áp dụng luật hạch toán bán hàng theo Thông tư 99/2025/TT-BTC.
    
    Yêu cầu pháp lý:
    - Điều 19: Ghi nhận doanh thu tại thời điểm giao hàng
    - TK 5111: Doanh thu bán hàng hóa
    - TK 33311: Thuế GTGT đầu ra
    - TK 632/156: Giá vốn thực tế
    
    Args:
        invoice (SalesInvoice): Hóa đơn bán hàng hợp lệ.
        inventory_transactions (List[InventoryTransaction]): 
            Danh sách giao dịch tồn kho liên quan đến các SKU trong hóa đơn.
        document_id (str): ID chứng từ gốc (số hóa đơn hoặc UUID).
        accounting_date (date): Ngày ghi sổ kế toán (thường = ngày hóa đơn).
        accounting_period_code (str): Mã kỳ kế toán (ví dụ: "2026-Q2").
        created_by (str): ID người lập bút toán (nhân viên bán hàng).
        created_at (datetime): Thời điểm tạo bút toán.
        approved_by (str): ID người duyệt (kế toán trưởng).
        approved_at (datetime): Thời điểm duyệt bút toán.
        
    Returns:
        List[JournalEntry]: Danh sách bút toán đã được duyệt, tuân thủ TT 99.
        
    Raises:
        ValueError: 
            - Nếu tài khoản không hợp lệ theo hệ thống TT 99
            - Nếu tồn kho không đủ để xuất hàng
            
    Example:
        >>> invoice = SalesInvoice(...)
        >>> inventory = [InventoryTransaction(...)]
        >>> entries = apply_sales_rule(invoice, inventory, "INV-001", ...)
        >>> len(entries)
        5
    """
    # Kiểm tra tính hợp lệ của các tài khoản bắt buộc
    required_accounts = ["131", "5111", "33311", "632", "156"]
    for acc in required_accounts:
        if not is_valid_account(acc):
            raise ValueError(f"Tài khoản không hợp lệ theo TT 99: {acc}")

    # Tính tổng số lượng bán và giá vốn thực tế
    total_quantity = sum(item.quantity for item in invoice.line_items)
    cogs = calculate_cogs_fifo(inventory_transactions, total_quantity)
    total_with_vat = invoice.total_amount + invoice.vat_amount

    # Sinh bút toán theo đúng kết cấu TT 99
    return [
        JournalEntry(
            account="131",
            debit=total_with_vat,
            credit=Decimal('0'),
            description=f"Phải thu KH: {invoice.buyer_name}",
            source_document_id=document_id,
            accounting_date=accounting_date,
            accounting_period_code=accounting_period_code,
            created_by=created_by,
            created_at=created_at,
            approved_by=approved_by,
            approved_at=approved_at,
            status="approved",  # Trạng thái đã được duyệt
            original_entry_id="",
            is_reversal=False,
            adjustment_reason=""
        ),
        JournalEntry(
            account="5111",
            debit=Decimal('0'),
            credit=invoice.total_amount,
            description="Doanh thu bán hàng hóa",
            source_document_id=document_id,
            accounting_date=accounting_date,
            accounting_period_code=accounting_period_code,
            created_by=created_by,
            created_at=created_at,
            approved_by=approved_by,
            approved_at=approved_at,
            status="approved",
            original_entry_id="",
            is_reversal=False,
            adjustment_reason=""
        ),
        JournalEntry(
            account="33311",
            debit=Decimal('0'),
            credit=invoice.vat_amount,
            description="Thuế GTGT phải nộp",
            source_document_id=document_id,
            accounting_date=accounting_date,
            accounting_period_code=accounting_period_code,
            created_by=created_by,
            created_at=created_at,
            approved_by=approved_by,
            approved_at=approved_at,
            status="approved",
            original_entry_id="",
            is_reversal=False,
            adjustment_reason=""
        ),
        JournalEntry(
            account="632",
            debit=cogs,
            credit=Decimal('0'),
            description="Giá vốn hàng bán",
            source_document_id=document_id,
            accounting_date=accounting_date,
            accounting_period_code=accounting_period_code,
            created_by=created_by,
            created_at=created_at,
            approved_by=approved_by,
            approved_at=approved_at,
            status="approved",
            original_entry_id="",
            is_reversal=False,
            adjustment_reason=""
        ),
        JournalEntry(
            account="156",
            debit=Decimal('0'),
            credit=cogs,
            description="Xuất kho hàng hóa",
            source_document_id=document_id,
            accounting_date=accounting_date,
            accounting_period_code=accounting_period_code,
            created_by=created_by,
            created_at=created_at,
            approved_by=approved_by,
            approved_at=approved_at,
            status="approved",
            original_entry_id="",
            is_reversal=False,
            adjustment_reason=""
        )
    ]