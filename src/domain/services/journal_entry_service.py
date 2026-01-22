"""
Module: JournalEntryService

Dịch vụ quản lý vòng đời bút toán kế toán theo Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Điều 10 TT 99: Chứng từ phải có người lập, người duyệt
- Điều 27 TT 99: Mọi thay đổi phải lưu vết
- Nguyên tắc: Không sửa xóa bút toán đã khóa sổ
"""

from datetime import datetime
from typing import List
from domain.entities.journal_entry import JournalEntry, JournalEntryStatus
from domain.services.coa_validator import (
    is_valid_account,
    is_debit_allowed,
    is_credit_allowed,
)


class JournalEntryService:
    """Dịch vụ quản lý bút toán kế toán."""

    @staticmethod
    def create_draft_entry(
        account: str,
        debit: float,
        credit: float,
        description: str,
        source_document_id: str,
        accounting_date: datetime.date,
        accounting_period_code: str,
        created_by: str,
        created_at: datetime = None,
    ) -> JournalEntry:
        """
        Tạo bút toán ở trạng thái NHÁP.

        Args:
            account (str): Mã tài khoản.
            debit (float): Số tiền Nợ.
            credit (float): Số tiền Có.
            description (str): Diễn giải.
            source_document_id (str): ID chứng từ gốc.
            accounting_date (date): Ngày ghi sổ.
            accounting_period_code (str): Mã kỳ kế toán.
            created_by (str): Người lập.
            created_at (datetime): Thời điểm tạo (mặc định hiện tại).

        Returns:
            JournalEntry: Bút toán trạng thái DRAFT.

        Raises:
            ValueError: Nếu tài khoản không hợp lệ hoặc kết cấu Nợ/Có sai.
        """
        from decimal import Decimal

        # Chuẩn hóa số
        debit = Decimal(str(debit))
        credit = Decimal(str(credit))

        # Kiểm tra tính hợp lệ
        if not is_valid_account(account):
            raise ValueError(f"Tài khoản không hợp lệ: {account}")
        if debit > 0 and not is_debit_allowed(account):
            raise ValueError(f"Không được ghi Nợ vào tài khoản: {account}")
        if credit > 0 and not is_credit_allowed(account):
            raise ValueError(f"Không được ghi Có vào tài khoản: {account}")

        if created_at is None:
            created_at = datetime.now()

        return JournalEntry(
            id="",  # ID sẽ được sinh khi lưu
            account=account,
            debit=debit,
            credit=credit,
            description=description,
            source_document_id=source_document_id,
            accounting_date=accounting_date,
            accounting_period_code=accounting_period_code,
            status=JournalEntryStatus.DRAFT,
            created_by=created_by,
            created_at=created_at,
            approved_by="",
            approved_at=None,
            original_entry_id="",
            is_reversal=False,
            adjustment_reason="",
        )

    @staticmethod
    def approve_entry(
        entry: JournalEntry, approver_id: str, approved_at: datetime = None
    ) -> JournalEntry:
        """
        Duyệt bút toán từ trạng thái NHÁP sang ĐÃ DUYỆT.

        Args:
            entry (JournalEntry): Bút toán cần duyệt.
            approver_id (str): ID người duyệt (kế toán trưởng).
            approved_at (datetime): Thời điểm duyệt.

        Returns:
            JournalEntry: Bút toán đã được duyệt.

        Raises:
            ValueError: Nếu bút toán không ở trạng thái DRAFT.
        """
        if entry.status != JournalEntryStatus.DRAFT:
            raise ValueError("Chỉ được duyệt bút toán ở trạng thái NHÁP")

        if approved_at is None:
            approved_at = datetime.now()

        # Tạo bản sao với trạng thái mới (immutable)
        return JournalEntry(
            id=entry.id,
            account=entry.account,
            debit=entry.debit,
            credit=entry.credit,
            description=entry.description,
            source_document_id=entry.source_document_id,
            accounting_date=entry.accounting_date,
            accounting_period_code=entry.accounting_period_code,
            status=JournalEntryStatus.APPROVED,
            created_by=entry.created_by,
            created_at=entry.created_at,
            approved_by=approver_id,
            approved_at=approved_at,
            original_entry_id=entry.original_entry_id,
            is_reversal=entry.is_reversal,
            adjustment_reason=entry.adjustment_reason,
        )

    @staticmethod
    def reverse_entry(
        original_entry: JournalEntry,
        reason: str,
        reverser_id: str,
        reversal_date: datetime.date = None,
        reversal_at: datetime = None,
    ) -> JournalEntry:
        """
        Tạo bút toán HỦY (điều chỉnh) cho bút toán gốc.

        Nguyên tắc:
        - Ghi âm bút toán gốc (Nợ ↔ Có)
        - Liên kết qua original_entry_id
        - Trạng thái: ADJUSTED

        Args:
            original_entry (JournalEntry): Bút toán gốc cần hủy.
            reason (str): Lý do điều chỉnh.
            reverser_id (str): Người thực hiện điều chỉnh.
            reversal_date (date): Ngày ghi sổ điều chỉnh (mặc định = ngày hiện tại).
            reversal_at (datetime): Thời điểm tạo bút toán hủy.

        Returns:
            JournalEntry: Bút toán hủy.

        Raises:
            ValueError: Nếu bút toán gốc đã bị khóa sổ.
        """
        if original_entry.status == JournalEntryStatus.CLOSED:
            raise ValueError("Không thể điều chỉnh bút toán đã khóa sổ")

        if reversal_date is None:
            reversal_date = datetime.now().date()
        if reversal_at is None:
            reversal_at = datetime.now()

        # Sinh ID duy nhất cho bút toán hủy
        import uuid

        reversal_id = f"REV-{uuid.uuid4().hex[:8]}"

        return JournalEntry(
            id=reversal_id,
            account=original_entry.account,
            debit=original_entry.credit,  # Đảo ngược
            credit=original_entry.debit,  # Đảo ngược
            description=f"HỦY [{original_entry.id}]: {original_entry.description}",
            source_document_id=original_entry.source_document_id,
            accounting_date=reversal_date,
            accounting_period_code=original_entry.accounting_period_code,
            status=JournalEntryStatus.ADJUSTED,
            created_by=reverser_id,
            created_at=reversal_at,
            approved_by=reverser_id,  # Tự động duyệt điều chỉnh
            approved_at=reversal_at,
            original_entry_id=original_entry.id,
            is_reversal=True,
            adjustment_reason=reason,
        )

    @staticmethod
    def close_entries_for_period(
        entries: List[JournalEntry], period_code: str
    ) -> List[JournalEntry]:
        """
        Khóa sổ tất cả bút toán trong một kỳ kế toán.

        Args:
            entries (List[JournalEntry]): Danh sách bút toán.
            period_code (str): Mã kỳ cần khóa.

        Returns:
            List[JournalEntry]: Danh sách bút toán đã khóa.

        Note:
            Chỉ khóa các bút toán đã được duyệt (APPROVED).
        """
        closed_entries = []
        for entry in entries:
            if (
                entry.accounting_period_code == period_code
                and entry.status == JournalEntryStatus.APPROVED
            ):
                # Tạo bản sao với trạng thái CLOSED
                closed_entry = JournalEntry(
                    id=entry.id,
                    account=entry.account,
                    debit=entry.debit,
                    credit=entry.credit,
                    description=entry.description,
                    source_document_id=entry.source_document_id,
                    accounting_date=entry.accounting_date,
                    accounting_period_code=entry.accounting_period_code,
                    status=JournalEntryStatus.CLOSED,
                    created_by=entry.created_by,
                    created_at=entry.created_at,
                    approved_by=entry.approved_by,
                    approved_at=entry.approved_at,
                    original_entry_id=entry.original_entry_id,
                    is_reversal=entry.is_reversal,
                    adjustment_reason=entry.adjustment_reason,
                )
                closed_entries.append(closed_entry)
            else:
                closed_entries.append(entry)
        return closed_entries
