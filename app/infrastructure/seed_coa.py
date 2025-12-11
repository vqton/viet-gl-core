# app/infrastructure/seed_coa.py
import logging
import os
from pathlib import Path

from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def seed_coa_from_sql(engine: Engine):
    sql_file = (
        Path(__file__).parent / "coa_seed_scripts" / "seed_coa_tt99_full.sql"
    )

    if not os.path.exists(sql_file):  # ← SỬA: sql_file, không phải sql_build
        raise FileNotFoundError(
            f"❌ File SQL seeding không tồn tại: {sql_file}"
        )

    logging.info(f"📖 Đang đọc file SQL: {sql_file}")
    with open(sql_file, "r", encoding="utf-8") as f:
        sql_content = f.read()

    logging.info("⚙️  Đang thực thi script SQL seeding...")
    try:
        with engine.connect() as conn:
            conn = conn.execution_options(autocommit=True)
            conn.execute(text(sql_content))
        logging.info("✅ Seeding COA từ SQL thành công.")
    except SQLAlchemyError as e:
        logging.error(f"❌ Lỗi cơ sở dữ liệu: {e}")
        raise
    except Exception as e:
        logging.error(f"💥 Lỗi không mong đợi: {e}")
        raise


if __name__ == "__main__":
    from app.infrastructure.database import engine

    seed_coa_from_sql(engine)
