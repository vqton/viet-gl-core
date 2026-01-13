"""
PATH: D:/TT99ACCT/source/database/models/accounting.py
"""

from sqlalchemy import (
    Column,
    String,
    Float,
    Date,
    ForeignKey,
    Integer,
    CheckConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from ..base import Base, EnterpriseMixin


class VoucherHeaderModel(Base, EnterpriseMixin):
    __tablename__ = "voucher_header"

    v_id = Column(String(100), primary_key=True)
    v_type = Column(String(10), nullable=False, index=True)  # PT, PC, PN, PX, PK
    v_no = Column(String(50), unique=True, nullable=False, index=True)
    date_at = Column(Date, nullable=False, index=True)
    description = Column(String(500))
    status = Column(String(20), default="POSTED")  # DRAFT, POSTED, CANCELLED

    # Quan hệ 1-Nhiều: Một chứng từ có nhiều dòng định khoản
    # cascade="all, delete-orphan": Xóa chứng từ là xóa sạch định khoản liên quan
    entries = relationship(
        "JournalEntryModel", back_populates="header", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return (
            f"<Voucher(no='{self.v_no}', type='{self.v_type}', date='{self.date_at}')>"
        )


class JournalEntryModel(Base, EnterpriseMixin):
    __tablename__ = "journal_entries"

    line_id = Column(Integer, primary_key=True, autoincrement=True)
    v_id = Column(
        String(100),
        ForeignKey("voucher_header.v_id", ondelete="CASCADE"),
        nullable=False,
    )

    # Thông tin hạch toán
    account_id = Column(String(20), nullable=False, index=True)
    entity_id = Column(String(50), ForeignKey("entities.entity_id"), nullable=True)
    description = Column(String(500))

    # Số tiền (Enterprise bắt buộc không âm tại tầng DB)
    debit = Column(Float, default=0.0)
    credit = Column(Float, default=0.0)

    # Quan hệ ngược lại
    header = relationship("VoucherHeaderModel", back_populates="entries")
    entity = relationship("EntityModel")  # Để lấy thông tên khách hàng khi in sổ cái

    # CORE: Bổ sung các cột bắt buộc theo TT99
    source_id = Column(
        String(20), nullable=True
    )  # Mã nguồn kinh phí (Kinh phí tự chủ, không tự chủ...)
    budget_chapter = Column(String(10), nullable=True)  # Chương
    budget_kind = Column(String(10), nullable=True)  # Loại
    budget_sub_kind = Column(String(10), nullable=True)  # Khoản
    budget_item = Column(String(10), nullable=True)  # Mục
    budget_sub_item = Column(String(10), nullable=True)  # Tiểu mục

    # Ràng buộc bảo vệ dữ liệu tài chính
    __table_args__ = (
        CheckConstraint("debit >= 0", name="check_debit_positive"),
        CheckConstraint("credit >= 0", name="check_credit_positive"),
        Index("idx_account_date", "account_id", "v_id"),  # Tối ưu tốc độ xuất sổ cái
    )

    def __repr__(self):
        return f"<Entry(acc='{self.account_id}', dr={self.debit}, cr={self.credit})>"
