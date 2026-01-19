import json
import os
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert
from source.database.foundation import engine
from source.database.models.accounts import Account
from source.database.models.customers import Customer
from source.database.models.vendors import Vendor
from source.database.models.employees import Employee

class DataIngestionService:
    def __init__(self):
        self.model_map = {
            "accounts": Account,
            "customers": Customer,
            "vendors": Vendor,
            "employees": Employee
        }

    def _extract_metadata(self, model, data: dict):
        """
        Tách các trường không có trong Schema để đẩy vào metadata_info.
        """
        main_columns = model.__table__.columns.keys()
        main_data = {}
        metadata = {}

        for key, value in data.items():
            if key in main_columns:
                main_data[key] = value
            else:
                metadata[key] = value
        
        # Nếu model có cột metadata_info, ta đóng gói phần dư thừa vào đó
        if "metadata_info" in main_columns:
            main_data["metadata_info"] = metadata
            
        return main_data

    def ingest_json(self, db: Session, target_type: str, file_path: str):
        """
        Nạp dữ liệu từ JSON vào Database theo phương thức Upsert (Insert or Update).
        """
        if not os.path.exists(file_path):
            print(f"⚠️ Cảnh báo: Không tìm thấy file {file_path}")
            return

        model = self.model_map.get(target_type)
        if not model:
            raise ValueError(f"❌ Loại dữ liệu '{target_type}' không được hỗ trợ.")

        with open(file_path, 'r', encoding='utf-8') as f:
            records = json.load(f)

        count = 0
        for record in records:
            # Xử lý bóc tách metadata thông minh
            clean_data = self._extract_metadata(model, record)
            
            # Kỹ thuật Upsert: Nếu trùng ID thì cập nhật, chưa có thì thêm mới
            stmt = insert(model).values(**clean_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['id'],
                set_=clean_data
            )
            
            db.execute(stmt)
            count += 1
        
        db.commit()
        print(f"✅ Đã nạp {count} bản ghi vào bảng {target_type.upper()}.")

# Khởi tạo instance dùng chung
ingestion_service = DataIngestionService()