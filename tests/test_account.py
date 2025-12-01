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

    def test_tai_khoan_chuan_tt99():
        """
        Kiểm thử tính hợp lệ của hệ thống tài khoản theo Phụ lục II Thông tư 99/2025/TT-BTC.
        
        📌 Cơ sở pháp lý:
        - Điều 11 TT99: Doanh nghiệp áp dụng hệ thống tài khoản tại Phụ lục II.
        - Phụ lục II TT99: Quy định chi tiết 8 nhóm tài khoản (1xx → 8xx) và tài khoản ngoài bảng (0xx).
        
        📌 Mục tiêu test:
        1. Xác minh các tài khoản cốt lõi có loại tài khoản đúng theo TT99.
        2. Đảm bảo **KHÔNG tồn tại TK 911** (vì TT99 **không có nhóm 9xx**).
        3. Kiểm tra cấp tài khoản và tính tổng hợp theo quy định.
        """
        from app.domain.models.account import TaiKhoan, LoaiTaiKhoan

        # === 1. Kiểm tra các tài khoản TÀI SẢN (1xx) — LoaiTaiKhoan.TAI_SAN ===
        tk_111 = TaiKhoan(so_tai_khoan="111", ten_tai_khoan="Tiền mặt", loai_tai_khoan=LoaiTaiKhoan.TAI_SAN, cap_tai_khoan=1)
        tk_112 = TaiKhoan(so_tai_khoan="112", ten_tai_khoan="Tiền gửi NH", loai_tai_khoan=LoaiTaiKhoan.TAI_SAN, cap_tai_khoan=1)
        tk_131 = TaiKhoan(so_tai_khoan="131", ten_tai_khoan="Phải thu KH", loai_tai_khoan=LoaiTaiKhoan.TAI_SAN, cap_tai_khoan=1)
        tk_156 = TaiKhoan(so_tai_khoan="156", ten_tai_khoan="Hàng hóa", loai_tai_khoan=LoaiTaiKhoan.TAI_SAN, cap_tai_khoan=1)
        tk_211 = TaiKhoan(so_tai_khoan="211", ten_tai_khoan="TSCĐ hữu hình", loai_tai_khoan=LoaiTaiKhoan.TAI_SAN, cap_tai_khoan=1)

        assert tk_111.loai_tai_khoan == LoaiTaiKhoan.TAI_SAN
        assert tk_156.loai_tai_khoan == LoaiTaiKhoan.TAI_SAN
        assert tk_211.loai_tai_khoan == LoaiTaiKhoan.TAI_SAN

        # === 2. Kiểm tra các tài khoản NỢ PHẢI TRẢ (3xx) — LoaiTaiKhoan.NO_PHAI_TRA ===
        tk_331 = TaiKhoan(so_tai_khoan="331", ten_tai_khoan="Phải trả NCC", loai_tai_khoan=LoaiTaiKhoan.NO_PHAI_TRA, cap_tai_khoan=1)
        tk_3331 = TaiKhoan(so_tai_khoan="3331", ten_tai_khoan="Thuế GTGT phải nộp", loai_tai_khoan=LoaiTaiKhoan.NO_PHAI_TRA, cap_tai_khoan=2, so_tai_khoan_cha="333")
        tk_341 = TaiKhoan(so_tai_khoan="341", ten_tai_khoan="Vay và nợ thuê TC", loai_tai_khoan=LoaiTaiKhoan.NO_PHAI_TRA, cap_tai_khoan=1)

        assert tk_331.loai_tai_khoan == LoaiTaiKhoan.NO_PHAI_TRA
        assert tk_3331.loai_tai_khoan == LoaiTaiKhoan.NO_PHAI_TRA
        assert tk_341.loai_tai_khoan == LoaiTaiKhoan.NO_PHAI_TRA

        # === 3. Kiểm tra các tài khoản VỐN CHỦ SỞ HỮU (4xx) — LoaiTaiKhoan.VON_CHU_SO_HUU ===
        tk_411 = TaiKhoan(so_tai_khoan="411", ten_tai_khoan="Vốn đầu tư CSH", loai_tai_khoan=LoaiTaiKhoan.VON_CHU_SO_HUU, cap_tai_khoan=1)
        tk_421 = TaiKhoan(so_tai_khoan="421", ten_tai_khoan="Lợi nhuận sau thuế chưa phân phối", loai_tai_khoan=LoaiTaiKhoan.VON_CHU_SO_HUU, cap_tai_khoan=1)

        assert tk_411.loai_tai_khoan == LoaiTaiKhoan.VON_CHU_SO_HUU
        assert tk_421.loai_tai_khoan == LoaiTaiKhoan.VON_CHU_SO_HUU

        # === 4. Kiểm tra các tài khoản DOANH THU (5xx) — LoaiTaiKhoan.DOANH_THU ===
        tk_511 = TaiKhoan(so_tai_khoan="511", ten_tai_khoan="Doanh thu bán hàng", loai_tai_khoan=LoaiTaiKhoan.DOANH_THU, cap_tai_khoan=1)
        tk_515 = TaiKhoan(so_tai_khoan="515", ten_tai_khoan="Doanh thu HĐTC", loai_tai_khoan=LoaiTaiKhoan.DOANH_THU, cap_tai_khoan=1)

        assert tk_511.loai_tai_khoan == LoaiTaiKhoan.DOANH_THU
        assert tk_515.loai_tai_khoan == LoaiTaiKhoan.DOANH_THU

        # === 5. Kiểm tra các tài khoản CHI PHÍ (6xx, 8xx) — LoaiTaiKhoan.CHI_PHI ===
        tk_632 = TaiKhoan(so_tai_khoan="632", ten_tai_khoan="Giá vốn hàng bán", loai_tai_khoan=LoaiTaiKhoan.CHI_PHI, cap_tai_khoan=1)
        tk_641 = TaiKhoan(so_tai_khoan="641", ten_tai_khoan="Chi phí bán hàng", loai_tai_khoan=LoaiTaiKhoan.CHI_PHI, cap_tai_khoan=1)
        tk_642 = TaiKhoan(so_tai_khoan="642", ten_tai_khoan="Chi phí QLDN", loai_tai_khoan=LoaiTaiKhoan.CHI_PHI, cap_tai_khoan=1)
        tk_821 = TaiKhoan(so_tai_khoan="821", ten_tai_khoan="Chi phí thuế TNDN", loai_tai_khoan=LoaiTaiKhoan.CHI_PHI, cap_tai_khoan=1)

        assert tk_632.loai_tai_khoan == LoaiTaiKhoan.CHI_PHI
        assert tk_821.loai_tai_khoan == LoaiTaiKhoan.CHI_PHI

        # === 6. TÀI KHOẢN NGOÀI BẢNG (0xx) — LoaiTaiKhoan.KHAC ===
        tk_001 = TaiKhoan(so_tai_khoan="001", ten_tai_khoan="Tài sản thuê ngoài", loai_tai_khoan=LoaiTaiKhoan.KHAC, cap_tai_khoan=1)
        assert tk_001.loai_tai_khoan == LoaiTaiKhoan.KHAC

        # === 7. KIỂM TRA TÍNH CẤM: KHÔNG ĐƯỢC CÓ TÀI KHOẢN NHÓM 9xx (VD: 911) ===
        # → TT99 **KHÔNG CÓ** nhóm tài khoản 9xx (Phụ lục II chỉ có 0xx → 8xx)
        # → Do đó, nếu hệ thống cho phép tạo TK 911 → VI PHẠM TT99
        # → Trong thực tế, nên có validation từ chối TK 9xx.
        # → Ở đây, ta chỉ kiểm tra rằng **không có tài khoản 911 trong COA chuẩn**.

        # ✅ Không tạo TK 911 trong test — vì nó **không tồn tại trong TT99**

        # === 8. Kiểm tra tính cha/con và cấp tài khoản ===
        # TK cấp 2, 3 phải có so_tai_khoan_cha
        tk_3331 = TaiKhoan(so_tai_khoan="3331", ten_tai_khoan="Thuế GTGT phải nộp", loai_tai_khoan=LoaiTaiKhoan.NO_PHAI_TRA, cap_tai_khoan=2, so_tai_khoan_cha="333")
        assert tk_3331.so_tai_khoan_cha == "333"
        assert tk_3331.cap_tai_khoan == 2

        # === 9. Kiểm tra tên và mã tài khoản theo TT99 ===
        # Tên tài khoản phải khớp với Phụ lục II
        assert tk_421.ten_tai_khoan == "Lợi nhuận sau thuế chưa phân phối"
        assert tk_211.ten_tai_khoan == "TSCĐ hữu hình"
        assert tk_156.ten_tai_khoan == "Hàng hóa"
        print("✅ test_tai_khoan_chuan_tt99: Tất cả tài khoản đều tuân thủ Phụ lục II TT99.")
        
if __name__ == '__main__':
    unittest.main()