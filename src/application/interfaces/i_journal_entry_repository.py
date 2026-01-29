"""
Module: Journal Entry Repository Interface

Định nghĩa hợp đồng truy xuất bút toán kế toán.
"""

from typing import List, Optional
from src.domain.entities.journal_entry import JournalEntry


class IJournalEntryRepository:
    """
    Interface quản lý bút toán kế toán.

    Methods:
        save(entry: JournalEntry) -> None:
            Lưu bút toán vào hệ thống.

        find_by_document_id(document_id: str) -> List[JournalEntry]:
            Tìm bút toán theo ID chứng từ gốc.

        find_by_account(account: str, period: str) -> List[JournalEntry]:
            Tìm bút toán theo tài khoản và kỳ kế toán.

        get_all_entries(period: str) -> List[JournalEntry]:
            Lấy toàn bộ bút toán trong kỳ.
    """

    def save(self, entry: JournalEntry) -> None:
        raise NotImplementedError("Phải được triển khai trong infrastructure layer")

    def find_by_document_id(self, document_id: str) -> List[JournalEntry]:
        raise NotImplementedError("Phải được triển khai trong infrastructure layer")

    def find_by_account(self, account: str, period: str) -> List[JournalEntry]:
        """
        Tìm bút toán theo tài khoản và kỳ kế toán.

        Args:
            account (str): Mã tài khoản (ví dụ: "111", "131")
            period (str): Kỳ kế toán (ví dụ: "2026-Q2")

        Returns:
            List[JournalEntry]: Danh sách bút toán
        """
        raise NotImplementedError("Phải được triển khai trong infrastructure layer")

    def get_all_entries(self, period: str) -> List[JournalEntry]:
        """
        Lấy toàn bộ bút toán trong kỳ.

        Args:
            period (str): Kỳ kế toán

        Returns:
            List[JournalEntry]: Toàn bộ bút toán
        """
        raise NotImplementedError("Phải được triển khai trong infrastructure layer")
