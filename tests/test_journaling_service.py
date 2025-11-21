# File: tests/test_journaling_service.py

import unittest
from unittest.mock import Mock
from decimal import Decimal
from datetime import date
from app.application.services.journaling_service import JournalingService
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine
from app.domain.models.account import TaiKhoan, LoaiTaiKhoan
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.infrastructure.repositories.account_repository import AccountRepository

class TestJournalingService(unittest.TestCase):

    def setUp(self):
        self.mock_je_repo = Mock()
        self.mock_acc_repo = Mock()
        self.service = JournalingService(repository=self.mock_je_repo, account_repository=self.mock_acc_repo)

    def test_tao_phieu_ke_toan_thanh_cong(self):
        """Test tạo bút toán thành công."""
        tai_khoan_131 = TaiKhoan(so_tai_khoan="131", ten_tai_khoan="Phải thu của khách hàng", loai_tai_khoan=LoaiTaiKhoan.TAI_SAN, cap_tai_khoan=1)
        tai_khoan_111 = TaiKhoan(so_tai_khoan="111", ten_tai_khoan="Tiền mặt", loai_tai_khoan=LoaiTaiKhoan.TAI_SAN, cap_tai_khoan=1)

        # Mock repo trả về tài khoản tồn tại
        self.mock_acc_repo.get_by_id.side_effect = lambda x: {
            "131": tai_khoan_131,
            "111": tai_khoan_111,
        }.get(x)

        # Mock repo.add trả về chính bút toán đầu vào
        self.mock_je_repo.add = Mock(return_value=JournalEntry(
            ngay_ct=date.today(),
            so_phieu="PT001",
            mo_ta="Bán hàng",
            lines=[JournalEntryLine(so_tai_khoan="131", no=Decimal('100'), co=Decimal('0'))],
            trang_thai="Posted"
        ))

        journal_entry = JournalEntry(
            ngay_ct=date.today(),
            so_phieu="PT001",
            mo_ta="Bán hàng",
            lines=[JournalEntryLine(so_tai_khoan="131", no=Decimal('100'), co=Decimal('0'))],
            trang_thai="Draft"
        )

        result = self.service.tao_phieu_ke_toan(journal_entry)

        self.assertEqual(result.so_phieu, "PT001")
        self.assertEqual(result.lines[0].no, Decimal('100'))
        self.mock_je_repo.add.assert_called_once()

    def test_tao_phieu_ke_toan_that_bai_vi_tai_khoan_khong_ton_tai(self):
        """Test tạo bút toán thất bại khi tài khoản không tồn tại."""
        journal_entry = JournalEntry(
            ngay_ct=date.today(),
            so_phieu="PT002",
            mo_ta="Mua hàng",
            lines=[JournalEntryLine(so_tai_khoan="999", no=Decimal('50'), co=Decimal('0'))], # Tài khoản không tồn tại
            trang_thai="Draft"
        )

        with self.assertRaises(ValueError) as context:
            self.service.tao_phieu_ke_toan(journal_entry)

        self.assertIn("Tài khoản '999' không tồn tại", str(context.exception))

    def test_ket_chuyen_cuoi_ky_don_gian(self):
        """
        Test kết chuyển cuối kỳ với dữ liệu giả lập đơn giản.
        Doanh thu: 511 = Có 1000
        Chi phí: 632 = Nợ 400
        -> Kết chuyển DT: Nợ 911 1000, Có 511 1000
        -> Kết chuyển CP: Nợ 632 400, Có 911 400
        -> SD 911 sau kết chuyển DT/CP: Nợ 1000 - Có 400 = Nợ 600
        -> Kết chuyển KQKD (lợi nhuận): Ghi Có 911 600, Ghi Nợ 421 600.
        """
        ky_hieu = "Năm 2025"
        ngay_ket_chuyen = date.today()

        # Dữ liệu giả lập: Các bút toán đã "Posted" trong kỳ
        entries_trong_ky = [
            JournalEntry(
                id=1,
                ngay_ct=date.today(),
                so_phieu="BH001",
                mo_ta="Bán hàng",
                lines=[
                    JournalEntryLine(so_tai_khoan="131", no=Decimal('1000'), co=Decimal('0')),
                    JournalEntryLine(so_tai_khoan="511", no=Decimal('0'), co=Decimal('1000')),
                ],
                trang_thai="Posted"
            ),
            JournalEntry(
                id=2,
                ngay_ct=date.today(),
                so_phieu="CP001",
                mo_ta="Chi phí hàng bán",
                lines=[
                    JournalEntryLine(so_tai_khoan="632", no=Decimal('400'), co=Decimal('0')),
                    JournalEntryLine(so_tai_khoan="111", no=Decimal('0'), co=Decimal('400')),
                ],
                trang_thai="Posted"
            )
        ]
        self.mock_je_repo.get_all.return_value = entries_trong_ky

        # Dữ liệu giả lập: Thông tin tài khoản
        tai_khoan_511 = TaiKhoan(so_tai_khoan="511", ten_tai_khoan="Doanh thu bán hàng", loai_tai_khoan=LoaiTaiKhoan.DOANH_THU, cap_tai_khoan=1)
        tai_khoan_632 = TaiKhoan(so_tai_khoan="632", ten_tai_khoan="Giá vốn hàng bán", loai_tai_khoan=LoaiTaiKhoan.CHI_PHI, cap_tai_khoan=1)
        tai_khoan_911 = TaiKhoan(so_tai_khoan="911", ten_tai_khoan="Xác định kết quả kinh doanh", loai_tai_khoan=LoaiTaiKhoan.KHAC, cap_tai_khoan=1) # LoaiTaiKhoan.KHAC là hợp lý cho 911
        tai_khoan_421 = TaiKhoan(so_tai_khoan="421", ten_tai_khoan="Lợi nhuận sau thuế chưa phân phối", loai_tai_khoan=LoaiTaiKhoan.VON_CHU_SO_HUU, cap_tai_khoan=1)

        self.mock_acc_repo.get_by_id.side_effect = lambda x: {
            "511": tai_khoan_511,
            "632": tai_khoan_632,
            "911": tai_khoan_911,
            "421": tai_khoan_421,
            # Thêm các tài khoản khác nếu cần từ entries_trong_ky
            "131": TaiKhoan(so_tai_khoan="131", ten_tai_khoan="Phải thu của khách hàng", loai_tai_khoan=LoaiTaiKhoan.TAI_SAN, cap_tai_khoan=1),
            "111": TaiKhoan(so_tai_khoan="111", ten_tai_khoan="Tiền mặt", loai_tai_khoan=LoaiTaiKhoan.TAI_SAN, cap_tai_khoan=1),
        }.get(x)

        # Mock repo.add để kiểm tra các bút toán kết chuyển được tạo
        self.mock_je_repo.add.side_effect = lambda x: x # Trả về chính đối tượng được gọi add

        # Gọi phương thức kết chuyển
        ket_qua = self.service.ket_chuyen_cuoi_ky(ky_hieu, ngay_ket_chuyen)

        # Kiểm tra số lượng bút toán kết chuyển được tạo
        # Có 3 loại kết chuyển: DT, CP, KQKD -> 3 bút toán
        self.assertEqual(len(ket_qua), 3)

        # Kiểm tra nội dung bút toán kết chuyển doanh thu
        buoc_toan_dt = None
        buoc_toan_cp = None
        buoc_toan_kqkd = None
        for bt in ket_qua:
            if "DOANH-THU" in bt.so_phieu:
                buoc_toan_dt = bt
            elif "CHI-PHI" in bt.so_phieu:
                buoc_toan_cp = bt
            elif "KQKD" in bt.so_phieu:
                buoc_toan_kqkd = bt

        self.assertIsNotNone(buoc_toan_dt)
        self.assertIsNotNone(buoc_toan_cp)
        self.assertIsNotNone(buoc_toan_kqkd)

        # Kiểm tra bút toán kết chuyển doanh thu (Nợ 911, Có 511)
        self.assertEqual(len(buoc_toan_dt.lines), 2)
        self.assertEqual(buoc_toan_dt.lines[0].so_tai_khoan, "911")
        self.assertEqual(buoc_toan_dt.lines[0].no, Decimal('1000'))
        self.assertEqual(buoc_toan_dt.lines[1].so_tai_khoan, "511")
        self.assertEqual(buoc_toan_dt.lines[1].co, Decimal('1000'))

        # Kiểm tra bút toán kết chuyển chi phí (Nợ 632, Có 911)
        self.assertEqual(len(buoc_toan_cp.lines), 2)
        self.assertEqual(buoc_toan_cp.lines[0].so_tai_khoan, "632")
        self.assertEqual(buoc_toan_cp.lines[0].no, Decimal('400'))
        self.assertEqual(buoc_toan_cp.lines[1].so_tai_khoan, "911")
        self.assertEqual(buoc_toan_cp.lines[1].co, Decimal('400'))

        # Kiểm tra bút toán kết chuyển KQKD (Lợi nhuận: Ghi Có 911, Ghi Nợ 421 - vì lợi nhuận = 1000 - 400 = 600)
        self.assertEqual(len(buoc_toan_kqkd.lines), 2)
        # Dòng đầu tiên: Ghi Có 911 (để kết chuyển số dư Nợ của 911 sau khi DT-CP)
        self.assertEqual(buoc_toan_kqkd.lines[0].so_tai_khoan, "911")
        self.assertEqual(buoc_toan_kqkd.lines[0].no, Decimal('0')) # Sai trước đây: Đúng là 0 vì là ghi Có
        self.assertEqual(buoc_toan_kqkd.lines[0].co, Decimal('600')) # Sai trước đây: Thêm kiểm tra này
        # Dòng thứ hai: Ghi Nợ 421 (lợi nhuận làm tăng VCSH)
        self.assertEqual(buoc_toan_kqkd.lines[1].so_tai_khoan, "421")
        self.assertEqual(buoc_toan_kqkd.lines[1].no, Decimal('600')) # Sai trước đây: Thêm kiểm tra này
        self.assertEqual(buoc_toan_kqkd.lines[1].co, Decimal('0')) # Sai trước đây: Thêm kiểm tra này


if __name__ == '__main__':
    unittest.main()