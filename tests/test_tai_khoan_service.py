# tests/test_tai_khoan_service.py

import unittest
from unittest.mock import Mock

from app.application.services.tai_khoan_service import TaiKhoanService
from app.domain.models.account import LoaiTaiKhoan, TaiKhoan


class TestTaiKhoanService(unittest.TestCase):

    def setUp(self):
        self.mock_repository = Mock()
        self.service = TaiKhoanService(repository=self.mock_repository)

    def test_tao_tai_khoan_thanh_cong(self):
        """Test tạo tài khoản cấp 1 thành công."""
        tai_khoan = TaiKhoan(
            so_tai_khoan="11311",
            ten_tai_khoan="Tiền gửi ngân hàng",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
            cap_tai_khoan=1,
            so_tai_khoan_cha=None,
            la_tai_khoan_tong_hop=True,
        )

        # 👇 MOCK: get_by_id -> None (chưa tồn tại), add -> trả về chính tai_khoan
        self.mock_repository.get_by_id.return_value = None
        self.mock_repository.add.return_value = (
            tai_khoan  # ← DÒNG NÀY LÀ CHÌA KHÓA
        )

        ket_qua = self.service.tao_tai_khoan(tai_khoan)

        self.mock_repository.add.assert_called_once_with(tai_khoan)
        self.assertEqual(ket_qua, tai_khoan)  # ✅ Bây giờ sẽ pass

    def test_tao_tai_khoan_cap_con_ma_cha_khong_ton_tai(self):
        """Test tạo tài khoản cấp con thất bại nếu tài khoản cha không tồn tại."""
        tai_khoan_con = TaiKhoan(
            so_tai_khoan="1111",
            ten_tai_khoan="Tiền mặt - Chi nhánh A",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
            cap_tai_khoan=2,
            so_tai_khoan_cha="999",
        )

        self.mock_repository.get_by_id.return_value = None

        with self.assertRaises(ValueError) as context:
            self.service.tao_tai_khoan(tai_khoan_con)

        self.assertIn(
            "Tài khoản cha '999' không tồn tại.", str(context.exception)
        )

    def test_tao_tai_khoan_that_bai_do_trung_so(self):
        """Test không tạo được nếu số tài khoản đã tồn tại."""
        tai_khoan = TaiKhoan(
            so_tai_khoan="11311",
            ten_tai_khoan="Tiền gửi",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
            cap_tai_khoan=1,
        )

        # Giả lập: tài khoản đã tồn tại
        self.mock_repository.get_by_id.return_value = tai_khoan

        with self.assertRaises(ValueError) as context:
            self.service.tao_tai_khoan(tai_khoan)

        self.assertIn(
            "Số tài khoản '11311' đã tồn tại.", str(context.exception)
        )
