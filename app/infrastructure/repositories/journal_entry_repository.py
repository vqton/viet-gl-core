# app/infrastructure/repositories/journal_entry_repository.py
from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.application.interfaces.journal_entry_repo import (
    JournalEntryRepositoryInterface,
)
from app.domain.models.journal_entry import (
    GhiSoKeToan,
    ButToanLine,
    TransactionType,
)
from app.infrastructure.models.sql_journal_entry import (
    SQLJournalEntry,
    SQLJournalEntryLine,
)
from app.infrastructure.repositories.account_repository import (
    AccountRepository,
)


class JournalEntryRepository(JournalEntryRepositoryInterface):
    """
    Repository cho Bút Toán (JournalEntry).
    Ánh xạ Domain ↔ ORM đầy đủ, bao gồm chứng từ gốc theo TT99 Điều 10.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.account_repository = AccountRepository(db_session)

    def add(self, entry: GhiSoKeToan) -> GhiSoKeToan:
        """Thêm bút toán mới vào DB, ánh xạ đầy đủ chứng từ gốc."""
        sql_je = SQLJournalEntry(
            ngay_ct=entry.entry_date,
            so_phieu=entry.document_number,
            mo_ta=entry.description,
            trang_thai="Draft",
        )
        self.db_session.add(sql_je)
        self.db_session.flush()  # Lấy ID để gán cho dòng

        sql_lines = []
        for line in entry.lines:
            # Xác định số tiền Nợ/Có từ amount + transaction_type
            no_val = (
                line.amount
                if line.transaction_type == TransactionType.DEBIT
                else Decimal(0)
            )
            co_val = (
                line.amount
                if line.transaction_type == TransactionType.CREDIT
                else Decimal(0)
            )

            sql_line = SQLJournalEntryLine(
                journal_entry_id=sql_je.id,
                so_tai_khoan=line.account_number,
                no=no_val,
                co=co_val,
                mo_ta="",
                # === ÁNH XẠ CHỨNG TỪ GỐC THEO TT99 ĐIỀU 10 ===
                so_chung_tu_goc=line.so_chung_tu_goc,
                ngay_chung_tu_goc=line.ngay_chung_tu_goc,
            )
            sql_lines.append(sql_line)

        self.db_session.add_all(sql_lines)
        self.db_session.commit()

        # Trả về domain model đã được lưu (có ID từ DB nếu cần)
        return GhiSoKeToan(
            entry_id=str(sql_je.id),  # Có thể dùng ID số hoặc giữ UUID
            entry_date=sql_je.ngay_ct,
            document_type=entry.document_type,
            document_number=sql_je.so_phieu,
            description=sql_je.mo_ta,
            lines=entry.lines,
            created_at=entry.created_at,
        )

    def get_by_id(self, id: int) -> Optional[GhiSoKeToan]:
        """Lấy bút toán theo ID, ánh xạ chứng từ gốc từ DB → domain."""
        sql_je = (
            self.db_session.query(SQLJournalEntry)
            .options(joinedload(SQLJournalEntry.lines))
            .filter(SQLJournalEntry.id == id)
            .first()
        )

        if not sql_je:
            return None

        lines_domain = []
        for sql_line in sql_je.lines:
            # Xác định transaction_type từ no/co
            tx_type = (
                TransactionType.DEBIT if sql_line.no > 0 else TransactionType.CREDIT
            )
            amount = sql_line.no + sql_line.co

            lines_domain.append(
                ButToanLine(
                    account_number=sql_line.so_tai_khoan,
                    amount=amount,
                    transaction_type=tx_type,
                    # === ÁNH XẠ CHỨNG TỪ GỐC ===
                    so_chung_tu_goc=sql_line.so_chung_tu_goc,
                    ngay_chung_tu_goc=sql_line.ngay_chung_tu_goc,
                    detail_object_type=None,  # Cần mở rộng nếu có
                    detail_object_id=None,
                )
            )

        return GhiSoKeToan(
            entry_id=str(sql_je.id),
            entry_date=sql_je.ngay_ct,
            document_type="",  # Cần lưu trữ nếu có
            document_number=sql_je.so_phieu,
            description=sql_je.mo_ta,
            lines=lines_domain,
            created_at=sql_je.ngay_ct,
        )

    def get_all_posted_in_range(self, start: date, end: date) -> List[GhiSoKeToan]:
        """Lấy tất cả bút toán đã ghi sổ trong khoảng thời gian."""
        sql_entries = (
            self.db_session.query(SQLJournalEntry)
            .options(joinedload(SQLJournalEntry.lines))
            .filter(
                SQLJournalEntry.trang_thai == "Posted",
                SQLJournalEntry.ngay_ct >= start,
                SQLJournalEntry.ngay_ct <= end,
            )
            .all()
        )

        return [self._map_sql_to_domain(sql_je) for sql_je in sql_entries]

    def update_status(self, id: int, new_status: str) -> GhiSoKeToan:
        """Cập nhật trạng thái bút toán (Draft/Posted/Locked)."""
        sql_je = (
            self.db_session.query(SQLJournalEntry)
            .filter(SQLJournalEntry.id == id)
            .first()
        )
        if not sql_je:
            raise ValueError(f"Bút toán ID {id} không tồn tại.")

        sql_je.trang_thai = new_status
        self.db_session.commit()

        return self.get_by_id(id)

    def get_draft_entries_by_date_range(
        self, start: date, end: date
    ) -> List[GhiSoKeToan]:
        """Lấy các bút toán ở trạng thái Draft trong khoảng thời gian (dùng cho khóa kỳ)."""
        sql_entries = (
            self.db_session.query(SQLJournalEntry)
            .options(joinedload(SQLJournalEntry.lines))
            .filter(
                SQLJournalEntry.trang_thai == "Draft",
                SQLJournalEntry.ngay_ct >= start,
                SQLJournalEntry.ngay_ct <= end,
            )
            .all()
        )
        return [self._map_sql_to_domain(sql_je) for sql_je in sql_entries]

    def _map_sql_to_domain(self, sql_je: SQLJournalEntry) -> GhiSoKeToan:
        """Hàm trợ giúp ánh xạ SQLJournalEntry → GhiSoKeToan."""
        lines_domain = []
        for sql_line in sql_je.lines:
            tx_type = (
                TransactionType.DEBIT if sql_line.no > 0 else TransactionType.CREDIT
            )
            amount = sql_line.no + sql_line.co
            lines_domain.append(
                ButToanLine(
                    account_number=sql_line.so_tai_khoan,
                    amount=amount,
                    transaction_type=tx_type,
                    so_chung_tu_goc=sql_line.so_chung_tu_goc,
                    ngay_chung_tu_goc=sql_line.ngay_chung_tu_goc,
                    detail_object_type=None,
                    detail_object_id=None,
                )
            )
        return GhiSoKeToan(
            entry_id=str(sql_je.id),
            entry_date=sql_je.ngay_ct,
            document_type="",  # ← Cần mở rộng nếu lưu `document_type`
            document_number=sql_je.so_phieu,
            description=sql_je.mo_ta,
            lines=lines_domain,
            created_at=sql_je.ngay_ct,
        )
