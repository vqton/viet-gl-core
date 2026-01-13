"""
PATH: D:/TT99ACCT/source/database/storage.py
AUTH: PM & CFO
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import StaleDataError

# Thay vì: from .base import Base
from source.database.base import Base

# Thay vì: from .models import ...
from source.database.models import EntityModel, VoucherHeaderModel, JournalEntryModel
import os
from datetime import datetime


class AccountingStorage:
    def __init__(self, current_user="SYSTEM_ADMIN"):
        base_dir = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        db_path = os.path.join(base_dir, "data", "db", "tt99_finance.db")

        # 1. Khởi tạo Engine (Hỗ trợ SQLite Foreign Keys)
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)

        # Kích hoạt Foreign Key Constraint cho SQLite (Mặc định nó tắt)
        from sqlalchemy import event

        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

        # 2. Tạo bảng tự động (Modular)
        Base.metadata.create_all(self.engine)

        # 3. Cấu hình Session Factory
        self.Session = sessionmaker(bind=self.engine)
        self.current_user = current_user

    def add_entity(self, entity_id, name, tax_code=None, e_type="KH", **kwargs):
        """Thêm đối tượng với đầy đủ Audit Columns"""
        session = self.Session()
        try:
            new_entity = EntityModel(
                entity_id=entity_id,
                name=name,
                tax_code=tax_code,
                entity_type=e_type,
                created_by=self.current_user,
                updated_by=self.current_user,
                **kwargs,
            )
            session.add(new_entity)
            session.commit()
            return True, f"Entity {entity_id} created."
        except Exception as e:
            session.rollback()
            return False, f"Database Error: {str(e)}"
        finally:
            session.close()

    def save_transaction(self, v_type, v_no, date_at, description, entries_data):
        """
        Ghi sổ chứng từ phức tạp (Atomic Transaction)
        entries_data: List các dict/object chứa {account_id, debit, credit, entity_id, description}
        """
        session = self.Session()
        v_id = f"{v_type}-{v_no}-{date_at.strftime('%Y%m%d') if isinstance(date_at, datetime) else date_at}"

        try:
            # Tạo Header
            header = VoucherHeaderModel(
                v_id=v_id,
                v_type=v_type,
                v_no=v_no,
                date_at=date_at,
                description=description,
                created_by=self.current_user,
                updated_by=self.current_user,
            )

            # Add các dòng định khoản
            for data in entries_data:
                entry = JournalEntryModel(
                    account_id=data.get("account_id"),
                    entity_id=data.get("entity_id"),
                    description=data.get("description", description),
                    debit=data.get("debit", 0),
                    credit=data.get("credit", 0),
                    created_by=self.current_user,
                    updated_by=self.current_user,
                )
                header.entries.append(entry)

            session.add(header)
            session.commit()
            return True, f"Voucher {v_no} posted successfully."

        except StaleDataError:
            session.rollback()
            return (
                False,
                "ERROR: Xung đột dữ liệu (Version Conflict). Người khác đã sửa chứng từ này!",
            )
        except Exception as e:
            session.rollback()
            return False, f"Transaction Failed: {str(e)}"
        finally:
            session.close()


# Khởi tạo instance mặc định
DB_STORAGE = AccountingStorage()
