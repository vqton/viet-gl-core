# File: tests/test_tai_khoan_service.py

import unittest
from unittest.mock import Mock # Để giả lập Repository
from app.application.services.tai_khoan_service import TaiKhoanService
from app.domain.models.account import TaiKhoan, LoaiTaiKhoan

class TestTaiKhoanService(unittest.TestCase):

    def setUp(self):
        # Giả lập Repository
        self.mock_repository = Mock()
        self.service = TaiKhoanService(repository=self.mock_repository)

    def test_tao_tai_khoan_thanh_cong(self):
        """Test tạo tài khoản thành công."""
        tai_khoan_moi = TaiKhoan(so_tai_khoan="111", ten_tai_khoan="Tiền mặt", loai_tai_khoan=LoaiTaiKhoan.TAI_SAN)
        
        # Cấu hình mock
        self.mock_repository.add.return_value = tai_khoan_moi
        
        result = self.service.tao_tai_khoan(tai_khoan_moi)
        
        # Kiểm tra
        self.assertEqual(result.so_tai_khoan, "111")
        self.mock_repository.add.assert_called_once_with(tai_khoan_moi)

    def test_tao_tai_khoan_cap_con_ma_cha_khong_ton_tai(self):
        """Test tạo tài khoản cấp con thất bại nếu tài khoản cha không tồn tại."""
        tai_khoan_con = TaiKhoan(
            so_tai_khoan="1111",
            ten_tai_khoan="Tiền mặt - Chi nhánh A",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
            cap_tai_khoan=2,
            so_tai_khoan_cha="999" # Mã cha không tồn tại
        )
        
        # Cấu hình mock: get_by_id trả về None
        self.mock_repository.get_by_id.return_value = None
        
        with self.assertRaises(ValueError) as context:
            self.service.tao_tai_khoan(tai_khoan_con)
            
        self.assertIn("Tài khoản cha '999' không tồn tại.", str(context.exception))