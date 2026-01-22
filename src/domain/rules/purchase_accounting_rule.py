"""
Luật hạch toán mua hàng theo Thông tư 99/2025/TT-BTC.
- Ghi nhận hàng hóa tại thời điểm nhận hàng
- Tách biệt thuế GTGT được khấu trừ
- Hạch toán chi phí thu mua vào TK 1562
- Đáp ứng đầy đủ yêu cầu audit trail
"""

from typing import List
from datetime import datetime, date
from decimal import Decimal
from src.domain.entities.journal_entry import JournalEntry, JournalEntryStatus
from src.domain.value_objects.purchase_invoice import PurchaseInvoice
from src.domain.services.coa_validator import is_valid_account


def apply_purchase_rule(
    invoice: PurchaseInvoice,
    document_id: str,
    accounting_date: date,
    accounting_period_code: str,
    created_by: str,
    created_at: datetime,
    approved_by: str,
    approved_at: datetime,
) -> List[JournalEntry]:
    """
    Áp dụng luật hạch toán mua hàng theo TT 99.

    Args:
        invoice (PurchaseInvoice): Hóa đơn mua hàng hợp lệ.
        document_id (str): ID chứng từ gốc.
        accounting_date (date): Ngày ghi sổ kế toán.
        accounting_period_code (str): Mã kỳ kế toán.
        created_by (str): ID người lập bút toán.
        created_at (datetime): Thời điểm tạo bút toán.
        approved_by (str): ID người duyệt (kế toán trưởng).
        approved_at (datetime): Thời điểm duyệt bút toán.

    Returns:
        List[JournalEntry]: Danh sách bút toán đã được duyệt.

    Raises:
        ValueError: Nếu tài khoản không hợp lệ.
    """
    # Kiểm tra tính hợp lệ của tài khoản
    required_accounts = ["1561", "1562", "13311", "331"]
    for acc in required_accounts:
        if not is_valid_account(acc):
            raise ValueError(f"Tài khoản không hợp lệ theo TT 99: {acc}")

    entries = []

    # 1. Hàng hóa mua vào
    entries.append(
        JournalEntry(
            account="1561",
            debit=invoice.goods_value,
            credit=Decimal("0"),
            description=f"Hàng hóa mua vào từ NCC: {invoice.supplier_name}",
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
        )
    )

    # 2. Chi phí vận chuyển (nếu có)
    if invoice.freight_cost > 0:
        entries.append(
            JournalEntry(
                account="1562",
                debit=invoice.freight_cost,
                credit=Decimal("0"),
                description="Chi phí vận chuyển hàng mua",
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
            )
        )

    # 3. Thuế GTGT được khấu trừ
    entries.append(
        JournalEntry(
            account="13311",
            debit=invoice.vat_amount,
            credit=Decimal("0"),
            description="Thuế GTGT được khấu trừ",
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
        )
    )

    # 4. Phải trả người bán
    total_payable = invoice.goods_value + invoice.freight_cost + invoice.vat_amount
    entries.append(
        JournalEntry(
            account="331",
            debit=Decimal("0"),
            credit=total_payable,
            description=f"Phải trả NCC: {invoice.supplier_name}",
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
        )
    )

    return entries
