"""
Cấu hình pytest cho toàn bộ test suite.

Mục đích:
- Tự động thêm thư mục gốc vào Python path
- Đảm bảo import module thành công từ src.domain

Yêu cầu kỹ thuật:
- Không chứa logic nghiệp vụ
- Chỉ hỗ trợ môi trường test
"""

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))
