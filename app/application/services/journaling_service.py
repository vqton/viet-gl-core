from datetime import date
from typing import List, Optional

# Domain Models
from app.domain.models.journal_entry import JournalEntry as JournalEntryDomain

# Repositories
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.infrastructure.repositories.account_repository import AccountRepository

# Services
from app.application.services.accounting_period_service import AccountingPeriodService # <-- NEW IMPORT

class JournalingService:
    def __init__(self,
                 repository: JournalEntryRepository,
                 account_repository: AccountRepository,
                 accounting_period_service: AccountingPeriodService # <-- NEW DEPENDENCY
                ):
        """
        Khởi tạo JournalingService với các Repository và Service cần thiết.
        """
        self.repository = repository
        self.account_repository = account_repository
        self.accounting_period_service = accounting_period_service

    def _kiem_tra_khoa_so(self, ngay_ct: date):
        """
        Helper function: Kiểm tra xem ngày chứng từ có nằm trong kỳ đã khóa hay không.
        Nếu kỳ đã khóa hoặc không tìm thấy kỳ, sẽ raise ValueError.
        """
        # 1. Tìm kỳ kế toán chứa ngày chứng từ
        # Chức năng này được giả định đã có trong AccountingPeriodService
        ky = self.accounting_period_service.lay_ky_chua_ngay(ngay_ct)

        if not ky:
            raise ValueError(f"Không tìm thấy kỳ kế toán cho ngày {ngay_ct.strftime('%Y-%m-%d')}. Vui lòng kiểm tra ngày chứng từ hoặc tạo kỳ kế toán.")

        # 2. Kiểm tra trạng thái kỳ
        if self.accounting_period_service.is_ky_da_khoa(ky.id):
            raise ValueError(f"Kỳ kế toán '{ky.ten_ky}' (ID: {ky.id}) đã bị khóa. Không thể thực hiện nghiệp vụ cho ngày {ngay_ct.strftime('%Y-%m-%d')}.")

    def tao_phieu_ke_toan(self, journal_entry_domain: JournalEntryDomain) -> JournalEntryDomain:
        """
        Tạo mới một bút toán kế toán.
        - Kiểm tra khóa sổ.
        - Kiểm tra tài khoản có tồn tại trong hệ thống.
        - Gọi Repository để lưu vào DB.
        """
        # 1. Kiểm tra khóa sổ
        self._kiem_tra_khoa_so(journal_entry_domain.ngay_ct)

        # 2. Kiểm tra tài khoản tồn tại cho từng dòng trong bút toán
        for line in journal_entry_domain.lines:
            tai_khoan = self.account_repository.get_by_id(line.so_tai_khoan)
            if not tai_khoan:
                raise ValueError(f"Tài khoản '{line.so_tai_khoan}' không tồn tại trong hệ thống.")

        # 3. Gọi Repository để thêm vào DB
        return self.repository.add(journal_entry_domain)

    def lay_phieu_ke_toan_theo_id(self, id: int) -> Optional[JournalEntryDomain]:
        """
        Lấy thông tin bút toán theo ID.
        """
        return self.repository.get_by_id(id)

    def lay_tat_ca_phieu_ke_toan(self) -> List[JournalEntryDomain]:
        """
        Lấy danh sách tất cả bút toán kế toán.
        """
        return self.repository.get_all()

    def cap_nhat_phieu_ke_toan(self, id: int, journal_entry_domain_updated: JournalEntryDomain) -> Optional[JournalEntryDomain]:
        """
        Cập nhật một bút toán kế toán.
        - Chỉ cho phép cập nhật nếu trạng thái là 'Draft' VÀ kỳ kế toán chưa khóa.
        - Kiểm tra hợp lệ lại (tài khoản tồn tại).
        - Gọi Repository để cập nhật DB.
        """
        journal_entry_hien_tai = self.repository.get_by_id(id)
        if not journal_entry_hien_tai:
            return None # Không tìm thấy để cập nhật

        # 1. Kiểm tra trạng thái hiện tại
        if journal_entry_hien_tai.trang_thai != "Draft":
             raise ValueError(f"Không thể cập nhật bút toán {id} vì nó đang ở trạng thái '{journal_entry_hien_tai.trang_thai}'. Chỉ có thể cập nhật bút toán 'Draft'.")

        # 2. Kiểm tra khóa sổ cho ngày chứng từ mới
        self._kiem_tra_khoa_so(journal_entry_domain_updated.ngay_ct)

        # 3. Kiểm tra tài khoản tồn tại cho từng dòng mới
        for line in journal_entry_domain_updated.lines:
            tai_khoan = self.account_repository.get_by_id(line.so_tai_khoan)
            if not tai_khoan:
                raise ValueError(f"Tài khoản '{line.so_tai_khoan}' không tồn tại trong hệ thống.")

        # 4. Gọi Repository để cập nhật DB
        return self.repository.update(id, journal_entry_domain_updated)

    def xoa_phieu_ke_toan(self, id: int) -> bool:
        """
        Xóa một bút toán kế toán.
        - Kiểm tra xem bút toán có tồn tại không.
        - Chỉ cho phép xóa nếu bút toán là 'Draft' VÀ Kỳ chưa khóa.
        - Gọi Repository để xóa.
        """
        journal_entry = self.repository.get_by_id(id)
        if not journal_entry:
            return False

        # 1. Kiểm tra trạng thái
        if journal_entry.trang_thai != "Draft":
            raise ValueError(f"Không thể xóa bút toán {id} vì trạng thái là '{journal_entry.trang_thai}'. Chỉ có thể xóa bút toán ở trạng thái 'Draft'.")

        # 2. Kiểm tra khóa sổ
        self._kiem_tra_khoa_so(journal_entry.ngay_ct)

        return self.repository.delete(id)

    def ghi_so(self, id: int) -> JournalEntryDomain:
        """
        Ghi sổ (Post) một bút toán.
        - Đảm bảo bút toán là 'Draft'.
        - Kiểm tra kỳ kế toán chưa khóa.
        - Cập nhật trạng thái thành 'Posted'.
        """
        journal_entry = self.repository.get_by_id(id)
        if not journal_entry:
            raise ValueError(f"Bút toán với ID {id} không tồn tại.")

        # 1. Kiểm tra trạng thái
        if journal_entry.trang_thai != "Draft":
            raise ValueError(f"Chỉ có thể Ghi sổ bút toán ở trạng thái 'Draft'. Bút toán {id} đang ở trạng thái '{journal_entry.trang_thai}'.")

        # 2. Kiểm tra khóa sổ
        self._kiem_tra_khoa_so(journal_entry.ngay_ct)

        # 3. Cập nhật trạng thái và lưu
        return self.repository.update_status(id, "Posted")

    def huy_ghi_so(self, id: int) -> JournalEntryDomain:
        """
        Hủy ghi sổ (Unpost) một bút toán.
        - Đảm bảo bút toán là 'Posted'.
        - Kiểm tra kỳ kế toán chưa khóa.
        - Cập nhật trạng thái thành 'Draft'.
        """
        journal_entry = self.repository.get_by_id(id)
        if not journal_entry:
            raise ValueError(f"Bút toán với ID {id} không tồn tại.")

        # 1. Kiểm tra trạng thái
        if journal_entry.trang_thai != "Posted":
            raise ValueError(f"Chỉ có thể Hủy ghi sổ bút toán ở trạng thái 'Posted'. Bút toán {id} đang ở trạng thái '{journal_entry.trang_thai}'.")

        # 2. Kiểm tra khóa sổ
        self._kiem_tra_khoa_so(journal_entry.ngay_ct)

        # 3. Cập nhật trạng thái và lưu
        return self.repository.update_status(id, "Draft")