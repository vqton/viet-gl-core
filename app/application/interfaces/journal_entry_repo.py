from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal
from typing import List, Optional

from app.domain.models.journal_entry import ButToanLine, GhiSoKeToan

# from app.domain.models.journal_entry import JournalEntry


class JournalEntryRepositoryInterface(ABC):
    """
    Interface định nghĩa các phương thức cần thiết để lưu trữ và truy xuất
    Bút toán tổng hợp (JournalEntry), bao gồm cả các phương thức báo cáo
    (get_all_posted_in_range, get_so_du_dau_ky).
    """

    @abstractmethod
    def add(self, entry: GhiSoKeToan) -> GhiSoKeToan:
        """Thêm một bút toán mới vào hệ thống."""
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> Optional[GhiSoKeToan]:
        """Lấy bút toán theo ID."""
        pass

    @abstractmethod
    def get_all(self) -> List[GhiSoKeToan]:
        """Lấy tất cả các bút toán."""
        pass

    @abstractmethod
    def get_all_posted_in_range(
        self, start: date, end: date
    ) -> List[GhiSoKeToan]:
        """Lấy tất cả các bút toán đã ghi sổ (Posted) trong phạm vi ngày."""
        pass

    @abstractmethod
    def update_status(self, id: int, status: str) -> GhiSoKeToan:
        """Cập nhật trạng thái của bút toán và trả về đối tượng đã cập nhật."""
        pass

    @abstractmethod
    def get_so_du_dau_ky(self, so_tai_khoan: str, ngay: date) -> Decimal:
        """
        Lấy số dư đầu kỳ của một tài khoản cụ thể (Dư Nợ hoặc Dư Có) tại một ngày cho trước.
        Giá trị trả về luôn là số dương.
        """
        pass
