import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from app.domain.models.account import TaiKhoan, LoaiTaiKhoan
from app.main import app

# ⚠️ QUAN TRỌNG: Import hàm dependency mà Router thực sự sử dụng
# Giả sử hàm này nằm ở app.api.dependencies hoặc nơi bạn định nghĩa nó
# Bạn cần trỏ đúng đường dẫn import của dự án
from app.presentation.api.v1.accounting import get_tai_khoan_service

@pytest.fixture
def client_with_mock_service():
    mock_service = MagicMock()
    
    # ✅ SỬA ĐÚNG: Override hàm get_tai_khoan_service, không phải class TaiKhoanService
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
        "la_tai_khoan_tong_hop": True
    }

    # Mock return value
    fake_account = TaiKhoan(
        so_tai_khoan="11311",
        ten_tai_khoan="Tiền gửi ngân hàng",
        loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
        cap_tai_khoan=1,
        so_tai_khoan_cha=None,
        la_tai_khoan_tong_hop=True
    )
    mock_service.tao_tai_khoan.return_value = fake_account

    response = client.post("/accounting/v1/accounts/", json=payload)

    # Debug: Nếu vẫn lỗi, in nội dung lỗi ra để xem service thật đang báo gì
    if response.status_code != 201:
        print(f"\nDEBUG ERROR RESPONSE: {response.json()}")

    assert response.status_code == 201
    
    data = response.json()
    assert data["so_tai_khoan"] == "11311"
    
    # Kiểm tra mock đã được gọi (Chứng minh override thành công)
    mock_service.tao_tai_khoan.assert_called_once()