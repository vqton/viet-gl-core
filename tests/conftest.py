"""
PATH: D:/TT99ACCT/tests/conftest.py
ROLE: Cấu hình môi trường Test Suite
"""

import pytest
import os


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    # PM: Đảm bảo các thư mục data tồn tại trước khi test
    os.makedirs("data/db", exist_ok=True)
    os.makedirs("data/master_data", exist_ok=True)
    yield
    # Có thể thêm logic dọn dẹp sau khi test xong tại đây
