# File: app/infrastructure/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.infrastructure.base import Base
from app.config import DATABASE_URL


engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Import models SAU Base + engine
from app.infrastructure.models.sql_account import SQLAccount
from app.infrastructure.models.sql_journal_entry import (
    SQLJournalEntry,
    SQLJournalEntryLine
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    print("Metadata tables loaded:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)
    print("Các bảng đã được tạo (hoặc đã tồn tại).")


if __name__ == "__main__":
    create_tables()
