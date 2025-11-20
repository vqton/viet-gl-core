# File: tests/test_account.py
import unittest
from app.domain.models.account import TaiKhoan, LoaiTaiKhoan
from dataclasses import dataclass

class TestTaiKhoan(unittest.TestCase):
    """
    Unit tests cho Entity Domain TaiKhoan.
    """

    def test_khoi_tao_thanh_cong_cap_1(self):
        """
        Test khởi tạo tài khoản cấp 1 thành công.
        """
        tai_khoan = TaiKhoan(
            so_tai_khoan="111",
            ten_tai_khoan="Tiền mặt",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
            cap_tai_khoan=1,
            la_tai_khoan_tong_hop=True
        )
        self.assertEqual(tai_khoan.so_tai_khoan, "111")
        self.assertEqual(tai_khoan.ten_tai_khoan, "Tiền mặt")
        self.assertEqual(tai_khoan.loai_tai_khoan, LoaiTaiKhoan.TAI_SAN)
        self.assertEqual(tai_khoan.cap_tai_khoan, 1)
        self.assertTrue(tai_khoan.la_tai_khoan_tong_hop)
        self.assertIsNone(tai_khoan.so_tai_khoan_cha)

    def test_khoi_tao_thanh_cong_cap_2_co_cha(self):
        """
        Test khởi tạo tài khoản cấp 2 có tài khoản cha thành công.
        """
        tai_khoan = TaiKhoan(
            so_tai_khoan="1331",
            ten_tai_khoan="Thuế GTGT được khấu trừ",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
            cap_tai_khoan=2,
            so_tai_khoan_cha="133",
            la_tai_khoan_tong_hop=False
        )
        self.assertEqual(tai_khoan.so_tai_khoan, "1331")
        self.assertEqual(tai_khoan.so_tai_khoan_cha, "133")

    def test_so_tai_khoan_trong(self):
        """
        Test khởi tạo thất bại khi so_tai_khoan trống.
        """
        with self.assertRaises(ValueError) as context:
            TaiKhoan(
                so_tai_khoan="", # Trống
                ten_tai_khoan="Một tài khoản",
                loai_tai_khoan=LoaiTaiKhoan.NO_PHAI_TRA,
                cap_tai_khoan=1
            )
        self.assertIn("Số tài khoản không được để trống", str(context.exception))

    def test_ten_tai_khoan_trong(self):
        """
        Test khởi tạo thất bại khi ten_tai_khoan trống.
        """
        with self.assertRaises(ValueError) as context:
            TaiKhoan(
                so_tai_khoan="123",
                ten_tai_khoan="", # Trống
                loai_tai_khoan=LoaiTaiKhoan.NO_PHAI_TRA,
                cap_tai_khoan=1
            )
        self.assertIn("Tên tài khoản không được để trống", str(context.exception))

    def test_cap_tai_khoan_nho_hon_1(self):
        """
        Test khởi tạo thất bại khi cap_tai_khoan < 1.
        """
        with self.assertRaises(ValueError) as context:
            TaiKhoan(
                so_tai_khoan="123",
                ten_tai_khoan="Một tài khoản",
                loai_tai_khoan=LoaiTaiKhoan.NO_PHAI_TRA,
                cap_tai_khoan=0 # Sai
            )
        self.assertIn("Cấp tài khoản phải từ 1 đến 3", str(context.exception))

    def test_cap_tai_khoan_lon_hon_3(self):
        """
        Test khởi tạo thất bại khi cap_tai_khoan > 3.
        """
        with self.assertRaises(ValueError) as context:
            TaiKhoan(
                so_tai_khoan="123",
                ten_tai_khoan="Một tài khoản",
                loai_tai_khoan=LoaiTaiKhoan.NO_PHAI_TRA,
                cap_tai_khoan=4 # Sai
            )
        self.assertIn("Cấp tài khoản phải từ 1 đến 3", str(context.exception))

    def test_cap_2_khong_co_cha(self):
        """
        Test khởi tạo thất bại khi cap_tai_khoan > 1 nhưng so_tai_khoan_cha là None hoặc trống.
        """
        with self.assertRaises(ValueError) as context:
            TaiKhoan(
                so_tai_khoan="1234", # Cấp 2 hoặc 3
                ten_tai_khoan="Một tài khoản cấp con",
                loai_tai_khoan=LoaiTaiKhoan.CHI_PHI,
                cap_tai_khoan=2, # Cấp 2
                so_tai_khoan_cha=None # Thiếu cha
            )
        self.assertIn("Tài khoản cấp con", str(context.exception))

        with self.assertRaises(ValueError) as context:
            TaiKhoan(
                so_tai_khoan="1235", # Cấp 2 hoặc 3
                ten_tai_khoan="Một tài khoản cấp con khác",
                loai_tai_khoan=LoaiTaiKhoan.CHI_PHI,
                cap_tai_khoan=3, # Cấp 3
                so_tai_khoan_cha="" # Thiếu cha (trống)
            )
        self.assertIn("Tài khoản cấp con", str(context.exception))


if __name__ == '__main__':
    unittest.main()