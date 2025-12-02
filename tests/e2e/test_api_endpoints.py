# tests/e2e/test_api_endpoints.py
"""
End-to-end tests cho các API endpoint kế toán

📋 TT99/2025/TT-BTC:
- Điều 8–10: Chứng từ gốc
- Điều 24: Ghi sổ kép
"""
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.application.services.tai_khoan_service import TaiKhoanService
from app.domain.models.account import LoaiTaiKhoan, TaiKhoan
from app.main import app


@pytest.fixture
def client_with_mock_service():
    from app.application.services.tai_khoan_service import TaiKhoanService
    from app.main import app
    from app.presentation.api.v1.accounting.dependencies import (
        get_tai_khoan_service,
    )

    mock_service = MagicMock()
    # 👇 Override đúng function được inject vào route
    app.dependency_overrides[get_tai_khoan_service] = lambda: mock_service

    with TestClient(app) as client:
        yield client, mock_service

    app.dependency_overrides.clear()


def test_create_account_success(client_with_mock_service):
    client, mock_service = client_with_mock_service

    payload = {
        "so_tai_khoan": "11311",
        "ten_tai_khoan": "Tiền gửi ngân hàng",
        "loai_tai_khoan": "TAI_SAN",
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    }

    fake_account = TaiKhoan(
        so_tai_khoan="11311",
        ten_tai_khoan="Tiền gửi ngân hàng",
        loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
        cap_tai_khoan=1,
        so_tai_khoan_cha=None,
        la_tai_khoan_tong_hop=True,
    )

    mock_service.tao_tai_khoan.return_value = fake_account

    response = client.post("/accounting/v1/accounts/", json=payload)

    # 👇 DEBUG: In lỗi chi tiết nếu có
    if response.status_code != 201:
        print("DEBUG RESPONSE:", response.json())

    assert response.status_code == 201
    data = response.json()
    assert data["so_tai_khoan"] == "11311"

    mock_service.tao_tai_khoan.assert_called_once()


def test_create_account_duplicate_fails(client_with_mock_service):
    """[TT99-PL2] Không được tạo tài khoản trùng số."""
    client, mock_service = client_with_mock_service

    payload = {
        "so_tai_khoan": "11211",
        "ten_tai_khoan": "TK trùng",
        "loai_tai_khoan": "TAI_SAN",
        "cap_tai_khoan": 1,
    }

    mock_service.tao_tai_khoan.side_effect = ValueError(
        "Số tài khoản '11211' đã tồn tại."
    )

    response = client.post("/accounting/v1/accounts/", json=payload)

    assert response.status_code == 400
    assert "đã tồn tại" in response.json()["detail"]
