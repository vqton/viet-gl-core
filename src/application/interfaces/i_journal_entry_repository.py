"""
Module: Journal Entry Repository Interface

Định nghĩa hợp đồng lưu trữ bút toán kế toán.

Yêu cầu pháp lý:
- Điều 27 TT 99: Phải lưu trữ đầy đủ audit trail
- Phải hỗ trợ truy vấn theo chứng từ, kỳ kế toán, tài khoản

Lưu ý:
- Không chứa logic nghiệp vụ — chỉ định nghĩa hành vi
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
    """

    def save(self, entry: JournalEntry) -> None:
        """
        Lưu bút toán kế toán.

        Args:
            entry (JournalEntry): Bút toán cần lưu.

        Raises:
            NotImplementedError: Vì đây là interface.
        """
        raise NotImplementedError("Phải được triển khai trong adapter layer")

    def find_by_document_id(self, document_id: str) -> List[JournalEntry]:
        """
        Tìm bút toán theo ID chứng từ gốc.

        Args:
            document_id (str): ID chứng từ (ví dụ: số hóa đơn).

        Returns:
            List[JournalEntry]: Danh sách bút toán liên quan.

        Raises:
            NotImplementedError: Vì đây là interface.
        """
        raise NotImplementedError("Phải được triển khai trong adapter layer")
