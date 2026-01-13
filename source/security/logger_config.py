"""
PROJECT: TT99ACCT
MODULE: SECURITY - LOGGER CONFIG
DESCRIPTION: Cấu hình hệ thống ghi nhật ký tập trung cho toàn bộ ứng dụng.
"""

import logging
import os
from datetime import datetime

# Xác định đường dẫn folder logs (trỏ về D:/TT99ACCT/logs)
LOG_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "../../../logs"))
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logger(name: str):
    """Cấu hình logger ghi cả ra Console và File."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Định dạng log: Thời gian - Tên module - Mức độ - Nội dung
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # 1. File Handler: Lưu log vào file theo ngày
    log_file = os.path.join(LOG_DIR, f"system_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 2. Console Handler: Hiển thị ra màn hình để Dev theo dõi
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# Instance logger mặc định cho hệ thống
logger = setup_logger("TT99_FINANCE")
