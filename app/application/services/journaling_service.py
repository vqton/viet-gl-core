# File: app/application/services/journaling_service.py

from typing import List, Optional
from app.domain.models.journal_entry import JournalEntry as JournalEntryDomain
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.infrastructure.repositories.account_repository import AccountRepository # Thêm import để kiểm tra

class JournalingService:
    def __init__(self, repository: JournalEntryRepository, account_repository: AccountRepository):
        self.repository = repository
        self.account_repository = account_repository # Dùng để kiểm tra tài khoản trong service

    def tao_phieu_ke_toan(self, journal_entry_domain: JournalEntryDomain) -> JournalEntryDomain:
        """
        Tạo mới một bút toán kế toán.
        - Kiểm tra hợp lệ đã được thực hiện trong Domain Entity (kiem_tra_can_bang).
        - Kiểm tra tài khoản có tồn tại trong hệ thống hay không (tại Application Layer).
        - Gọi Repository để lưu vào DB.
        """
        # Kiểm tra tài khoản tồn tại cho từng dòng trong bút toán
        for line in journal_entry_domain.lines:
            tai_khoan = self.account_repository.get_by_id(line.so_tai_khoan)
            if not tai_khoan:
                raise ValueError(f"Tài khoản '{line.so_tai_khoan}' không tồn tại trong hệ thống.")

        # Gọi Repository để thêm vào DB
        # (Lưu ý: Logic kiểm tra cân bằng `kiem_tra_can_bang` đã được thực hiện
        # trong `__post_init__` của `JournalEntryDomain` khi nó được tạo ra từ API)
        return self.repository.add(journal_entry_domain)

    def lay_phieu_ke_toan_theo_id(self, id: int) -> Optional[JournalEntryDomain]:
        """
        Lấy thông tin bút toán theo ID.
        """
        return self.repository.get_by_id(id)

    def lay_danh_sach_phieu_ke_toan(self) -> List[JournalEntryDomain]:
        """
        Lấy danh sách tất cả bút toán.
        """
        return self.repository.get_all()

    # (Có thể thêm các phương thức khác như cap_nhat_phieu, xoa_phieu, ket_chuyen_tu_dong nếu cần)