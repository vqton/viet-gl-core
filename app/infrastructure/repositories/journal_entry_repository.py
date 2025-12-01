from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.domain.models.journal_entry import JournalEntry as JournalEntryDomain, JournalEntryLine as JournalEntryLineDomain
from app.infrastructure.models.sql_journal_entry import SQLJournalEntry, SQLJournalEntryLine
from app.infrastructure.repositories.account_repository import AccountRepository # Import để kiểm tra tài khoản
from typing import List, Optional
from datetime import date
from decimal import Decimal

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
            trang_thai=journal_entry_domain.trang_thai,
            # lines sẽ được thêm sau
        )
        self.db_session.add(sql_journal_entry)
        self.db_session.flush() # Lấy ID của bút toán cha trước

        # Thêm các dòng bút toán
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

        self.db_session.add_all(sql_lines)
        self.db_session.commit()
        self.db_session.refresh(sql_journal_entry)

        # Chuyển đổi lại về Domain Entity để trả về (cần load lines)
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

    def get_by_id(self, id: int) -> Optional[JournalEntryDomain]:
        """
        Lấy thông tin bút toán theo ID, bao gồm các dòng.
        """
        sql_j = self.db_session.query(SQLJournalEntry).options(joinedload(SQLJournalEntry.lines)).filter(SQLJournalEntry.id == id).first()
        if not sql_j:
            return None

        lines_domain = [\
            JournalEntryLineDomain(\
                so_tai_khoan=line.so_tai_khoan,\
                no=line.no,\
                co=line.co,\
                mo_ta=line.mo_ta\
            )\
            for line in sql_j.lines\
        ]
        return JournalEntryDomain(
            id=sql_j.id,
            ngay_ct=sql_j.ngay_ct,
            so_phieu=sql_j.so_phieu,
            mo_ta=sql_j.mo_ta,
            lines=lines_domain,
            trang_thai=sql_j.trang_thai
        )

    def get_all(self) -> List[JournalEntryDomain]:
        """
        Lấy danh sách tất cả bút toán, bao gồm các dòng.
        """
        sql_journal_entries = self.db_session.query(SQLJournalEntry).options(joinedload(SQLJournalEntry.lines)).all()
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
            # Giả định period_id được thêm vào SQLJournalEntry (chưa thấy trong snippet)
            # Tạm thời chỉ trả về tất cả cho đến khi mô hình SQLJournalEntry được cập nhật
            return self.db_session.query(SQLJournalEntry).all()
            # return self.db_session.query(SQLJournalEntry).filter(SQLJournalEntry.period_id == period_id).all()

    def update(self, id: int, journal_entry_domain_updated: JournalEntryDomain) -> Optional[JournalEntryDomain]:
        """
        Cập nhật thông tin bút toán.
        Giả định rằng việc cập nhật sẽ xóa Lines cũ và thêm Lines mới (hoặc chỉ cập nhật trạng thái).
        """
        sql_journal_entry = self.db_session.query(SQLJournalEntry).options(joinedload(SQLJournalEntry.lines)).filter(SQLJournalEntry.id == id).first()
        if not sql_journal_entry:
            return None

        # 1. Cập nhật thông tin chính
        sql_journal_entry.ngay_ct = journal_entry_domain_updated.ngay_ct
        sql_journal_entry.so_phieu = journal_entry_domain_updated.so_phieu
        sql_journal_entry.mo_ta = journal_entry_domain_updated.mo_ta
        sql_journal_entry.trang_thai = journal_entry_domain_updated.trang_thai

        # 2. Xóa lines cũ (Nếu có thay đổi nội dung bút toán, nếu chỉ thay đổi trạng thái thì bỏ qua)
        # Trong hệ thống thật, cần kiểm tra sâu hơn về việc cho phép sửa đổi.
        for line in sql_journal_entry.lines:
            self.db_session.delete(line)

        # 3. Thêm lines mới
        sql_lines = []
        for line_domain in journal_entry_domain_updated.lines:
            sql_line = SQLJournalEntryLine(
                journal_entry_id=sql_journal_entry.id,
                so_tai_khoan=line_domain.so_tai_khoan,
                no=line_domain.no,
                co=line_domain.co,
                mo_ta=line_domain.mo_ta
            )
            sql_lines.append(sql_line)
        
        sql_journal_entry.lines = sql_lines # Gán lại relationship

        self.db_session.commit()
        self.db_session.refresh(sql_journal_entry)

        # Chuyển đổi lại về Domain Entity để trả về
        lines_domain_updated = [
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
            lines=lines_domain_updated,
            trang_thai=sql_journal_entry.trang_thai
        )
    
    def delete(self, id: int) -> bool:
        """
        Xóa một bút toán và các dòng liên quan.
        """
        sql_journal_entry = self.db_session.query(SQLJournalEntry).options(joinedload(SQLJournalEntry.lines)).filter(SQLJournalEntry.id == id).first()
        if not sql_journal_entry:
            return False
        
        # Xóa các dòng trước (Cascade Delete nên được thiết lập ở ORM, nhưng làm thủ công cho chắc chắn)
        for line in sql_journal_entry.lines:
            self.db_session.delete(line)
            
        self.db_session.delete(sql_journal_entry)
        self.db_session.commit()
        return True

    def get_posted_lines_by_account_and_date(self, so_tai_khoan: str, end_date: date) -> List[JournalEntryLineDomain]:
        """
        Lấy danh sách các dòng bút toán đã được 'Posted' cho một tài khoản cụ thể
        và có ngày chứng từ (ngay_ct) nhỏ hơn hoặc bằng end_date.
        """
        # 1. Query các dòng bút toán (SQLJournalEntryLine)
        # 2. Join với bút toán cha (SQLJournalEntry)
        # 3. Filter theo so_tai_khoan, trang_thai='Posted', và ngay_ct <= end_date
        
        # Lấy các dòng bút toán
        sql_lines = (
            self.db_session.query(SQLJournalEntryLine)
            .join(SQLJournalEntry, SQLJournalEntry.id == SQLJournalEntryLine.journal_entry_id)
            .filter(SQLJournalEntryLine.so_tai_khoan == so_tai_khoan)
            .filter(SQLJournalEntry.trang_thai == "Posted")
            .filter(SQLJournalEntry.ngay_ct <= end_date)
            .all()
        )
        
        # Chuyển đổi sang Domain VO
        return [
            JournalEntryLineDomain(
                so_tai_khoan=line.so_tai_khoan,
                no=line.no,
                co=line.co,
                mo_ta=line.mo_ta
            )
            for line in sql_lines
        ]