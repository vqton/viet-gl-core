# File: app/infrastructure/models/sql_journal_entry.py

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship
from app.infrastructure.base import Base
from app.infrastructure.models.sql_account import SQLAccount


class SQLJournalEntryLine(Base):
    """
    ORM Model đại diện cho bảng 'journal_entry_lines' trong cơ sở dữ liệu,
    ánh xạ tới Value Object 'JournalEntryLine' trong Domain.

    [TT99-Đ10] Mỗi dòng bút toán phải có chứng từ gốc →
    bắt buộc có so_chung_tu_goc và ngay_chung_tu_goc.
    """

    __tablename__ = "journal_entry_lines"

    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(Integer, ForeignKey("journal_entries.id"), nullable=False)
    so_tai_khoan = Column(
        String(20), ForeignKey("accounts.so_tai_khoan"), nullable=False
    )
    no = Column(Numeric(precision=19, scale=4), nullable=False)
    co = Column(Numeric(precision=19, scale=4), nullable=False)
    mo_ta = Column(String(256), nullable=True)

    # === [TT99-Đ10] BẮT BUỘC CHỨNG TỪ GỐC ===
    so_chung_tu_goc = Column(String(50), nullable=False)
    ngay_chung_tu_goc = Column(Date, nullable=False)

    # Relationships
    journal_entry = relationship("SQLJournalEntry", back_populates="lines")
    account = relationship("SQLAccount")


class SQLJournalEntry(Base):
    """
    ORM Model đại diện cho bảng 'journal_entries' trong cơ sở dữ liệu,
    ánh xạ tới Entity 'JournalEntry' trong Domain.
    """

    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    ngay_ct = Column(Date, nullable=False)
    so_phieu = Column(String(50), nullable=False, unique=True)
    mo_ta = Column(String(512), nullable=True)
    trang_thai = Column(String(20), nullable=False, default="Draft")

    lines = relationship(
        "SQLJournalEntryLine",
        back_populates="journal_entry",
        cascade="all, delete-orphan",
    )
