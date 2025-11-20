# File: tests/test_journal_entry.py
import unittest
from decimal import Decimal
from datetime import date
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine
from app.domain.models.account import TaiKhoan, LoaiTaiKhoan

class TestJournalEntryLine(unittest.TestCase):
    """Test riêng cho Value Object JournalEntryLine."""

    def test_khoi_tao_thanh_cong(self):
        """Test khởi tạo dòng bút toán thành công."""
        line = JournalEntryLine(so_tai_khoan="111", no=Decimal('100.00'), co=Decimal('0.00'))
        self.assertEqual(line.so_tai_khoan, "111")
        self.assertEqual(line.no, Decimal('100.00'))
        self.assertEqual(line.co, Decimal('0.00'))

    def test_khoi_tao_that_bai_vi_tien_am(self):
        """Test khởi tạo thất bại khi dòng có số tiền âm."""
        with self.assertRaises(ValueError) as context:
            JournalEntryLine(so_tai_khoan="111", no=Decimal('-10.00'), co=Decimal('0.00'))
        self.assertIn("Số tiền ghi Nợ và Có không thể âm", str(context.exception))

        with self.assertRaises(ValueError) as context:
            JournalEntryLine(so_tai_khoan="111", no=Decimal('0.00'), co=Decimal('-5.00'))
        self.assertIn("Số tiền ghi Nợ và Có không thể âm", str(context.exception))

    def test_khoi_tao_that_bai_vi_ca_no_va_co_lon_hon_0(self):
        """Test khởi tạo thất bại khi một dòng có cả Nợ và Có > 0."""
        with self.assertRaises(ValueError) as context:
            JournalEntryLine(so_tai_khoan="111", no=Decimal('10.00'), co=Decimal('5.00'))
        self.assertIn("chỉ được ghi Nợ hoặc Có, không đồng thời cả hai", str(context.exception))

    def test_khoi_tao_khong_co_loi_neu_ca_no_va_co_bang_0(self):
        """Test khởi tạo không lỗi nếu cả Nợ và Có đều bằng 0 (nếu logic cho phép)."""
        # Với logic hiện tại trong __post_init__, điều này sẽ pass
        line = JournalEntryLine(so_tai_khoan="111", no=Decimal('0.00'), co=Decimal('0.00'))
        # Không assert gì cụ thể, nếu không có exception thì OK


class TestJournalEntry(unittest.TestCase):
    """Test cho Entity JournalEntry."""

    def test_khoi_tao_thanh_cong_va_can_bang(self):
        """Test khởi tạo bút toán thành công khi tổng Nợ = Tổng Có."""
        lines = [
            JournalEntryLine(so_tai_khoan="111", no=Decimal('100.00'), co=Decimal('0.00')),
            JournalEntryLine(so_tai_khoan="331", no=Decimal('0.00'), co=Decimal('100.00'))
        ]
        je = JournalEntry(
            ngay_ct=date.today(),
            so_phieu="PT001",
            mo_ta="Test journal entry",
            lines=lines,
            trang_thai="Draft"
        )
        # __post_init__ sẽ tự gọi kiem_tra_can_bang, nếu không lỗi thì pass
        self.assertEqual(je.so_phieu, "PT001")
        self.assertEqual(len(je.lines), 2)

    def test_khoi_tao_that_bai_vi_khong_can_bang(self):
        """Test khởi tạo thất bại khi tổng Nợ != Tổng Có."""
        lines = [
            JournalEntryLine(so_tai_khoan="111", no=Decimal('100.00'), co=Decimal('0.00')),
            JournalEntryLine(so_tai_khoan="331", no=Decimal('0.00'), co=Decimal('90.00')) # Tổng Có < Tổng Nợ
        ]
        with self.assertRaises(ValueError) as context:
            JournalEntry(
                ngay_ct=date.today(),
                so_phieu="PT002",
                mo_ta="Test unbalanced journal entry",
                lines=lines,
                trang_thai="Draft"
            )
        self.assertIn("Bút toán không cân bằng", str(context.exception))

    def test_khoi_tao_that_bai_vi_so_phieu_trong(self):
        """Test khởi tạo thất bại khi số phiếu trống."""
        lines = [
            JournalEntryLine(so_tai_khoan="111", no=Decimal('100.00'), co=Decimal('0.00')),
            JournalEntryLine(so_tai_khoan="331", no=Decimal('0.00'), co=Decimal('100.00'))
        ]
        with self.assertRaises(ValueError) as context:
            JournalEntry(
                ngay_ct=date.today(),
                so_phieu="", # Trống
                mo_ta="Test empty so_phieu",
                lines=lines,
                trang_thai="Draft"
            )
        self.assertIn("Số phiếu không được để trống", str(context.exception))

    def test_khoi_tao_that_bai_vi_khong_co_dong(self):
        """Test khởi tạo thất bại khi không có dòng bút toán."""
        with self.assertRaises(ValueError) as context:
            JournalEntry(
                ngay_ct=date.today(),
                so_phieu="PT003",
                mo_ta="Test no lines",
                lines=[], # Danh sách rỗng
                trang_thai="Draft"
            )
        self.assertIn("Bút toán phải có ít nhất một dòng", str(context.exception))

if __name__ == '__main__':
    unittest.main()