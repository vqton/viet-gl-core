from datetime import date
from typing import List, Optional

from app.domain.models.accounting_period import KyKeToan as KyKeToanDomain
from app.domain.models.journal_entry import JournalEntry as JournalEntryDomain
from app.infrastructure.repositories.accounting_period_repository import (
    AccountingPeriodRepository,
)
from app.infrastructure.repositories.journal_entry_repository import (
    JournalEntryRepository,
)


class AccountingPeriodService:
    """
    Dịch vụ quản lý các quy trình nghiệp vụ liên quan đến Kỳ Kế Toán.
    """

    def __init__(
        self,
        repository: AccountingPeriodRepository,
        journal_entry_repo: JournalEntryRepository,
    ):
        self.repository = repository
        self.journal_entry_repo = journal_entry_repo

    def tao_ky_ke_toan(
        self, ky_ke_toan_domain: KyKeToanDomain
    ) -> KyKeToanDomain:
        """
        Tạo mới một kỳ kế toán.
        - Đảm bảo tên kỳ là duy nhất.
        - Gọi Repository để thêm vào DB.
        """
        # Kiểm tra xem tên kỳ đã tồn tại chưa
        existing_ky = self.repository.get_by_ten_ky(ky_ke_toan_domain.ten_ky)
        if existing_ky:
            raise ValueError(
                f"Kỳ kế toán '{ky_ke_toan_domain.ten_ky}' đã tồn tại."
            )

        # Gọi Repository để thêm vào DB
        return self.repository.add(ky_ke_toan_domain)

    def lay_ky_ke_toan_theo_id(self, id: int) -> Optional[KyKeToanDomain]:
        """
        Lấy thông tin kỳ kế toán theo ID.
        """
        return self.repository.get_by_id(id)

    def lay_ky_hien_hanh_cho_ngay(
        self, ngay: date
    ) -> Optional[KyKeToanDomain]:
        """
        Tìm kỳ kế toán đang mở hoặc đã khóa mà ngày chứng từ thuộc về.
        (Cần một method get_by_date trong repository để thực hiện điều này)
        """
        return self.repository.get_by_date(ngay)

    def is_ky_da_khoa(self, ky_id: int) -> bool:
        """
        Kiểm tra xem một kỳ kế toán đã bị khóa chưa.
        """
        ky = self.repository.get_by_id(ky_id)
        return ky is not None and ky.trang_thai == "Locked"

    def khoa_ky(self, id: int, nguoi_thuc_hien: str = "System") -> bool:
        """
        Khóa sổ kế toán cho kỳ đã cho (GL-05 - Quy trình khóa sổ).
        - Kiểm tra bút toán nháp (Draft).
        - Cập nhật trạng thái thành 'Locked'.
        """
        ky = self.repository.get_by_id(id)
        if not ky:
            raise ValueError(f"Kỳ kế toán với ID {id} không tồn tại.")

        if ky.trang_thai == "Locked":
            raise ValueError(f"Kỳ '{ky.ten_ky}' đã bị khóa rồi.")

        # 1. Kiểm tra bút toán nháp (Draft) trong khoảng thời gian của kỳ
        draft_entries = (
            self.journal_entry_repo.get_draft_entries_by_date_range(
                ky.ngay_bat_dau, ky.ngay_ket_thuc
            )
        )

        if draft_entries:
            draft_so_phieu = [e.so_phieu for e in draft_entries]
            raise ValueError(
                f"Không thể khóa kỳ '{ky.ten_ky}'. Vẫn còn {len(draft_entries)} bút toán nháp: {', '.join(draft_so_phieu[:5])}{'...' if len(draft_so_phieu) > 5 else ''}"
            )

        # Nếu tất cả kiểm tra đều đạt, cập nhật trạng thái
        self.repository.update_trang_thai(id, "Locked")
        return True

    def mo_ky(
        self, id: int, ly_do: str, nguoi_thuc_hien: str = "System"
    ) -> bool:
        """
        Mở sổ kế toán cho kỳ đã khóa.
        Yêu cầu: Phải có lý do chính đáng và chỉ áp dụng cho kỳ đang ở trạng thái 'Locked'.
        """
        if not ly_do or not ly_do.strip():
            raise ValueError("Lý do mở kỳ không được để trống.")

        ky = self.repository.get_by_id(id)
        if not ky:
            raise ValueError(f"Kỳ kế toán với ID {id} không tồn tại.")

        if ky.trang_thai != "Locked":
            raise ValueError(
                f"Kỳ '{ky.ten_ky}' không ở trạng thái 'Locked' nên không thể mở."
            )

        # Cập nhật trạng thái
        self.repository.update_trang_thai(id, "Open")
        return True

    def lay_tat_ca_ky_ke_toan(self) -> List[KyKeToanDomain]:
        """
        Lấy danh sách tất cả kỳ kế toán.
        """
        return self.repository.get_all()
