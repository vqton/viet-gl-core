"""
PATH: source/services/sync_service.py
STATUS: Production-ready
REVISION: 
    - Chuyển đổi sang kiến trúc Multi-Domain Master Data.
    - Tích hợp nạp đồng thời Accounts và Entities.
DESCRIPTION: 
    Hệ thống nạp dữ liệu tập trung (Master Data Hub).
    Đảm bảo làm sạch dữ liệu (Cleansing) và bảo vệ giao dịch (Atomicity).
"""

import json
import os
from typing import Type, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select
from pydantic import ValidationError

from ..database.base import Base
from ..database.models.master_data import AccountModel
from ..database.models.entities import EntityModel
from ..schemas.master_schemas import AccountJSONSchema, EntityJSONSchema

class SyncService:
    def __init__(self, db: Session):
        self.db = db

    def sync_all_master_data(self, data_map: Dict[str, str]):
        """
        Nạp đồng thời nhiều loại danh mục.
        data_map: {'accounts': 'path/to/acc.json', 'entities': 'path/to/ent.json'}
        """
        print("--- [START GLOBAL SYNC SESSION] ---")
        try:
            # 1. Nạp Accounts (Xử lý cấu trúc cây đặc thù)
            if 'accounts' in data_map:
                self._sync_domain(
                    file_path=data_map['accounts'],
                    model_class=AccountModel,
                    schema_class=AccountJSONSchema,
                    domain_name="Accounts"
                )
                self._update_account_hierarchy()

            # 2. Nạp Entities (Đối tượng KH, NCC)
            if 'entities' in data_map:
                self._sync_domain(
                    file_path=data_map['entities'],
                    model_class=EntityModel,
                    schema_class=EntityJSONSchema,
                    domain_name="Entities"
                )

            self.db.commit()
            print("--- [GLOBAL SYNC COMPLETED SUCCESSFULLY] ---")
        except Exception as e:
            self.db.rollback()
            print(f"--- [GLOBAL SYNC FAILED] Critical Error: {str(e)} ---")
            raise e

    def _sync_domain(self, file_path: str, model_class: Type[Base], schema_class: Any, domain_name: str):
        """Hàm nạp dữ liệu Generic cho các danh mục phẳng"""
        if not os.path.exists(file_path):
            print(f"[SKIP] {domain_name}: File not found at {file_path}")
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        print(f"[INFO] Syncing {domain_name}: {len(raw_data)} records...")

        for item in raw_data:
            try:
                # MDM Step 1: Validation & Cleansing bằng Pydantic
                valid_data = schema_class(**item)
                data_dict = valid_data.dict()

                # MDM Step 2: Upsert logic (Dựa trên Primary Key 'id')
                stmt = select(model_class).filter(model_class.id == data_dict['id'])
                existing_record = self.db.execute(stmt).scalar_one_or_none()

                if existing_record:
                    # Cập nhật các trường dữ liệu (trừ ID)
                    for key, value in data_dict.items():
                        setattr(existing_record, key, value)
                else:
                    # Thêm mới
                    new_record = model_class(**data_dict)
                    self.db.add(new_record)

            except ValidationError as ve:
                print(f"[ERROR] {domain_name} ID {item.get('id')}: Validation failed. {ve.json()}")
                raise ve

    def _update_account_hierarchy(self):
        """
        Logic đặc thù cho tài khoản: Tự động tính level và is_leaf.
        Đây là bước xử lý hậu kỳ (Post-processing) sau khi đã nạp thô.
        """
        print("[INFO] Accounts: Re-calculating hierarchy (is_leaf, level)...")
        self.db.flush()
        all_accs = self.db.query(AccountModel).all()
        parent_ids = {a.parent_id for a in all_accs if a.parent_id}

        for acc in all_accs:
            acc.is_leaf = acc.id not in parent_ids
            # Logic tính Level nhanh
            depth = 1
            curr_parent = acc.parent_id
            while curr_parent:
                depth += 1
                parent_obj = next((p for p in all_accs if p.id == curr_parent), None)
                curr_parent = parent_obj.parent_id if parent_obj else None
            acc.level = depth