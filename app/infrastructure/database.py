# File: app/infrastructure/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import (  # <-- Cập nhật import
    declarative_base,
    sessionmaker,
)

from app.config import DATABASE_URL

# 1. Tạo engine kết nối DB
engine = create_engine(DATABASE_URL)

# 2. SessionLocal là class factory để tạo session object
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 3. Base là lớp cơ sở cho các ORM model
Base = declarative_base()

# --- QUAN TRỌNG: Import các ORM Model sau khi Base được định nghĩa ---
# Điều này đảm bảo Base.metadata biết về các model này.
# Nếu bạn có nhiều model, import tất cả ở đây.
from app.infrastructure.models.sql_account import (  # <-- Import SQLAccount
    SQLAccount,
)
from app.infrastructure.models.sql_accounting_period import (  # <-- Thêm import này
    SQLAccountingPeriod,
)
from app.infrastructure.models.sql_journal_entry import (  # <-- Import các model khác nếu có
    SQLJournalEntry,
    SQLJournalEntryLine,
)

# (Có thể import các model khác sau này)
# from app.infrastructure.models.other_models import OtherModel

# --- Hết phần import ---


def get_db():
    """
    Dependency để inject DB session vào các endpoint hoặc service.
    FastAPI sẽ sử dụng hàm này để cung cấp session cho mỗi request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Hàm tiện ích để tạo schema (chỉ dùng cho dev/migration sau này nếu không dùng Alembic)
def create_tables():
    """
    Tạo tất cả các bảng dựa trên ORM models đã được import.
    Chỉ nên dùng cho dev hoặc khởi tạo DB mới.
    """
    Base.metadata.create_all(bind=engine)
    print("Các bảng đã được tạo (hoặc đã tồn tại).")


# Nếu bạn muốn chạy create_tables khi file này được chạy trực tiếp (chỉ dev)
if __name__ == "__main__":
    print("Đang tạo bảng... (nếu chưa tồn tại)")
    # Bật logging tạm thời nếu cần debug create_tables
    import logging

    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    create_tables()
