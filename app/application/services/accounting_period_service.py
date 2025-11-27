# File: app/application/services/accounting_period_service.py

from typing import List, Optional
from datetime import date
from app.domain.models.accounting_period import KyKeToan as KyKeToanDomain
from app.infrastructure.repositories.accounting_period_repository import AccountingPeriodRepository
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository # Cần repo để kiểm tra bút toán

class AccountingPeriodService:
    """
    Service Layer cho việc quản lý các Kỳ Kế toán (Khóa/Mở sổ).
    """
    def __init__(self, repository: AccountingPeriodRepository, journal_entry_repo: JournalEntryRepository):
        self.repository = repository
        self.journal_entry_repo = journal_entry_repo

    def tao_ky_ke_toan(self, ky_ke_toan_domain: KyKeToanDomain) -> KyKeToanDomain:
        """
        Tạo mới một kỳ kế toán.
        - Kiểm tra tên kỳ đã tồn tại chưa.
        - Kiểm tra ngày tháng có bị trùng lặp với các kỳ đã có không.
        """
        # Kiểm tra xem tên kỳ đã tồn tại chưa
        existing_ky = self.repository.get_by_ten_ky(ky_ke_toan_domain.ten_ky)
        if existing_ky:
            raise ValueError(f"Kỳ kế toán '{ky_ke_toan_domain.ten_ky}' đã tồn tại.")

        # Kiểm tra ngày tháng có bị trùng lặp với các kỳ đã có không
        if self.repository.check_overlapping_periods(ky_ke_toan_domain.ngay_bat_dau, ky_ke_toan_domain.ngay_ket_thuc):
             raise ValueError("Ngày bắt đầu hoặc ngày kết thúc bị trùng lặp với một kỳ kế toán khác.")

        # Gọi Repository để thêm vào DB
        return self.repository.add(ky_ke_toan_domain)

    def lay_ky_ke_toan_theo_id(self, id: int) -> Optional[KyKeToanDomain]:
        """
        Lấy kỳ kế toán theo ID.
        """
        return self.repository.get_by_id(id)

    def lay_tat_ca_ky_ke_toan(self) -> List[KyKeToanDomain]:
        """
        Lấy danh sách tất cả các kỳ kế toán.
        """
        return self.repository.get_all()

    def lay_ky_ke_toan_theo_ngay(self, ngay: date) -> Optional[KyKeToanDomain]:
        """
        Tìm kỳ kế toán mà ngày cho trước nằm trong khoảng [ngay_bat_dau, ngay_ket_thuc].
        """
        return self.repository.get_by_date(ngay)

    def is_ky_da_khoa(self, ky_id: int) -> bool:
        """
        Kiểm tra xem kỳ kế toán đã bị khóa (Locked) hay chưa.
        """
        ky = self.repository.get_by_id(ky_id)
        if not ky:
            # Nếu không tìm thấy kỳ, coi như không bị khóa
            return False
        return ky.trang_thai == "Locked"

    def _kiem_tra_khoa_so(self, ngay_chung_tu: date):
        """
        Hàm helper để kiểm tra xem ngày chứng từ có nằm trong kỳ đã khóa hay không.
        Nếu có, sẽ raise ValueError.
        """
        ky = self.lay_ky_ke_toan_theo_ngay(ngay_chung_tu)
        if not ky:
            raise ValueError(f"Không tìm thấy kỳ kế toán hợp lệ cho ngày {ngay_chung_tu.strftime('%Y-%m-%d')}.")

        if ky.trang_thai == "Locked":
            raise ValueError(f"Kỳ kế toán '{ky.ten_ky}' (ID: {ky.id}) đã bị khóa. Không thể tạo/cập nhật bút toán cho ngày {ngay_chung_tu.strftime('%Y-%m-%d')}.")

        return ky # Trả về kỳ nếu cần sử dụng ID hoặc thông tin khác


    def khoa_ky(self, id: int, nguoi_thuc_hien: str = "System") -> bool:
        """
        Khóa sổ kế toán cho kỳ đã cho (GL-05).
        - Kiểm tra kỳ tồn tại.
        - Kiểm tra kỳ đang ở trạng thái 'Open'.
        - Kiểm tra không có bút toán 'Draft' (Nháp) nào trong kỳ.
        """
        ky = self.repository.get_by_id(id)
        if not ky:
            raise ValueError(f"Kỳ kế toán với ID {id} không tồn tại.")

        if ky.trang_thai != "Open":
            raise ValueError(f"Kỳ '{ky.ten_ky}' phải ở trạng thái 'Open' mới có thể khóa.")

        # Kiểm tra bút toán nháp
        # Sử dụng journal_entry_repo để tìm các bút toán nháp trong kỳ này (dựa trên ngày tháng)
        draft_entries = self.journal_entry_repo.get_draft_entries_by_period(id) # Sử dụng logic dựa trên ngày tháng trong repo
        if draft_entries:
            raise ValueError(f"Không thể khóa kỳ '{ky.ten_ky}'. Vẫn còn {len(draft_entries)} bút toán ở trạng thái 'Draft'.")

        # Tất cả kiểm tra đều đạt, cập nhật trạng thái
        self.repository.update_trang_thai(id, "Locked")
        print(f"[LOG] Kỳ '{ky.ten_ky}' (ID: {id}) đã được khóa bởi {nguoi_thuc_hien} vào {ky.ngay_ket_thuc}.")
        return True

    def mo_ky(self, id: int, ly_do: str, nguoi_thuc_hien: str = "System") -> bool:
        """
        Mở sổ kế toán cho kỳ đã cho.
        Yêu cầu: Phải có lý do chính đáng.
        """
        # (Có thể thêm kiểm tra quyền hạn người dùng ở đây nếu có hệ thống phân quyền)
        if not ly_do or not ly_do.strip():
            raise ValueError("Lý do mở kỳ không được để trống.")

        ky = self.repository.get_by_id(id)
        if not ky:
            raise ValueError(f"Kỳ kế toán với ID {id} không tồn tại.")

        if ky.trang_thai != "Locked":
            raise ValueError(f"Kỳ '{ky.ten_ky}' không ở trạng thái 'Locked' nên không thể mở.")

        # Cập nhật trạng thái
        self.repository.update_trang_thai(id, "Open")
        print(f"[LOG] Kỳ '{ky.ten_ky}' (ID: {id}) đã được mở bởi {nguoi_thuc_hien} với lý do: {ly_do}.")
        return True