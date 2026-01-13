import pytest
import time
import random
from source.services.entity_service import ENTITY_SERVICE


def test_create_entity_success():
    """TC-E01: Tạo mới đối tượng hợp lệ với MST ngẫu nhiên"""
    unique_suffix = int(time.time()) + random.randint(1, 1000)
    status, msg = ENTITY_SERVICE.create_entity(
        entity_id=f"ENT_{unique_suffix}",
        name="TEST SUCCESS",
        tax_code=f"TAX_{unique_suffix}",  # Đảm bảo không bao giờ trùng MST
        e_type="KH",
    )
    assert status is True, f"Nên thành công nhưng lỗi: {msg}"


def test_duplicate_tax_code():
    """TC-E02: Chặn trùng mã số thuế"""
    unique_tax = f"ST_{int(time.time())}"
    # Tạo phát đầu
    ENTITY_SERVICE.create_entity("ID_1", "NAME 1", unique_tax, "KH")
    # Tạo phát hai trùng MST
    status, msg = ENTITY_SERVICE.create_entity("ID_2", "NAME 2", unique_tax, "KH")

    assert status is False
    assert "UNIQUE constraint failed" in msg


def test_entity_id_required():
    """TC-E03: Kiểm tra thông báo lỗi chuẩn Architect đề xuất"""
    status, msg = ENTITY_SERVICE.create_entity(
        entity_id="  ",  # Test khoảng trắng như CFO yêu cầu
        name="LỖI",
        tax_code="123456",
        e_type="KH",
    )
    assert status is False
    assert "entity_id is required" in msg.lower()
