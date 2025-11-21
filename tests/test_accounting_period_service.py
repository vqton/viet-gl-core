# File: tests/test_accounting_period_service.py

import unittest
from unittest.mock import Mock
from app.application.services.accounting_period_service import AccountingPeriodService
from app.domain.models.journal_entry import JournalEntry,JournalEntryLine
from decimal import Decimal

class TestAccountingPeriodService(unittest.TestCase):

    def setUp(self):
        self.mock_je_repo = Mock()
        self.service = AccountingPeriodService(self.mock_je_repo)

    def test_khoa_ky_thanh_cong(self):
        """
        Test khóa sổ thành công khi tất cả bút toán đều đã "Posted".
        """
          # Tạo dòng bút toán giả định (ví dụ: Nợ 111, Có 331)
        lines = [
                JournalEntryLine(so_tai_khoan="111", no=Decimal('100'), co=Decimal('0')),
                JournalEntryLine(so_tai_khoan="331", no=Decimal('0'), co=Decimal('100'))
                 ]
        # lines = [JournalEntryLine(so_tai_khoan="331", no=Decimal('0'), co=Decimal('100'))]
        # Tạo các bút toán giả định
        entries = [
            JournalEntry(id=1, so_phieu="PT001", trang_thai="Posted",  lines=lines),
            # JournalEntry(id=2, so_phieu="PT002", trang_thai="Posted",  lines=lines2),
        ]
        self.mock_je_repo.get_all_by_period.return_value = entries

        # Gọi hàm khóa sổ
        result = self.service.khoa_ky(1)

        # Kiểm tra
        self.assertTrue(result)
        # Kiểm tra rằng các bút toán đã được cập nhật trạng thái thành "Locked"
        for je in entries:
            self.assertEqual(je.trang_thai, "Locked")

    def test_khoa_ky_that_bai_vi_chua_posted(self):
        """
        Test khóa sổ thất bại khi có bút toán chưa "Posted".
        """
                  # Tạo dòng bút toán giả định (ví dụ: Nợ 111, Có 331)
        lines = [JournalEntryLine(so_tai_khoan="111", no=Decimal('100'), co=Decimal('0')),
                  JournalEntryLine(so_tai_khoan="331", no=Decimal('0'), co=Decimal('100'))]
        # lines2 = []
        # Tạo các bút toán giả định
        entries = [
            JournalEntry(id=1, so_phieu="PT001", trang_thai="Draft",lines=lines), # Không được phép khóa
            # JournalEntry(id=2, so_phieu="PT002", trang_thai="Posted",lines=lines2),
        ]
        self.mock_je_repo.get_all_by_period.return_value = entries

        with self.assertRaises(ValueError):
            self.service.khoa_ky(1)