# File: app/infrastructure/repositories/journal_entry_repository.py

from sqlalchemy.orm import Session
from app.domain.models.journal_entry import JournalEntry as JournalEntryDomain, JournalEntryLine as JournalEntryLineDomain
from app.infrastructure.models.sql_journal_entry import SQLJournalEntry, SQLJournalEntryLine
from app.infrastructure.repositories.account_repository import AccountRepository # Import để kiểm tra tài khoản
from typing import List, Optional

class JournalEntryRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.account_repository = AccountRepository(db_session) # Để kiểm tra tài khoản tồn tại

    def add(self, journal_entry_domain: JournalEntryDomain) -> JournalEntryDomain:
        """
        Thêm một bút toán mới vào cơ sở dữ liệu.
        """
        # Kiểm tra tài khoản tồn tại cho từng dòng
        for line in journal_entry_domain.lines:
            tai_khoan = self.account_repository.get_by_id(line.so_tai_khoan)
            if not tai_khoan:
                raise ValueError(f"Tài khoản '{line.so_tai_khoan}' trong bút toán không tồn tại.")

        # Chuyển đổi từ Domain Entity sang ORM Model
        sql_journal_entry = SQLJournalEntry(
            ngay_ct=journal_entry_domain.ngay_ct,
            so_phieu=journal_entry_domain.so_phieu,
            mo_ta=journal_entry_domain.mo_ta,
            trang_thai=journal_entry_domain.trang_thai
        )
        self.db_session.add(sql_journal_entry)
        self.db_session.flush() # flush() để lấy ID của bút toán cha trước khi tạo dòng con

        sql_lines = []
        for line in journal_entry_domain.lines:
            sql_line = SQLJournalEntryLine(
                journal_entry_id=sql_journal_entry.id,
                so_tai_khoan=line.so_tai_khoan,
                no=line.no,
                co=line.co,
                mo_ta=line.mo_ta
            )
            sql_lines.append(sql_line)
            self.db_session.add(sql_line)

        self.db_session.commit()
        self.db_session.refresh(sql_journal_entry) # Cập nhật lại thông tin bút toán cha (nếu cần)

        # Chuyển đổi lại từ ORM Model sang Domain Entity để trả về
        lines_domain = [
            JournalEntryLineDomain(
                so_tai_khoan=line.so_tai_khoan,
                no=line.no,
                co=line.co,
                mo_ta=line.mo_ta
            )
            for line in sql_lines
        ]
        return JournalEntryDomain(
            id=sql_journal_entry.id,
            ngay_ct=sql_journal_entry.ngay_ct,
            so_phieu=sql_journal_entry.so_phieu,
            mo_ta=sql_journal_entry.mo_ta,
            lines=lines_domain,
            trang_thai=sql_journal_entry.trang_thai
        )

    def get_by_id(self, id: int) -> Optional[JournalEntryDomain]:
        """
        Lấy thông tin bút toán theo ID.
        """
        sql_journal_entry = self.db_session.query(SQLJournalEntry).filter(SQLJournalEntry.id == id).first()
        if not sql_journal_entry:
            return None

        lines_domain = [
            JournalEntryLineDomain(
                so_tai_khoan=line.so_tai_khoan,
                no=line.no,
                co=line.co,
                mo_ta=line.mo_ta
            )
            for line in sql_journal_entry.lines
        ]
        return JournalEntryDomain(
            id=sql_journal_entry.id,
            ngay_ct=sql_journal_entry.ngay_ct,
            so_phieu=sql_journal_entry.so_phieu,
            mo_ta=sql_journal_entry.mo_ta,
            lines=lines_domain,
            trang_thai=sql_journal_entry.trang_thai
        )

    def get_all(self) -> List[JournalEntryDomain]:
        """
        Lấy danh sách tất cả bút toán.
        """
        sql_journal_entries = self.db_session.query(SQLJournalEntry).all()
        journal_entries_domain = []
        for sql_j in sql_journal_entries:
            lines_domain = [
                JournalEntryLineDomain(
                    so_tai_khoan=line.so_tai_khoan,
                    no=line.no,
                    co=line.co,
                    mo_ta=line.mo_ta
                )
                for line in sql_j.lines
            ]
            journal_entries_domain.append(
                JournalEntryDomain(
                    id=sql_j.id,
                    ngay_ct=sql_j.ngay_ct,
                    so_phieu=sql_j.so_phieu,
                    mo_ta=sql_j.mo_ta,
                    lines=lines_domain,
                    trang_thai=sql_j.trang_thai
                )
            )
        return journal_entries_domain

    def get_all_by_period(self, period_id: int) -> List[SQLJournalEntry]:
            """
            Lấy tất cả bút toán trong một kỳ kế toán.
            Giả sử có trường period_id trong SQLJournalEntry.
            """
            return self.db_session.query(SQLJournalEntry).filter(SQLJournalEntry.period_id == period_id).all()

    def update(self, sql_journal_entry: SQLJournalEntry) -> None:
        """
        Cập nhật thông tin bút toán (chủ yếu để thay đổi trạng thái trang_thai).
        """
        self.db_session.add(sql_journal_entry)
        self.db_session.commit()
        self.db_session.refresh(sql_journal_entry)
    # (Có thể thêm các phương thức khác như update, delete, find_by_condition nếu cần)