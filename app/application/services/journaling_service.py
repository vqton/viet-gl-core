from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from typing import List, Optional

# Domain Models
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine
from app.domain.models.journal_entry import JournalEntry as JournalEntryDomain, JournalEntryLine
from app.domain.models.account import TaiKhoan, LoaiTaiKhoan # Giữ lại cho mục đích type hinting nếu cần

# Repositories
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.infrastructure.repositories.account_repository import AccountRepository

# Services
from app.application.services.accounting_period_service import AccountingPeriodService

class JournalingService:
    """
    Service Layer quản lý các nghiệp vụ liên quan đến Bút toán Kế toán (Journal Entry).
    Bao gồm các kiểm tra nghiệp vụ như: tồn tại tài khoản, cân bằng Nợ/Có (Domain Entity lo), 
    và kiểm tra trạng thái khóa sổ của kỳ kế toán (Business Logic).
    """
    def __init__(self, 
                 repository: JournalEntryRepository, 
                 account_repository: AccountRepository,
                 accounting_period_service: AccountingPeriodService):
        self.repository = repository
        self.account_repository = account_repository
        self.accounting_period_service = accounting_period_service

    def _kiem_tra_khoa_so(self, ngay_ct: date):
        """
        Hàm tiện ích kiểm tra xem ngày chứng từ có thuộc kỳ đã khóa sổ hay không.
        Nếu kỳ đã khóa, sẽ raise ValueError.
        """
        ky_ke_toan = self.accounting_period_service.lay_ky_ke_toan_theo_ngay(ngay_ct)
        if not ky_ke_toan:
            # Có thể cho phép tạo nếu chưa có kỳ, hoặc bắt buộc phải có kỳ
            # Tùy theo logic nghiệp vụ. Ở đây, ta cho phép nhưng cảnh báo
            print(f"[WARN] Ngày {ngay_ct} không thuộc bất kỳ kỳ kế toán nào. Cho phép tạo.")
            return
        
        if ky_ke_toan.trang_thai == "Locked":
            raise ValueError(f"Kỳ kế toán '{ky_ke_toan.ten_ky}' (Ngày {ngay_ct.strftime('%Y-%m-%d')}) đã bị khóa. Không thể thực hiện nghiệp vụ.")

    def _kiem_tra_tai_khoan_ton_tai(self, lines: List[JournalEntryLine]):
        """
        Kiểm tra tất cả tài khoản trong các dòng bút toán có tồn tại không.
        """
        for line in lines:
            tai_khoan = self.account_repository.get_by_id(line.so_tai_khoan)
            if not tai_khoan:
                raise ValueError(f"Tài khoản '{line.so_tai_khoan}' không tồn tại trong hệ thống.")

    # --- CRUD Operations ---

    def tao_phieu_ke_toan(self, journal_entry_domain: JournalEntryDomain) -> JournalEntryDomain:
        """
        Tạo mới một bút toán kế toán.
        """
        # 1. Kiểm tra khóa sổ
        self._kiem_tra_khoa_so(journal_entry_domain.ngay_ct)
        
        # 2. Kiểm tra tài khoản tồn tại
        self._kiem_tra_tai_khoan_ton_tai(journal_entry_domain.lines)

        # 3. Kiểm tra hợp lệ Domain Entity (đã thực hiện trong __post_init__ của JournalEntry)

        # 4. Thiết lập trạng thái ban đầu và lưu
        journal_entry_domain.trang_thai = "Draft"
        return self.repository.add(journal_entry_domain)

    def lay_phieu_ke_toan(self, id: int) -> Optional[JournalEntryDomain]:
        """
        Lấy thông tin bút toán theo ID.
        """
        return self.repository.get_by_id(id)

    def lay_tat_ca_phieu_ke_toan(self) -> List[JournalEntryDomain]:
        """
        Lấy danh sách tất cả bút toán.
        """
        return self.repository.get_all()

    def cap_nhat_phieu_ke_toan(self, id: int, journal_entry_domain_updated: JournalEntryDomain) -> JournalEntryDomain:
        """
        Cập nhật bút toán kế toán hiện có.
        """
        journal_entry_hien_tai = self.repository.get_by_id(id)
        if not journal_entry_hien_tai:
            raise ValueError(f"Bút toán với ID {id} không tồn tại.")

        # 1. Chỉ cho phép cập nhật nếu bút toán đang ở trạng thái Draft
        if journal_entry_hien_tai.trang_thai != "Draft":
            raise ValueError(f"Không thể cập nhật bút toán ID {id} vì trạng thái là '{journal_entry_hien_tai.trang_thai}'. Chỉ có thể cập nhật bút toán ở trạng thái 'Draft'.")

        # 2. Kiểm tra khóa sổ (dựa trên ngày chứng từ mới/ngày hiện tại, tốt nhất nên dựa trên cả 2)
        # Nếu ngày chứng từ thay đổi, ta kiểm tra cả ngày cũ và ngày mới
        if journal_entry_domain_updated.ngay_ct != journal_entry_hien_tai.ngay_ct:
             self._kiem_tra_khoa_so(journal_entry_domain_updated.ngay_ct)
        
        # Kiểm tra khóa sổ của ngày cũ (nếu có, để tránh việc chuyển bút toán ra khỏi kỳ đã khóa)
        self._kiem_tra_khoa_so(journal_entry_hien_tai.ngay_ct)

        # 3. Kiểm tra tài khoản tồn tại cho từng dòng mới
        self._kiem_tra_tai_khoan_ton_tai(journal_entry_domain_updated.lines)

        # 4. Kiểm tra hợp lệ Entity (sẽ được gọi trong Repostory.update)
        
        # 5. Cập nhật ID và trạng thái (đảm bảo vẫn là Draft)
        journal_entry_domain_updated.id = id
        journal_entry_domain_updated.trang_thai = "Draft"

        # 6. Gọi Repository để cập nhật
        return self.repository.update(journal_entry_domain_updated)


    def xoa_phieu_ke_toan(self, id: int) -> bool:
        """
        Xóa một bút toán kế toán.
        """
        journal_entry = self.repository.get_by_id(id)
        if not journal_entry:
            return False

        # 1. Chỉ cho phép xóa nếu bút toán đang ở trạng thái Draft
        if journal_entry.trang_thai != "Draft":
            raise ValueError(f"Không thể xóa bút toán ID {id} vì trạng thái là '{journal_entry.trang_thai}'. Chỉ có thể xóa bút toán ở trạng thái 'Draft'.")

        # 2. Kiểm tra khóa sổ
        self._kiem_tra_khoa_so(journal_entry.ngay_ct)

        # 3. Gọi Repository để xóa
        return self.repository.delete(id)
    
    # --- State Management Operations ---

    def post_phieu_ke_toan(self, id: int) -> JournalEntryDomain:
        """
        Đăng sổ (Post) một bút toán kế toán (chuyển trạng thái sang 'Posted').
        """
        journal_entry = self.repository.get_by_id(id)
        if not journal_entry:
            raise ValueError(f"Bút toán với ID {id} không tồn tại.")
            
        # 1. Kiểm tra khóa sổ
        self._kiem_tra_khoa_so(journal_entry.ngay_ct)

        # 2. Kiểm tra trạng thái hiện tại
        if journal_entry.trang_thai == "Posted":
            raise ValueError(f"Bút toán ID {id} đã được đăng sổ rồi.")
        if journal_entry.trang_thai == "Locked":
             raise ValueError(f"Bút toán ID {id} đã bị khóa, không thể thay đổi trạng thái.")
        
        # 3. Cập nhật trạng thái và lưu
        journal_entry.trang_thai = "Posted"
        return self.repository.update_status(id, "Posted")

    def unpost_phieu_ke_toan(self, id: int) -> JournalEntryDomain:
        """
        Hủy đăng sổ (Unpost) một bút toán kế toán (chuyển trạng thái về 'Draft').
        """
        journal_entry = self.repository.get_by_id(id)
        if not journal_entry:
            raise ValueError(f"Bút toán với ID {id} không tồn tại.")
        
        # 1. Kiểm tra khóa sổ
        self._kiem_tra_khoa_so(journal_entry.ngay_ct)

        # 2. Kiểm tra trạng thái hiện tại
        if journal_entry.trang_thai == "Draft":
            raise ValueError(f"Bút toán ID {id} đang ở trạng thái Draft, không cần hủy đăng sổ.")
        if journal_entry.trang_thai == "Locked":
             raise ValueError(f"Bút toán ID {id} đã bị khóa, không thể thay đổi trạng thái.")

        # 3. Cập nhật trạng thái và lưu
        journal_entry.trang_thai = "Draft"
        return self.repository.update_status(id, "Draft")

    # Lưu ý: Cần thêm các phương thức tìm kiếm nâng cao (ví dụ: theo ngày, theo tài khoản, theo trạng thái)
    # Tùy thuộc vào yêu cầu của API.
    def ket_chuyen_cuoi_ky(self, ky_hieu: str, ngay_ket_chuyen: date) -> List[JournalEntry]:
        """
        [Nghiệp vụ] Thực hiện kết chuyển cuối kỳ theo TT99/2025/TT-BTC.
        
        Các bước:
        1. Kết chuyển doanh thu (TK 511, 512, 515) → Nợ 911 / Có Doanh thu
        2. Kết chuyển chi phí (TK 632, 641, 642, 635, 811) → Nợ Chi phí / Có 911
        3. Kết chuyển lãi/lỗ: 
        - Nếu LÃI: Nợ 911 / Có 421
        - Nếu LỖ: Nợ 421 / Có 911

        Yêu cầu:
        - Tất cả bút toán trong kỳ đã được Posted.
        - Tài khoản 911 và 421 phải tồn tại.
        """
        # 1. Lấy tất cả bút toán đã Posted trong kỳ
        # (Giả định bạn có phương thức get_all_posted_in_period hoặc tương đương)
        # Ở đây ta dùng get_all() và lọc theo trạng thái Posted
        all_entries = self.repository.get_all()
        posted_entries = [e for e in all_entries if e.trang_thai == "Posted"]

        # 2. Tính tổng phát sinh Có của doanh thu và Nợ của chi phí
        doanh_thu_tong = Decimal(0)
        chi_phi_tong = Decimal(0)

        # Tài khoản doanh thu (theo Phụ lục II TT99)
        tk_doanh_thu = ["511", "512", "515"]
        # Tài khoản chi phí
        tk_chi_phi = ["632", "641", "642", "635", "811"]

        for entry in posted_entries:
            for line in entry.lines:
                if line.so_tai_khoan in tk_doanh_thu:
                    doanh_thu_tong += line.co  # Doanh thu ghi Có
                elif line.so_tai_khoan in tk_chi_phi:
                    chi_phi_tong += line.no    # Chi phí ghi Nợ

        # Làm tròn 2 chữ số thập phân
        doanh_thu_tong = doanh_thu_tong.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        chi_phi_tong = chi_phi_tong.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        ket_chuyen_entries = []

        # 3. Bút toán kết chuyển doanh thu: Nợ 911 / Có Doanh thu
        if doanh_thu_tong > 0:
            lines_dt = []
            # Ghi Nợ 911
            lines_dt.append(JournalEntryLine(so_tai_khoan="911", no=doanh_thu_tong, co=Decimal(0)))
            # Ghi Có từng TK doanh thu (đơn giản hóa: gộp chung)
            for tk in tk_doanh_thu:
                # Tính tổng Có từng TK (nếu cần chi tiết)
                pass
            # Gộp chung: Có tổng doanh thu
            lines_dt.append(JournalEntryLine(so_tai_khoan="511", no=Decimal(0), co=doanh_thu_tong))
            bt_dt = JournalEntry(
                ngay_ct=ngay_ket_chuyen,
                so_phieu=f"KC-DOANH-THU-{ky_hieu}",
                mo_ta=f"Kết chuyển doanh thu kỳ {ky_hieu}",
                lines=lines_dt,
                trang_thai="Draft"
            )
            bt_dt = self.tao_phieu_ke_toan(bt_dt)
            ket_chuyen_entries.append(bt_dt)

        # 4. Bút toán kết chuyển chi phí: Nợ Chi phí / Có 911
        if chi_phi_tong > 0:
            lines_cp = []
            # Ghi Nợ tổng chi phí (gộp)
            lines_cp.append(JournalEntryLine(so_tai_khoan="632", no=chi_phi_tong, co=Decimal(0)))
            # Ghi Có 911
            lines_cp.append(JournalEntryLine(so_tai_khoan="911", no=Decimal(0), co=chi_phi_tong))
            bt_cp = JournalEntry(
                ngay_ct=ngay_ket_chuyen,
                so_phieu=f"KC-CHI-PHI-{ky_hieu}",
                mo_ta=f"Kết chuyển chi phí kỳ {ky_hieu}",
                lines=lines_cp,
                trang_thai="Draft"
            )
            bt_cp = self.tao_phieu_ke_toan(bt_cp)
            ket_chuyen_entries.append(bt_cp)

        # 5. Tính lãi/lỗ
        lai_lo = doanh_thu_tong - chi_phi_tong
        lai_lo = lai_lo.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        if lai_lo != 0:
            lines_kqkd = []
            if lai_lo > 0:
                # LÃI: Nợ 911 / Có 421
                lines_kqkd.append(JournalEntryLine(so_tai_khoan="911", no=lai_lo, co=Decimal(0)))
                lines_kqkd.append(JournalEntryLine(so_tai_khoan="421", no=Decimal(0), co=lai_lo))
                mo_ta = f"Kết chuyển LÃI kỳ {ky_hieu}"
            else:
                # LỖ: Nợ 421 / Có 911
                loss = abs(lai_lo)
                lines_kqkd.append(JournalEntryLine(so_tai_khoan="421", no=loss, co=Decimal(0)))
                lines_kqkd.append(JournalEntryLine(so_tai_khoan="911", no=Decimal(0), co=loss))
                mo_ta = f"Kết chuyển LỖ kỳ {ky_hieu}"

            bt_kqkd = JournalEntry(
                ngay_ct=ngay_ket_chuyen,
                so_phieu=f"KC-KQKD-{ky_hieu}",
                mo_ta=mo_ta,
                lines=lines_kqkd,
                trang_thai="Draft"
            )
            bt_kqkd = self.tao_phieu_ke_toan(bt_kqkd)
            ket_chuyen_entries.append(bt_kqkd)

        # 6. Đăng sổ (Post) các bút toán kết chuyển
        for bt in ket_chuyen_entries:
            self.post_phieu_ke_toan(bt.id)

        return ket_chuyen_entries