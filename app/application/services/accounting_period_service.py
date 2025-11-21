# File: app/application/services/accounting_period_service.py

from typing import List, Optional
from app.domain.models.accounting_period import KyKeToan as KyKeToanDomain
from app.infrastructure.repositories.accounting_period_repository import AccountingPeriodRepository
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository # Cần repo để kiểm tra bút toán
from app.domain.models.journal_entry import JournalEntry as JournalEntryDomain # Nếu cần

class AccountingPeriodService:
    def __init__(self, repository: AccountingPeriodRepository, journal_entry_repo: JournalEntryRepository):
        self.repository = repository
        self.journal_entry_repo = journal_entry_repo

    def tao_ky_ke_toan(self, ky_ke_toan_domain: KyKeToanDomain) -> KyKeToanDomain:
        """
        Tạo mới một kỳ kế toán.
        """
        # Kiểm tra xem tên kỳ đã tồn tại chưa
        existing_ky = self.repository.get_by_ten_ky(ky_ke_toan_domain.ten_ky)
        if existing_ky:
            raise ValueError(f"Kỳ kế toán '{ky_ke_toan_domain.ten_ky}' đã tồn tại.")

        # Gọi Repository để thêm vào DB
        return self.repository.add(ky_ke_toan_domain)

    def lay_ky_ke_toan_theo_id(self, id: int) -> Optional[KyKeToanDomain]:
        """
        Lấy thông tin kỳ kế toán theo ID.
        """
        return self.repository.get_by_id(id)

    def lay_ky_ke_toan_theo_ten(self, ten_ky: str) -> Optional[KyKeToanDomain]:
        """
        Lấy thông tin kỳ kế toán theo tên kỳ.
        """
        return self.repository.get_by_ten_ky(ten_ky)

    def lay_danh_sach_ky_ke_toan(self) -> List[KyKeToanDomain]:
        """
        Lấy danh sách tất cả kỳ kế toán.
        """
        return self.repository.get_all()

    def khoa_ky(self, id: int, nguoi_thuc_hien: str = "System") -> bool:
        """
        Khóa sổ kế toán cho kỳ đã cho.
        Quy trình:
        1. Kiểm tra xem kỳ đã bị khóa chưa.
        2. Kiểm tra xem tất cả các bút toán trong kỳ đã được "Posted" chưa.
        3. (Tùy chọn) Kiểm tra xem tổng Nợ = Tổng Có trong kỳ (cân đối thử).
        4. Nếu đạt yêu cầu, cập nhật trạng thái của kỳ thành "Locked".
        5. Ghi log việc khóa kỳ.
        """
        ky = self.repository.get_by_id(id)
        if not ky:
            raise ValueError(f"Kỳ kế toán với ID {id} không tồn tại.")

        if ky.trang_thai == "Locked":
            raise ValueError(f"Kỳ '{ky.ten_ky}' đã bị khóa từ trước.")

        # Lấy tất cả bút toán trong kỳ (giả sử có phương thức lọc theo ngày trong repo)
        # journal_entries = self.journal_entry_repo.get_by_period_date_range(ky.ngay_bat_dau, ky.ngay_ket_thuc)
        # --- LƯU Ý: Repo hiện chưa có phương thức lọc theo ngày ---
        # Để đơn giản trong ví dụ này, ta giả định repo có phương thức này hoặc sẽ được bổ sung.
        # Ta sẽ giả định có một phương thức get_by_period_status(id_ky, status) hoặc lọc theo ngày.
        # Giả sử repo có phương thức get_all_for_period_by_date(start_date, end_date)
        # entries_trong_ky = self.journal_entry_repo.get_all_for_period_by_date(ky.ngay_bat_dau, ky.ngay_ket_thuc)
        # --- THAY THẾ: LẤY TẤT CẢ VÀ LỌC Ở ĐÂY ---
        all_entries = self.journal_entry_repo.get_all()
        entries_trong_ky = [e for e in all_entries if ky.ngay_bat_dau <= e.ngay_ct <= ky.ngay_ket_thuc]

        # Kiểm tra 1: Tất cả bút toán trong kỳ đều đã "Posted"
        for entry in entries_trong_ky:
            if entry.trang_thai != "Posted":
                raise ValueError(f"Bút toán {entry.so_phieu} (ngày {entry.ngay_ct}) trong kỳ '{ky.ten_ky}' vẫn ở trạng thái '{entry.trang_thai}'. Phải 'Posted' trước khi khóa sổ.")

        # Kiểm tra 2: Cân đối thử (có thể bỏ qua hoặc tính toán ở bước khác nếu cần chính xác cao)
        # ... (Logic phức tạp hơn, cần tính tổng toàn bộ dòng Nợ và Có trong kỳ)

        # Nếu tất cả kiểm tra đều đạt, cập nhật trạng thái
        self.repository.update_trang_thai(id, "Locked")
        print(f"[LOG] Kỳ '{ky.ten_ky}' (ID: {id}) đã được khóa bởi {nguoi_thuc_hien} vào {ky.ngay_ket_thuc}.")
        return True

    def mo_ky(self, id: int, ly_do: str, nguoi_thuc_hien: str = "System") -> bool:
        """
        Mở sổ kế toán cho kỳ đã cho.
        Yêu cầu: Phải có quyền Admin và lý do chính đáng.
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
        print(f"[LOG] Kỳ '{ky.ten_ky}' (ID: {id}) đã được mở bởi {nguoi_thuc_hien} với lý do: '{ly_do}'.")
        return True

    def is_ky_da_khoa(self, id: int) -> bool:
        """
        Kiểm tra xem kỳ đã bị khóa chưa.
        """
        ky = self.repository.get_by_id(id)
        if not ky:
            return False # Nếu kỳ không tồn tại, coi như chưa khóa
        return ky.trang_thai == "Locked"

    # (Có thể thêm các phương thức khác như cap_nhat_ky, xoa_ky nếu cần)