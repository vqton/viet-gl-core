"""
Module: Return Purchase Use Case

Xử lý nghiệp vụ trả lại hàng mua theo Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Điều chỉnh giảm chi phí mua hàng và thuế GTGT được khấu trừ
- Phải ghi nhận đầy đủ lý do trả hàng
- Có audit trail liên kết với hóa đơn gốc

Trách nhiệm:
- Giảm giá trị hàng hóa và chi phí thu mua
- Giảm thuế GTGT được khấu trừ
- Tăng phải trả người bán (hoặc giảm tiền đã trả)
"""

from datetime import datetime
from typing import List
from decimal import Decimal
from src.domain.entities.journal_entry import JournalEntry
from src.application.interfaces.i_journal_entry_repository import IJournalEntryRepository
from src.application.dtos.purchase_return_dto import PurchaseReturnDTO

class ReturnPurchaseUseCase:
    """
    Use case xử lý trả lại hàng mua.
    
    Attributes:
        journal_entry_repo (IJournalEntryRepository): Lưu bút toán
    """
    
    def __init__(self, journal_entry_repo: IJournalEntryRepository):
        self.journal_entry_repo = journal_entry_repo

    def execute(self, dto: PurchaseReturnDTO, created_by: str) -> List[JournalEntry]:
        """
        Thực thi nghiệp vụ trả hàng mua.
        
        Args:
            dto (PurchaseReturnDTO): Dữ liệu trả hàng từ UI/API
            created_by (str): ID người lập bút toán
            
        Returns:
            List[JournalEntry]: Danh sách bút toán điều chỉnh
        """
        # Tính toán giá trị điều chỉnh
        goods_value = sum(item.quantity * item.unit_price for item in dto.line_items)
        vat_amount = (goods_value + dto.freight_cost) * Decimal('0.1')
        
        entries = []
        
        # 1. Giảm giá trị hàng hóa (1561)
        if goods_value > 0:
            entries.append(
                JournalEntry(
                    account="1561",
                    debit=Decimal('0'),
                    credit=goods_value,
                    description=f"Trả hàng NCC: {dto.supplier_name} - {dto.reason}",
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
                    adjustment_reason=dto.reason
                )
            )
        
        # 2. Giảm chi phí thu mua (1562) - nếu có
        if dto.freight_cost > 0:
            entries.append(
                JournalEntry(
                    account="1562",
                    debit=Decimal('0'),
                    credit=dto.freight_cost,
                    description="Điều chỉnh giảm chi phí vận chuyển",
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
                    adjustment_reason=dto.reason
                )
            )
        
        # 3. Giảm thuế GTGT được khấu trừ (13311)
        if vat_amount > 0:
            entries.append(
                JournalEntry(
                    account="13311",
                    debit=Decimal('0'),
                    credit=vat_amount,
                    description="Điều chỉnh giảm thuế GTGT được khấu trừ",
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
                    adjustment_reason=dto.reason
                )
            )
        
        # 4. Tăng phải trả người bán (331)
        total_with_vat = goods_value + dto.freight_cost + vat_amount
        if total_with_vat > 0:
            entries.append(
                JournalEntry(
                    account="331",
                    debit=total_with_vat,
                    credit=Decimal('0'),
                    description=f"Tăng nợ NCC do trả hàng: {dto.supplier_name}",
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
                    adjustment_reason=dto.reason
                )
            )
        
        # Lưu bút toán
        for entry in entries:
            self.journal_entry_repo.save(entry)
            
        return entries

    def _get_period_code(self, date) -> str:
        """Chuyển đổi ngày thành mã kỳ kế toán."""
        year = date.year
        quarter = (date.month - 1) // 3 + 1
        return f"{year}-Q{quarter}"