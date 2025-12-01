import unittest
from decimal import Decimal
from datetime import date
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine


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
        self.assertIn("Số tiền Nợ/Có không thể âm", str(context.exception))

        with self.assertRaises(ValueError) as context:
            JournalEntryLine(so_tai_khoan="111", no=Decimal('0.00'), co=Decimal('-5.00'))
        self.assertIn("Số tiền Nợ/Có không thể âm", str(context.exception))

    def test_khoi_tao_that_bai_vi_ca_no_va_co_lon_hon_0(self):
        """Test khởi tạo thất bại khi một dòng có cả Nợ và Có > 0."""
        with self.assertRaises(ValueError) as context:
            JournalEntryLine(so_tai_khoan="111", no=Decimal('10.00'), co=Decimal('5.00'))
        self.assertIn("chỉ được ghi Nợ hoặc Có, không đồng thời cả hai", str(context.exception))

    def test_khoi_tao_that_bai_neu_ca_no_va_co_bang_0(self):
        """Theo TT99, dòng bút toán phải có giá trị phát sinh → không cho phép no=0, co=0."""
        with self.assertRaises(ValueError) as context:
            JournalEntryLine(so_tai_khoan="111", no=Decimal('0.00'), co=Decimal('0.00'))
        self.assertIn("phải có giá trị phát sinh", str(context.exception))


class TestJournalEntry(unittest.TestCase):
    """Test cho Entity JournalEntry."""

    def test_khoi_tao_thanh_cong_va_can_bang(self):
        """Test khởi tạo bút toán thành công khi tổng Nợ = Tổng Có và có ít nhất 2 dòng."""
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
        self.assertEqual(je.so_phieu, "PT001")
        self.assertEqual(len(je.lines), 2)

    def test_khoi_tao_that_bai_vi_khong_can_bang(self):
        """Test khởi tạo thất bại khi tổng Nợ != Tổng Có."""
        lines = [
            JournalEntryLine(so_tai_khoan="111", no=Decimal('100.00'), co=Decimal('0.00')),
            JournalEntryLine(so_tai_khoan="331", no=Decimal('0.00'), co=Decimal('90.00'))
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
                so_phieu="",  # Trống
                mo_ta="Test empty so_phieu",
                lines=lines,
                trang_thai="Draft"
            )
        self.assertIn("Số phiếu không được để trống", str(context.exception))

    def test_khoi_tao_that_bai_vi_it_hon_2_dong(self):
        """Theo TT99, bút toán phải có ít nhất 2 dòng (Nợ + Có)."""
        with self.assertRaises(ValueError) as context:
            JournalEntry(
                ngay_ct=date.today(),
                so_phieu="PT003",
                mo_ta="Test only 1 line",
                lines=[
                    JournalEntryLine(so_tai_khoan="111", no=Decimal('100'), co=Decimal('0'))
                ],
                trang_thai="Draft"
            )
        self.assertIn("ít nhất 2 dòng", str(context.exception))

    def test_khoi_tao_that_bai_vi_danh_sach_rong(self):
        """Test khởi tạo thất bại khi không có dòng bút toán."""
        with self.assertRaises(ValueError) as context:
            JournalEntry(
                ngay_ct=date.today(),
                so_phieu="PT004",
                mo_ta="Test no lines",
                lines=[],  # Danh sách rỗng
                trang_thai="Draft"
            )
        self.assertIn("ít nhất 2 dòng", str(context.exception))

    # tests/test_journal_entry.py
    def test_but_toan_can_bang_no_co():
        """Điều 24 TT99: Bút toán phải cân bằng Nợ = Có."""
        entry = JournalEntry(
            lines=[
                JournalEntryLine(so_tai_khoan="112", no=Decimal("110000000"), co=Decimal("0")),
                JournalEntryLine(so_tai_khoan="511", no=Decimal("0"), co=Decimal("100000000")),
                JournalEntryLine(so_tai_khoan="3331", no=Decimal("0"), co=Decimal("10000000")),
            ]
        )
        assert entry.tong_no == entry.tong_co

    def test_chung_tu_goc_bat_buoc_khi_ghi_so():
        """Điều 8–10 TT99: Bút toán ghi sổ phải có chứng từ gốc."""
        line = JournalEntryLine(
            so_tai_khoan="112",
            no=Decimal("100000000"),
            co=Decimal("0"),
            so_chung_tu_goc="PT-2025-001",      # ✅ Bắt buộc
            ngay_chung_tu_goc=date(2025, 6, 15)  # ✅ Bắt buộc
        )
        assert line.so_chung_tu_goc is not None
        assert line.ngay_chung_tu_goc is not None
    
if __name__ == '__main__':
    unittest.main()