# app/application/services/journaling/query_service.py
"""
[SRP] Service chỉ chịu trách nhiệm truy vấn bút toán kế toán (READ operations).
Không tạo, sửa, xóa, ghi sổ.

🎯 Mục tiêu:
- Cung cấp các hàm như: lấy bút toán theo ID, theo kỳ, theo tài khoản, danh sách, v.v.
- Không can thiệp vào nghiệp vụ ghi sổ hoặc kết chuyển.
"""

from datetime import date
from typing import List, Optional

from app.application.interfaces.journal_entry_repo import (
    JournalEntryRepositoryInterface,
)
from app.domain.models.journal_entry import JournalEntry


class QueryJournalEntryService:
    """
    [SRP] Chỉ phục vụ mục đích truy vấn (query) bút toán kế toán.
    """

    def __init__(self, repo: JournalEntryRepositoryInterface):
        self.repo = repo

    def lay_theo_id(self, id: int) -> Optional[JournalEntry]:
        """
        Lấy bút toán theo ID.
        """
        return self.repo.get_by_id(id)

    def lay_tat_ca(self) -> List[JournalEntry]:
        """
        Lấy tất cả bút toán.
        """
        return self.repo.get_all()

    def lay_theo_ngay(
        self, ngay_bat_dau: date, ngay_ket_thuc: date
    ) -> List[JournalEntry]:
        """
        Lấy bút toán trong khoảng thời gian.
        """
        return self.repo.get_all_in_range(ngay_bat_dau, ngay_ket_thuc)

    def lay_theo_tai_khoan(self, so_tai_khoan: str) -> List[JournalEntry]:
        """
        Lấy các bút toán có chứa tài khoản cụ thể.
        """
        all_entries = self.repo.get_all()
        return [
            entry
            for entry in all_entries
            if any(line.so_tai_khoan == so_tai_khoan for line in entry.lines)
        ]

    def lay_theo_trang_thai(self, trang_thai: str) -> List[JournalEntry]:
        """
        Lấy bút toán theo trạng thái (Draft, Posted, Locked).
        """
        all_entries = self.repo.get_all()
        return [entry for entry in all_entries if entry.trang_thai == trang_thai]
