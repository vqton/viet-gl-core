"""
Module: Record Purchase Use Case

Ghi nhận nghiệp vụ mua hàng theo Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Điều 19 TT 99: Ghi nhận hàng hóa tại thời điểm nhận hàng
- Hướng dẫn TK 156: Chi phí thu mua (vận chuyển) ghi vào TK 1562
- Điều 10, 27 TT 99: Bút toán phải có audit trail đầy đủ

Trách nhiệm:
- Chuyển đổi DTO → Domain Entity
- Áp dụng rule hạch toán mua hàng
- Lưu bút toán vào hệ thống
"""

from datetime import datetime
from typing import List
from src.domain.value_objects.purchase_invoice import PurchaseInvoice
from src.domain.entities.journal_entry import JournalEntry
from src.domain.rules.purchase_accounting_rule import apply_purchase_rule
from src.application.interfaces.i_journal_entry_repository import (
    IJournalEntryRepository,
)
from src.application.dtos.purchase_invoice_dto import PurchaseInvoiceDTO


class RecordPurchaseUseCase:
    """
    Use case ghi nhận mua hàng.

    Attributes:
        journal_entry_repo (IJournalEntryRepository): Lưu bút toán
    """

    def __init__(self, journal_entry_repo: IJournalEntryRepository):
        self.journal_entry_repo = journal_entry_repo

    def execute(self, dto: PurchaseInvoiceDTO, created_by: str) -> List[JournalEntry]:
        """
        Thực thi ghi nhận mua hàng.

        Args:
            dto (PurchaseInvoiceDTO): Dữ liệu hóa đơn từ UI/API
            created_by (str): ID người lập bút toán

        Returns:
            List[JournalEntry]: Danh sách bút toán đã tạo

        Raises:
            ValueError: Nếu hóa đơn không hợp lệ
        """
        # 1. Chuyển DTO → Domain Entity
        invoice = PurchaseInvoice(
            invoice_number=dto.invoice_number,
            invoice_date=dto.invoice_date,
            supplier_tax_code=dto.supplier_tax_code,
            supplier_name=dto.supplier_name,
            line_items=dto.line_items,
            freight_cost=dto.freight_cost,
            vat_rate=dto.vat_rate,
        )

        # 2. Áp dụng rule hạch toán từ core logic
        entries = apply_purchase_rule(
            invoice=invoice,
            document_id=invoice.invoice_number,
            accounting_date=invoice.invoice_date,
            accounting_period_code=self._get_period_code(invoice.invoice_date),
            created_by=created_by,
            created_at=datetime.now(),
            approved_by="KT_TRUONG",
            approved_at=datetime.now(),
        )

        # 3. Lưu bút toán vào hệ thống
        for entry in entries:
            self.journal_entry_repo.save(entry)

        return entries

    def _get_period_code(self, date) -> str:
        """Chuyển đổi ngày thành mã kỳ kế toán (ví dụ: 2026-Q2)."""
        year = date.year
        quarter = (date.month - 1) // 3 + 1
        return f"{year}-Q{quarter}"
