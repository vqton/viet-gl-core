# File: test_db.py
# Thiết lập một database tạm thời (in-memory SQLite) cho mục đích kiểm thử

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.base import Base  # Import Base từ file cơ sở

# Sử dụng SQLite in-memory cho tốc độ, hoặc file DB tạm thời nếu cần
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
# Sử dụng in-memory database
engine = create_engine(
    "sqlite:///:memory:", connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


def override_get_db():
    """
    Hàm Dependency để cung cấp Session cho các bài test.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Hàm tiện ích để tạo lại tất cả các bảng trước mỗi lần test
def setup_test_db():
    """
    Tạo tất cả các bảng dựa trên Base.metadata.
    """
    Base.metadata.create_all(bind=engine)


def teardown_test_db():
    """
    Xóa tất cả các bảng.
    """
    Base.metadata.drop_all(bind=engine)


# Cần import tất cả ORM models để Base.metadata biết về chúng
from app.infrastructure.models.sql_account import SQLAccount
from app.infrastructure.models.sql_accounting_period import SQLAccountingPeriod
from app.infrastructure.models.sql_journal_entry import (
    SQLJournalEntry,
    SQLJournalEntryLine,
)

# Import các model khác nếu có
