# PATH: D:\tt99acct\source/database/models/master_data.py
"""
PATH: source/database/models/master_data.py
STATUS: Production-ready
DESCRIPTION: 
    Quản lý danh mục tài khoản (Chart of Accounts) và các danh mục gốc.
    Thiết kế hỗ trợ cấu trúc cây (Parent-Child) vô hạn cấp để đáp ứng TT99.
LOGIC:
    - Chỉ tài khoản cấp LÁ (is_leaf=True) mới được phép hạch toán nghiệp vụ.
    - Xử lý ràng buộc RESTRICT: Không cho xóa tài khoản cha nếu còn tài khoản con.
"""

from typing import List, Optional
from sqlalchemy import String, Boolean, ForeignKey, Index, CheckConstraint, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates
from ..base import Base, EnterpriseMixin

class AccountModel(Base, EnterpriseMixin):
    """
    Model Tài khoản kế toán.
    Đáp ứng tiêu chuẩn Production: Indexing cho báo cáo nhanh, Constraints bảo vệ dữ liệu.
    """
    __tablename__ = "accounts"

    # --- ĐỊNH DANH & THÔNG TIN GỐC ---
    id: Mapped[str] = mapped_column(String(20), primary_key=True, comment="Số hiệu tài khoản (Ví dụ: 1111)")
    name: Mapped[str] = mapped_column(String(255), nullable=False, comment="Tên gọi tài khoản")
    
    # --- CẤU TRÚC CÂY (HIERARCHY) ---
    parent_id: Mapped[Optional[str]] = mapped_column(
        String(20), 
        ForeignKey("accounts.id", ondelete="RESTRICT"), # Bảo vệ: Không xóa cha khi còn con
        nullable=True,
        index=True
    )
    
    is_leaf: Mapped[bool] = mapped_column(
        Boolean, 
        default=True, 
        index=True, 
        comment="True nếu là tài khoản chi tiết cuối cùng"
    )
    
    level: Mapped[int] = mapped_column(
        default=1, 
        comment="Cấp độ tài khoản (1, 2, 3...)"
    )

    # --- TÍNH CHẤT KẾ TOÁN (TT99) ---
    # Ví dụ: Asset (Tài sản), Liability (Nợ phải trả), Equity (Nguồn vốn)...
    acc_type: Mapped[str] = mapped_column(String(20), index=True, comment="Loại tài khoản")
    
    # Tính chất số dư: DEBIT (Nợ), CREDIT (Có), BOTH (Lưỡng tính)
    nature: Mapped[str] = mapped_column(String(10), default="DEBIT")

    # --- QUAN HỆ ĐỆ QUY ---
    children: Mapped[List["AccountModel"]] = relationship(
        "AccountModel", backref="parent", remote_side=[id]
    )

    # --- PRODUCTION-READY CONSTRAINTS ---
    __table_args__ = (
        # Đảm bảo mã tài khoản không trống
        CheckConstraint("length(id) > 0", name="ck_account_id_not_empty"),
        # Chỉ mục tìm kiếm nhanh theo tên cho kế toán khi gõ tìm kiếm
        Index("ix_accounts_name_search", "name"),
    )

    # --- VALIDATION LOGIC ---
    @validates("id")
    def validate_id(self, key, value):
        if not value or len(value) < 1:
            raise ValueError("Mã tài khoản không được để trống.")
        return value

    def __repr__(self) -> str:
        return f"<Account(id={self.id}, name={self.name}, leaf={self.is_leaf})>"

class CurrencyModel(Base, EnterpriseMixin):
    """
    Danh mục Tiền tệ.
    Sử dụng kiểu Numeric cho tỷ giá để đảm bảo độ chính xác tài chính.
    """
    __tablename__ = "currencies"
    
    code: Mapped[str] = mapped_column(String(3), primary_key=True, comment="Mã tiền tệ (VND, USD)")
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Sử dụng Numeric thay vì Float để tránh sai số lũy kế trong kế toán
    exchange_rate: Mapped[float] = mapped_column(Numeric(18, 4), default=1.0)
    is_base: Mapped[bool] = mapped_column(Boolean, default=False, comment="Đồng tiền hạch toán chính")

    def __repr__(self) -> str:
        return f"<Currency(code={self.code}, rate={self.exchange_rate})>"