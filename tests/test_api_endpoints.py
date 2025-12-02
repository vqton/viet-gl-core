# tests/test_api.py
import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_journal_entry_with_document():
    """
    [TT99-Đ8-10] Bút toán phải có chứng từ gốc khi ghi sổ.
    """
    payload = {
        "so_phieu": "PT-001",
        "ngay_ct": "2025-06-15",
        "mo_ta": "Bán hàng",
        "lines": [
            {
                "so_tai_khoan": "111",
                "no": "110000000",
                "co": "0",
                "so_chung_tu_goc": "HD-2025-001",  # ✅ Bắt buộc
                "ngay_chung_tu_goc": "2025-06-15",  # ✅ Bắt buộc
            },
            {"so_tai_khoan": "511", "no": "0", "co": "100000000"},
            {"so_tai_khoan": "3331", "no": "0", "co": "10000000"},
        ],
        "trang_thai": "Draft",
    }

    response = client.post("/accounting/v1/journal-entries/", json=payload)
    assert response.status_code == 201
