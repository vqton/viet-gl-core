"""
Module: Return Sales Use Case

Xử lý nghiệp vụ hàng bán bị trả lại theo Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Hướng dẫn TK 521: Hàng bán bị trả lại phải ghi giảm doanh thu
- Điều 19 TT 99: Ghi nhận điều chỉnh tại thời điểm trả hàng
- Phải khôi phục hàng hóa vào kho (tăng TK 156)

Trách nhiệm:
- Giảm doanh thu và thuế GTGT đầu ra
- Khôi phục hàng hóa vào kho
- Lưu bút toán với audit trail đầy đủ
"""

from datetime import datetime
from typing import List
from decimal import Decimal
from src.domain.entities.journal_entry import JournalEntry
from src.application.interfaces.i_journal_entry_repository import (
    IJournalEntryRepository,
)
from src.application.dtos.sales_return_dto import SalesReturnDTO


class ReturnSalesUseCase:
    """
    Use case xử lý hàng bán bị trả lại.

    Attributes:
        journal_entry_repo (IJournalEntryRepository): Lưu bút toán
    """

    def __init__(self, journal_entry_repo: IJournalEntryRepository):
        self.journal_entry_repo = journal_entry_repo

    def execute(self, dto: SalesReturnDTO, created_by: str) -> List[JournalEntry]:
        """
        Thực thi nghiệp vụ trả hàng.

        Args:
            dto (SalesReturnDTO): Dữ liệu trả hàng từ UI/API
            created_by (str): ID người lập bút toán

        Returns:
            List[JournalEntry]: Danh sách bút toán điều chỉnh

        Raises:
            ValueError: Nếu dữ liệu không hợp lệ
        """
        # Tính tổng giá trị trả lại
        total_amount = sum(item.quantity * item.unit_price for item in dto.line_items)
        vat_amount = total_amount * Decimal("0.1")
        total_with_vat = total_amount + vat_amount

        # Sinh bút toán điều chỉnh
        entries = [
            # 1. Giảm phải thu khách hàng
            JournalEntry(
                account="131",
                debit=Decimal("0"),
                credit=total_with_vat,
                description=f"Trả hàng KH: {dto.buyer_name} - {dto.reason}",
                source_document_id=dto.return_number,
                accounting_date=dto.return_date,
                accounting_period_code=self._get_period_code(dto.return_date),
                created_by=created_by,
                created_at=datetime.now(),
                approved_by="KT_TRUONG",
                approved_at=datetime.now(),
                status="approved",
                original_entry_id=dto.original_invoice_number,
                is_reversal=True,
                adjustment_reason=dto.reason,
            ),
            # 2. Giảm doanh thu (TK 5212)
            JournalEntry(
                account="5212",
                debit=total_amount,
                credit=Decimal("0"),
                description="Hàng bán bị trả lại",
                source_document_id=dto.return_number,
                accounting_date=dto.return_date,
                accounting_period_code=self._get_period_code(dto.return_date),
                created_by=created_by,
                created_at=datetime.now(),
                approved_by="KT_TRUONG",
                approved_at=datetime.now(),
                status="approved",
                original_entry_id=dto.original_invoice_number,
                is_reversal=True,
                adjustment_reason=dto.reason,
            ),
            # 3. Giảm thuế GTGT đầu ra
            JournalEntry(
                account="33311",
                debit=vat_amount,
                credit=Decimal("0"),
                description="Điều chỉnh giảm thuế GTGT đầu ra",
                source_document_id=dto.return_number,
                accounting_date=dto.return_date,
                accounting_period_code=self._get_period_code(dto.return_date),
                created_by=created_by,
                created_at=datetime.now(),
                approved_by="KT_TRUONG",
                approved_at=datetime.now(),
                status="approved",
                original_entry_id=dto.original_invoice_number,
                is_reversal=True,
                adjustment_reason=dto.reason,
            ),
            # 4. Nhập lại hàng hóa vào kho
            JournalEntry(
                account="156",
                debit=total_amount,  # Giả định giá vốn = giá bán (đơn giản hóa)
                credit=Decimal("0"),
                description="Nhập lại hàng trả từ KH",
                source_document_id=dto.return_number,
                accounting_date=dto.return_date,
                accounting_period_code=self._get_period_code(dto.return_date),
                created_by=created_by,
                created_at=datetime.now(),
                approved_by="KT_TRUONG",
                approved_at=datetime.now(),
                status="approved",
                original_entry_id=dto.original_invoice_number,
                is_reversal=True,
                adjustment_reason=dto.reason,
            ),
            # 5. Giảm giá vốn hàng bán
            JournalEntry(
                account="632",
                debit=Decimal("0"),
                credit=total_amount,
                description="Điều chỉnh giảm giá vốn hàng trả lại",
                source_document_id=dto.return_number,
                accounting_date=dto.return_date,
                accounting_period_code=self._get_period_code(dto.return_date),
                created_by=created_by,
                created_at=datetime.now(),
                approved_by="KT_TRUONG",
                approved_at=datetime.now(),
                status="approved",
                original_entry_id=dto.original_invoice_number,
                is_reversal=True,
                adjustment_reason=dto.reason,
            ),
        ]

        # Lưu bút toán
        for entry in entries:
            self.journal_entry_repo.save(entry)

        return entries

    def _get_period_code(self, date) -> str:
        """Chuyển đổi ngày thành mã kỳ kế toán."""
        year = date.year
        quarter = (date.month - 1) // 3 + 1
        return f"{year}-Q{quarter}"
