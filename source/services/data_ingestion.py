# Path: source/services/data_ingestion.py
"""
SERVICE: Data Ingestion
PURPOSE: Chuyển đổi dữ liệu thô từ file JSON sang các bản ghi SQL Database.
Xử lý thông minh các trường dữ liệu động thông qua metadata_info.
"""

import json
import os
from sqlalchemy.orm import Session
from sqlalchemy.dialects.sqlite import insert
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
        """Tách các trường không có trong Schema để đẩy vào metadata_info."""
        main_columns = model.__table__.columns.keys()
        main_data = {}
        metadata = {}

        for key, value in data.items():
            if key in main_columns:
                main_data[key] = value
            else:
                metadata[key] = value
        
        if "metadata_info" in main_columns:
            main_data["metadata_info"] = metadata
            
        return main_data

    def ingest_json(self, db: Session, target_type: str, file_path: str):
        """Nạp dữ liệu từ JSON vào Database theo cơ chế Upsert."""
        if not os.path.exists(file_path):
            print(f"⚠️ Warning: Missing {file_path}")
            return

        model = self.model_map.get(target_type)
        with open(file_path, 'r', encoding='utf-8') as f:
            records = json.load(f)

        for record in records:
            clean_data = self._extract_metadata(model, record)
            stmt = insert(model).values(**clean_data)
            # Nếu trùng ID, thực hiện cập nhật (Update)
            stmt = stmt.on_conflict_do_update(index_elements=['id'], set_=clean_data)
            db.execute(stmt)
        
        db.commit()
        print(f"✅ Ingested {len(records)} records into {target_type.upper()}.")

ingestion_service = DataIngestionService()