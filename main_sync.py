"""
PATH: main_sync.py
STATUS: Latest Production Version
REVISION: 
    - Mở rộng master_data_map để nạp tài khoản Super Full.
    - Chia nhỏ Entities thành Customers, Vendors, Employees để quản trị MDM.
"""

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Đảm bảo hệ thống nhận diện được folder source
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from source.database.base import Base
from source.services.sync_service import SyncService

# Cấu hình đường dẫn DB
DB_URL = "sqlite:///data/finance.db"

def run_latest_sync():
    # 1. Khởi tạo môi trường
    if not os.path.exists("data"):
        os.makedirs("data")
    
    engine = create_engine(DB_URL)
    SessionLocal = sessionmaker(bind=engine)
    
    print("[SYSTEM] --- KHỞI CHẠY ĐỒNG BỘ DANH MỤC THÔNG TƯ 99/2025 ---")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    sync_tool = SyncService(db)

    # 2. Cập nhật Latest Master Data Map
    # Chia nhỏ để dễ dàng quản lý theo phòng ban (Kế toán bán hàng/mua hàng/nhân sự)
    master_data_map = {
        "accounts": "source/master/data/accounts_tt99.json",  # Bản Super Full >100 rows
        "customers": "source/master/data/customers.json",    # File chuyên biệt Khách hàng
        "vendors": "source/master/data/vendors.json",        # File chuyên biệt Nhà cung cấp
        "employees": "source/master/data/employees.json"      # File chuyên biệt Nhân viên
    }

    try:
        # Nạp theo thứ tự ưu tiên (Accounts luôn nạp trước để làm gốc cho hạch toán)
        sync_tool.sync_all_master_data(master_data_map)
        print("[SUCCESS] --- HỆ THỐNG ĐÃ SẴN SÀNG VỚI DỮ LIỆU MỚI NHẤT ---")
    except Exception as e:
        print(f"[CRITICAL ERROR] Quá trình đồng bộ thất bại: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    run_latest_sync()