import os

from dotenv import load_dotenv

# Load các biến môi trường từ file .env
load_dotenv()

# Đọc DATABASE_URL từ biến môi trường
# [Cấu hình] Chuỗi kết nối đến cơ sở dữ liệu (ví dụ: SQLite, PostgreSQL).
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "Biến môi trường DATABASE_URL chưa được thiết lập trong file .env"
    )

# (Bạn có thể thêm các biến cấu hình khác ở đây nếu cần sau này)
