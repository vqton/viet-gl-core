# app/infrastructure/seed_coa.py
import logging
import os
from pathlib import Path
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def seed_coa_from_sql(engine: Engine, sql_file_path: str = None):
    """
    Chèn COA từ file SQL thuần.
    File SQL phải bao gồm:
      - DROP TABLE/TYPE cũ (nếu cần)
      - CREATE TYPE, CREATE TABLE
      - INSERT INTO accounts
    """
    if sql_file_path is None:
        # Tự động tìm file trong thư mục cùng cấp
        sql_file_path = Path(__file__).parent / "coa_seed_scripts" / "seed_coa_tt99_full.sql"

    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(f"SQL seed file không tồn tại: {sql_file_path}")

    logging.info(f"- ĐANG SEED COA TỪ FILE: {sql_file_path} -")
    try:
        with open(sql_file_path, "r", encoding="utf-8") as f:
            sql_commands = f.read()

        # Thực thi toàn bộ SQL (có thể gồm nhiều lệnh)
        with engine.connect() as conn:
            # Bật autocommit cho DDL (CREATE, DROP)
            conn = conn.execution_options(autocommit=True)
            conn.execute(text(sql_commands))

        logging.info("✅ Seeding COA từ SQL thành công.")
    except SQLAlchemyError as e:
        logging.error(f"Lỗi SQLAlchemy khi chạy SQL seed: {e}")
        raise
    except Exception as e:
        logging.error(f"Lỗi không xác định khi đọc/chạy SQL seed: {e}")
        raise

# ———————— DÙNG TRỰC TIẾP KHI CHẠY MODULE ————————
if __name__ == "__main__":
    from app.infrastructure.database import engine
    seed_coa_from_sql(engine)