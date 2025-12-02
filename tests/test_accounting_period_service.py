import unittest
from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from app.application.services.accounting_period_service import (
    AccountingPeriodService,
)
from app.domain.models.account import LoaiTaiKhoan, TaiKhoan
from app.domain.models.accounting_period import KyKeToan
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine


class TestAccountingPeriodService(unittest.TestCase):

    def setUp(self):
        # Mock cả 2 repository: dành cho AccountingPeriod và JournalEntry
        self.mock_period_repo = Mock()
        self.mock_je_repo = Mock()
        # 👇 Truyền ĐÚNG TÊN THAM SỐ theo constructor của AccountingPeriodService
        self.service = AccountingPeriodService(
            repository=self.mock_period_repo,
            journal_entry_repo=self.mock_je_repo,
        )

    def test_khoa_ky_thanh_cong(self):
        # Mock master data kỳ kế toán
        ky = KyKeToan(
            id=1,
            ten_ky="Năm 2025",
            ngay_bat_dau=date(2025, 1, 1),
            ngay_ket_thuc=date(2025, 12, 31),
            trang_thai="Open",
        )
        self.mock_period_repo.get_by_id.return_value = ky
        # 👇 MOCK: Không có bút toán nháp → trả về list rỗng
        self.mock_je_repo.get_draft_entries_by_date_range.return_value = []

        result = self.service.khoa_ky(1)
        self.assertTrue(result)
        self.mock_period_repo.update_trang_thai.assert_called_once_with(
            1, "Locked"
        )

    def test_khoa_ky_that_bai_vi_chua_posted(self):
        # Mock master data kỳ kế toán
        ky = KyKeToan(
            id=1,
            ten_ky="Năm 2025",
            ngay_bat_dau=date(2025, 1, 1),
            ngay_ket_thuc=date(2025, 12, 31),
            trang_thai="Open",
        )
        self.mock_period_repo.get_by_id.return_value = ky
        # Mock: Có 1 bút toán nháp
        entries = [
            JournalEntry(
                id=1,
                ngay_ct=date.today(),
                so_phieu="PT001",
                mo_ta="Mua hàng",
                lines=[
                    JournalEntryLine(
                        so_tai_khoan="111", no=Decimal('100'), co=Decimal('0')
                    ),
                    JournalEntryLine(
                        so_tai_khoan="331", no=Decimal('0'), co=Decimal('100')
                    ),
                ],
                trang_thai="Draft",
            )
        ]
        self.mock_je_repo.get_draft_entries_by_date_range.return_value = (
            entries
        )

        with self.assertRaises(ValueError) as context:
            self.service.khoa_ky(1)
        # 👇 SỬA MESSAGE CHO KHỚP VỚI IMPLEMENTATION
        self.assertIn("Vẫn còn", str(context.exception))
