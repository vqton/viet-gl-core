# app/infrastructure/repositories/reporting_repository_impl.py
from datetime import date
from decimal import Decimal
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.application.interfaces.reporting_repository import ReportingRepository
from app.domain.models.account import TaiKhoan
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine
from app.infrastructure.models.sql_account import SQLAccount

# --- Các import cần thiết để file không bị lỗi (giả sử bạn có các model này)
from app.infrastructure.models.sql_journal_entry import SQLJournalEntry


class ReportingRepositoryImpl(ReportingRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all_posted_entries_in_range(
        self, start: date, end: date
    ) -> List[JournalEntry]:
        # Truy vấn từ SQLJournalEntry và map sang Domain
        sql_entries = (
            self.db.query(SQLJournalEntry)
            .filter(
                SQLJournalEntry.ngay_ct.between(start, end),
                SQLJournalEntry.trang_thai == "Posted",
            )
            .all()
        )

        return [self._map_sql_to_domain(sql_e) for sql_e in sql_entries]

    def get_all_accounts(self) -> List[TaiKhoan]:
        sql_accounts = self.db.query(SQLAccount).all()
        return [
            TaiKhoan(
                so_tai_khoan=sql_acc.so_tai_khoan,
                ten_tai_khoan=sql_acc.ten_tai_khoan,
                loai_tai_khoan=sql_acc.loai_tai_khoan,
                cap_tai_khoan=sql_acc.cap_tai_khoan,
                so_tai_khoan_cha=sql_acc.so_tai_khoan_cha,
                la_tai_khoan_tong_hop=sql_acc.la_tai_khoan_tong_hop,
            )
            for sql_acc in sql_accounts
        ]

    def get_opening_balance(self, so_tai_khoan: str, ngay: date) -> Decimal:
        # Lấy số dư đầu kỳ từ bảng Sổ Cái hoặc Sổ Tổng Hợp
        # Trong ví dụ này, giả lập
        return Decimal("0")

    def get_account_balance(
        self, so_tai_khoan: str, ngay_bat_dau: date, ngay_ket_thuc: date
    ) -> Tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
        # Tính số dư đầu kỳ, phát sinh, số dư cuối kỳ
        # Trả về (SDĐK, PS Nợ, PS Có, SDCK Nợ, SDCK Có)
        # Trong ví dụ này, giả lập
        return (
            Decimal("0"),
            Decimal("100"),
            Decimal("50"),
            Decimal("50"),
            Decimal("0"),
        )

    def _map_sql_to_domain(self, sql_entry) -> JournalEntry:
        lines = [
            JournalEntryLine(
                so_tai_khoan=line.so_tai_khoan, no=line.no, co=line.co
            )
            for line in sql_entry.lines
        ]
        return JournalEntry(
            id=sql_entry.id,
            ngay_ct=sql_entry.ngay_ct,
            so_phieu=sql_entry.so_phieu,
            mo_ta=sql_entry.mo_ta,
            lines=lines,
            trang_thai=sql_entry.trang_thai,
        )
