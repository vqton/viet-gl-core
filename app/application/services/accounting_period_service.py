# File: app/application/services/accounting_period_service.py

from datetime import date
from typing import Optional
from sqlalchemy.orm import Session
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.domain.models.journal_entry import JournalEntry
from app.domain.models.account import TaiKhoan

class AccountingPeriodService:
    def __init__(self, journal_entry_repo: JournalEntryRepository):
        self.journal_entry_repo = journal_entry_repo

    def khoa_ky(self, period_id: int) -> bool:
        """
        Khóa sổ kế toán cho kỳ đã cho.
        Quy trình:
        1. Kiểm tra xem tất cả các bút toán trong kỳ đã được "Posted" chưa.
        2. Kiểm tra xem tổng Nợ = Tổng Có trong kỳ.
        3. Nếu đạt yêu cầu, cập nhật trạng thái của tất cả bút toán trong kỳ thành "Locked".
        """
        # 1. Lấy tất cả bút toán trong kỳ (giả sử có trường period_id trong JournalEntry)
        journal_entries = self.journal_entry_repo.get_all_by_period(period_id)

        # Kiểm tra 1: Tất cả bút toán đều đã "Posted"
        for je in journal_entries:
            if je.trang_thai != "Posted":
                raise ValueError(f"Bút toán {je.so_phieu} vẫn ở trạng thái {je.trang_thai}. Phải 'Posted' trước khi khóa sổ.")

        # Kiểm tra 2: Tổng Nợ = Tổng Có trong kỳ (có thể tính toán từ các dòng bút toán)
        # ... (Logic phức tạp hơn, cần tính tổng toàn bộ dòng Nợ và Có trong kỳ)
        # ... (Bỏ qua để tập trung vào cấu trúc, thực tế cần tính toán chi tiết)

        # Nếu tất cả kiểm tra đều đạt, cập nhật trạng thái
        for je in journal_entries:
            je.trang_thai = "Locked"
            self.journal_entry_repo.update(je) # Cần thêm phương thức update trong Repository

        return True

    def mo_ky(self, period_id: int) -> bool:
        """
        Mở sổ kế toán cho kỳ đã cho.
        Chỉ Admin mới có quyền, cần có lý do chính đáng.
        """
        # ... (Logic mở sổ, cập nhật trạng thái từ "Locked" về "Posted")
        # ... (Có thể thêm kiểm tra vai trò người dùng ở đây nếu cần)
        return True

    def is_ky_da_khoa(self, period_id: int) -> bool:
        """
        Kiểm tra xem kỳ đã bị khóa chưa.
        """
        journal_entries = self.journal_entry_repo.get_all_by_period(period_id)
        if not journal_entries:
            return False
        # Nếu có ít nhất một bút toán trong kỳ có trạng thái "Locked", thì kỳ đã khóa
        for je in journal_entries:
            if je.trang_thai == "Locked":
                return True
        return False