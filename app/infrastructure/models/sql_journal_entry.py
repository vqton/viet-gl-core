# File: app/infrastructure/models/sql_journal_entry.py

from sqlalchemy import Column, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import (  # Import relationship
    declarative_base,
    relationship,
)

from app.infrastructure.base import Base
from app.infrastructure.models.sql_account import (  # Import để ràng buộc FK
    SQLAccount,
)

# from app.infrastructure.database import Base


class SQLJournalEntryLine(Base):
    """
    ORM Model đại diện cho bảng 'journal_entry_lines' trong cơ sở dữ liệu,
    ánh xạ tới Value Object 'JournalEntryLine' trong Domain.
    """

    __tablename__ = 'journal_entry_lines'

    id = Column(Integer, primary_key=True, index=True)
    journal_entry_id = Column(
        Integer, ForeignKey('journal_entries.id'), nullable=False
    )  # Khóa ngoại đến bút toán cha
    so_tai_khoan = Column(
        String(20), ForeignKey('accounts.so_tai_khoan'), nullable=False
    )  # Khóa ngoại đến tài khoản
    no = Column(
        Numeric(precision=19, scale=4), nullable=False
    )  # Số tiền ghi Nợ
    co = Column(
        Numeric(precision=19, scale=4), nullable=False
    )  # Số tiền ghi Có
    mo_ta = Column(String(256), nullable=True)  # Mô tả dòng (tuỳ chọn)

    # Relationship đến bút toán cha
    journal_entry = relationship("SQLJournalEntry", back_populates="lines")
    # Relationship đến tài khoản
    account = relationship(
        "SQLAccount"
    )  # Không cần back_populates nếu không cần truy vấn ngược từ tài khoản


class SQLJournalEntry(Base):
    """
    ORM Model đại diện cho bảng 'journal_entries' trong cơ sở dữ liệu,
    ánh xạ tới Entity 'JournalEntry' trong Domain.
    """

    __tablename__ = 'journal_entries'

    id = Column(Integer, primary_key=True, index=True)
    ngay_ct = Column(Date, nullable=False)
    so_phieu = Column(
        String(50), nullable=False, unique=True
    )  # Số phiếu phải là duy nhất
    mo_ta = Column(String(512), nullable=True)
    trang_thai = Column(
        String(20), nullable=False, default="Draft"
    )  # Draft, Posted, Locked

    # Relationship đến các dòng bút toán
    lines = relationship(
        "SQLJournalEntryLine",
        back_populates="journal_entry",
        cascade="all, delete-orphan",
    )
    # cascade="all, delete-orphan" đảm bảo khi xóa bút toán cha, các dòng con cũng bị xóa
