# File: tests/test_api_endpoints.py

import unittest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAccountingAPI(unittest.TestCase):

    def test_create_account_success(self):
        """Test tạo tài khoản mới qua API."""
        response = client.post("/accounting/accounts/", json={
            "so_tai_khoan": "112",
            "ten_tai_khoan": "Tiền gửi ngân hàng",
            "loai_tai_khoan": "Tai_San",
            "cap_tai_khoan": 1
        })
        if response.status_code != 200:
            print(f"Error creating account: {response.status_code}, Detail: {response.text}") # Thêm dòng này
        assert response.status_code == 200
        data = response.json()
        assert data["so_tai_khoan"] == "112"
        assert data["ten_tai_khoan"] == "Tiền gửi ngân hàng"

    def test_create_account_invalid_data(self):
        """Test tạo tài khoản với dữ liệu sai (số tài khoản trống)."""
        response = client.post("/accounting/accounts/", json={
            "so_tai_khoan": "",
            "ten_tai_khoan": "Tên không hợp lệ",
            "loai_tai_khoan": "Tai_San"
        })
        assert response.status_code == 422
        # Kiểm tra message lỗi
        assert "Số tài khoản không được để trống" in response.text