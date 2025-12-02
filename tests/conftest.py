# tests/conftest.py
import sys
from pathlib import Path

# Thêm thư mục gốc (chứa thư mục `app`) vào PYTHONPATH
# Ví dụ: D:\tt99acct\app
project_root = Path(__file__).parent.parent  # Lên 2 cấp: từ tests/ → tt99acct/
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
