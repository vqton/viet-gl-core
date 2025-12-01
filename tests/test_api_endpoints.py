from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from app.domain.models.account import LoaiTaiKhoan, TaiKhoan
from app.main import app

client = TestClient(app)


class TestAccountingAPI:
    """Test các endpoint API kế toán."""

    def test_create_account_success(self):
        # 1. Tạo dữ liệu giả mà bạn muốn Repository trả về (không cần ghi DB)
        fake_account = TaiKhoan(
            so_tai_khoan="99999", 
            ten_tai_khoan="Tiền gửi ngân hàng", 
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN, 
            cap_tai_khoan=1
        )

        # 2. Sử dụng PATCH để chặn đường gọi vào hàm 'add' của Repository
        # LƯU Ý: Đường dẫn trong patch() phải trỏ tới nơi Repository được IMPORT/SỬ DỤNG, 
        # không phải nơi nó được định nghĩa. Ví dụ: 'app.api.endpoints.accounting.account_repository'
        
        # Giả sử bạn đang dùng Dependency Injection, ta có thể override dependency của FastAPI:
        from app.main import app # Import app FastAPI của bạn
        from app.infrastructure.repositories.account_repository import AccountRepository
        
        # Tạo Mock Repository
        mock_repo = MagicMock()
        mock_repo.add.return_value = fake_account # Giả vờ add thành công và trả về object
        mock_repo.get_by_id.return_value = None   # Giả vờ tài khoản chưa tồn tại
        
        # Override dependency: Bất cứ khi nào API cần AccountRepository, hãy đưa cái Mock này
        app.dependency_overrides[AccountRepository] = lambda: mock_repo

        # 3. Gọi API như bình thường
        response = client.post("/accounting/v1/accounts/", json={
            "so_tai_khoan": "11311", # Số này trùng cũng không sao vì ta đã Mock
            "ten_tai_khoan": "Tiền gửi ngân hàng",
            "loai_tai_khoan": "TAI_SAN",
            "cap_tai_khoan": 1
        })

        # 4. Dọn dẹp override sau khi test xong
        app.dependency_overrides = {}

        # 5. Kiểm tra kết quả
        assert response.status_code in (200, 201)
        # Kiểm tra xem hàm add của repo giả có được gọi không
        mock_repo.add.assert_called_once()

    def test_create_account_invalid_data(self):
        """Test tạo tài khoản với dữ liệu sai (số tài khoản trống)."""
        response = client.post("/accounting/v1/accounts/", json={
            "so_tai_khoan": "",
            "ten_tai_khoan": "Tên không hợp lệ",
            "loai_tai_khoan": "Tai_San"
        })
        # FastAPI (Pydantic) sẽ trả về 422 cho dữ liệu không hợp lệ
        assert response.status_code == 422