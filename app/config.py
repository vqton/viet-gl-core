# File: app/config.py
import os
from dotenv import load_dotenv

# Load các biến môi trường từ file .env
load_dotenv()

# Đọc DATABASE_URL từ biến môi trường
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("Biến môi trường DATABASE_URL chưa được thiết lập trong file .env")

# (Bạn có thể thêm các biến cấu hình khác ở đây nếu cần sau này)
# Ví dụ:
# SECRET_KEY = os.getenv("SECRET_KEY", "your-fallback-secret-key")
# DEBUG = os.getenv("DEBUG", "False").lower() == "true"