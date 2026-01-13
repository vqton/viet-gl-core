"""
PATH: D:/TT99ACCT/source/database/models/__init__.py
MANIFEST: Khai báo toàn bộ các Model trong hệ thống
"""

# Import các Model từ các phân hệ Modular
from .entities import EntityModel
from .accounting import VoucherHeaderModel, JournalEntryModel

# Danh sách Export chuẩn để storage.py hoặc các module báo cáo sử dụng
# Khi bạn thêm bảng thứ 100, hãy nhớ khai báo thêm tên Class vào list này
__all__ = ["EntityModel", "VoucherHeaderModel", "JournalEntryModel"]
