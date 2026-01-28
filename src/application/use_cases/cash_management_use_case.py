"""
Module: Cash Management Use Case

Quản lý giao dịch tiền mặt và tiền gửi theo Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Điều 10 TT 99: Mọi giao dịch tiền phải có chứng từ hợp lệ
- Phải phân biệt rõ tiền mặt (111) và tiền gửi (112)
- Phải lưu trữ đầy đủ audit trail

Trách nhiệm:
- Ghi nhận thu/chi tiền mặt, tiền gửi
- Sinh bút toán đúng tài khoản
- Liên kết với chứng từ gốc
"""

from datetime import datetime
from decimal import Decimal
from src.domain.entities.journal_entry import JournalEntry
from src.application.interfaces.i_journal_entry_repository import IJournalEntryRepository
from src.application.dtos.cash_transaction_dto import CashTransactionDTO, CashTransactionType

class CashManagementUseCase:
    """
    Use case quản lý giao dịch tiền.
    
    Attributes:
        journal_entry_repo (IJournalEntryRepository): Lưu bút toán
    """
    
    def __init__(self, journal_entry_repo: IJournalEntryRepository):
        self.journal_entry_repo = journal_entry_repo

    def execute(self, dto: CashTransactionDTO, created_by: str) -> JournalEntry:
        """
        Thực thi giao dịch tiền.
        
        Args:
            dto (CashTransactionDTO): Dữ liệu giao dịch
            created_by (str): ID người lập bút toán
            
        Returns:
            JournalEntry: Bút toán đã tạo
            
        Raises:
            ValueError: Nếu loại giao dịch không hợp lệ
        """
        if dto.amount <= 0:
            raise ValueError("Số tiền phải lớn hơn 0")
            
        # Xác định tài khoản và kết cấu Nợ/Có
        account, debit, credit = self._get_account_and_amounts(dto.transaction_type, dto.amount)
        
        # Tạo bút toán
        entry = JournalEntry(
            account=account,
            debit=debit,
            credit=credit,
            description=dto.description,
            source_document_id=dto.transaction_number,
            accounting_date=dto.transaction_date,
            accounting_period_code=self._get_period_code(dto.transaction_date),
            created_by=created_by,
            created_at=datetime.now(),
            approved_by="KT_TRUONG",
            approved_at=datetime.now(),
            status="approved",
            original_entry_id=dto.related_document_id,
            is_reversal=False,
            adjustment_reason=""
        )
        
        # Lưu bút toán
        self.journal_entry_repo.save(entry)
        return entry

    def _get_account_and_amounts(self, transaction_type: CashTransactionType, amount: Decimal):
        """
        Xác định tài khoản và kết cấu Nợ/Có cho từng loại giao dịch.
        
        Returns:
            tuple: (account, debit, credit)
        """
        if transaction_type == CashTransactionType.CASH_IN:
            # Thu tiền mặt → Nợ 111
            return "111", amount, Decimal('0')
        elif transaction_type == CashTransactionType.CASH_OUT:
            # Chi tiền mặt → Có 111
            return "111", Decimal('0'), amount
        elif transaction_type == CashTransactionType.BANK_IN:
            # Thu tiền gửi → Nợ 112
            return "112", amount, Decimal('0')
        elif transaction_type == CashTransactionType.BANK_OUT:
            # Chi tiền gửi → Có 112
            return "112", Decimal('0'), amount
        else:
            raise ValueError(f"Loại giao dịch không hợp lệ: {transaction_type}")

    def _get_period_code(self, date) -> str:
        """Chuyển đổi ngày thành mã kỳ kế toán."""
        year = date.year
        quarter = (date.month - 1) // 3 + 1
        return f"{year}-Q{quarter}"