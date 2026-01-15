# PATH: D:/tt99acct/source/core/db_config.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Cấu hình đường dẫn Database (Mặc định dùng SQLite tại thư mục gốc dự án)
# Trong tương lai có thể thay bằng: "postgresql://user:password@localhost/dbname"
DATABASE_URL = "sqlite:///D:/tt99acct/tt99_core.db"

# Khởi tạo Engine với cấu hình tối ưu
# check_same_thread=False chỉ dành cho SQLite để hỗ trợ đa luồng
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Chuyển thành True nếu muốn log toàn bộ câu lệnh SQL ra console
)

# Tạo Session factory để quản lý các phiên làm việc với DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function để quản lý vòng đời của một Database Session.
    Đảm bảo session luôn được đóng sau khi sử dụng xong.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()