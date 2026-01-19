# Path: bootstrap.py
"""
BOOTSTRAPPER: Khởi tạo và đồng bộ hóa toàn bộ dự án.
Quy trình: Làm sạch DB -> Tạo bảng -> Nạp dữ liệu Master Data từ JSON.
"""

import os
from sqlalchemy.orm import Session
from source.database.foundation import engine, Base
from source.services.data_ingestion import ingestion_service

def reset_database():
    """Xóa bỏ và khởi tạo lại Schema Database."""
    print("--- 🛠️  INITIALIZING SYSTEM ---")
    if not os.path.exists('data'):
        os.makedirs('data')
    
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Schema created successfully.")

def run_ingestion():
    """Nạp dữ liệu theo thứ tự ưu tiên."""
    with Session(engine) as session:
        # 1. Accounts phải nạp trước
        ingestion_service.ingest_json(session, "accounts", "source/master/data/chart_of_accounts/accounts_tt99.json")
        # 2. Partners nạp sau
        ingestion_service.ingest_json(session, "customers", "source/master/data/partners/customers.json")
        ingestion_service.ingest_json(session, "vendors", "source/master/data/partners/vendors.json")
        ingestion_service.ingest_json(session, "employees", "source/master/data/partners/employees.json")

if __name__ == "__main__":
    reset_database()
    run_ingestion()
    print("\n--- 🚀 SYSTEM READY ---")