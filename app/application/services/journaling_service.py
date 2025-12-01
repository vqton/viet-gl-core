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
        [Nghiệp vụ] Thực hiện kết chuyển cuối kỳ theo Thông tư 99/2025/TT-BTC.
        
        📌 BUSINESS RULE (TT99):
        - Điều 24: Cuối kỳ kế toán, doanh nghiệp phải kết chuyển toàn bộ doanh thu, 
        thu nhập khác và chi phí để xác định kết quả kinh doanh.
        - Phụ lục II: Hệ thống tài khoản KHÔNG CÓ tài khoản 911 "Xác định kết quả kinh doanh".
        - ➤ Do đó: KẾT CHUYỂN TRỰC TIẾP từ Doanh thu/Chi phí → Tài khoản 421 "Lợi nhuận sau thuế chưa phân phối".

        📌 LUỒNG KẾT CHUYỂN CHUẨN:
        1. NỢ các TK Doanh thu (511, 512, 515...) / CÓ 421 → Ghi nhận doanh thu vào lợi nhuận.
        2. NỢ 421 / CÓ các TK Chi phí (632, 641, 642, 635, 811...) → Ghi nhận chi phí làm giảm lợi nhuận.
        3. Số dư TK 421 sau kết chuyển = Lợi nhuận sau thuế chưa phân phối của kỳ.

        📌 LƯU Ý KỸ THUẬT:
        - Không tạo bút toán kết chuyển lãi/lỗ riêng (khác với TT200).
        - Tất cả bút toán kết chuyển đều ở trạng thái "Draft" → được ghi sổ ngay sau khi tạo.
        - Chỉ kết chuyển các tài khoản có phát sinh thực tế (tránh bút toán rỗng).

        📌 CẢNH BÁO VI PHẠM:
        - Nếu sử dụng TK 911 → VI PHẠM TT99 → Báo cáo tài chính KHÔNG HỢP LỆ.
        """
        nam = ngay_ket_chuyen.year

        # === 1. Danh sách tài khoản theo Phụ lục II TT99 ===
        tk_doanh_thu = ["511", "512", "515"]  # Phụ lục II, Mục V: Doanh thu
        tk_chi_phi = [
            "632",  # Giá vốn hàng bán
            "641",  # Chi phí bán hàng
            "642",  # Chi phí QLDN
            "635",  # Chi phí tài chính
            "811",  # Chi phí khác
            "821"   # Thuế TNDN hiện hành
        ]  # Phụ lục II, Mục VI: Chi phí

        # === 2. Tính tổng phát sinh trong năm ===
        doanh_thu_tong = sum(
            self._tinh_phat_sinh_tai_khoan(tk, "CO", nam) for tk in tk_doanh_thu
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        chi_phi_tong = sum(
            self._tinh_phat_sinh_tai_khoan(tk, "NO", nam) for tk in tk_chi_phi
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        ket_chuyen_entries = []

        # === 3. KẾT CHUYỂN DOANH THU → CÓ 421 (TRỰC TIẾP, KHÔNG QUA 911) ===
        if doanh_thu_tong > 0:
            lines_dt = []
            # Ghi NỢ từng TK doanh thu (theo phát sinh thực tế)
            for tk in tk_doanh_thu:
                ps_co = self._tinh_phat_sinh_tai_khoan(tk, "CO", nam)
                if ps_co > 0:
                    lines_dt.append(JournalEntryLine(
                        so_tai_khoan=tk,
                        no=ps_co,
                        co=Decimal(0)
                    ))
            # Ghi CÓ 421 → Tăng lợi nhuận
            lines_dt.append(JournalEntryLine(
                so_tai_khoan="421",
                no=Decimal(0),
                co=doanh_thu_tong
            ))
            bt_dt = JournalEntry(
                ngay_ct=ngay_ket_chuyen,
                so_phieu=f"KC-DOANH-THU-{ky_hieu}",
                mo_ta=f"Kết chuyển doanh thu kỳ {ky_hieu} (TT99 Điều 24)",
                lines=lines_dt,
                trang_thai="Draft"
            )
            bt_dt = self.tao_phieu_ke_toan(bt_dt)
            self.post_phieu_ke_toan(bt_dt.id)
            ket_chuyen_entries.append(bt_dt)

        # === 4. KẾT CHUYỂN CHI PHÍ → NỢ 421 (TRỰC TIẾP, KHÔNG QUA 911) ===
        if chi_phi_tong > 0:
            lines_cp = []
            # Ghi NỢ 421 → Giảm lợi nhuận
            lines_cp.append(JournalEntryLine(
                so_tai_khoan="421",
                no=chi_phi_tong,
                co=Decimal(0)
            ))
            # Ghi CÓ từng TK chi phí (theo phát sinh thực tế)
            for tk in tk_chi_phi:
                ps_no = self._tinh_phat_sinh_tai_khoan(tk, "NO", nam)
                if ps_no > 0:
                    lines_cp.append(JournalEntryLine(
                        so_tai_khoan=tk,
                        no=Decimal(0),
                        co=ps_no
                    ))
            bt_cp = JournalEntry(
                ngay_ct=ngay_ket_chuyen,
                so_phieu=f"KC-CHI-PHI-{ky_hieu}",
                mo_ta=f"Kết chuyển chi phí kỳ {ky_hieu} (TT99 Điều 24)",
                lines=lines_cp,
                trang_thai="Draft"
            )
            bt_cp = self.tao_phieu_ke_toan(bt_cp)
            self.post_phieu_ke_toan(bt_cp.id)
            ket_chuyen_entries.append(bt_cp)

        # === 5. KHÔNG CẦN BƯỚC KẾT CHUYỂN LÃI/LỖ ===
        # → Vì đã ghi trực tiếp vào 421, số dư 421 chính là kết quả kinh doanh ròng.
        # → Đảm bảo tuân thủ TT99 và tránh vi phạm do sử dụng TK 911.

        return ket_chuyen_entries
    
    def _tinh_phat_sinh_tai_khoan(self, so_tai_khoan: str, loai_ps: str, nam: int) -> Decimal:
        """
        Tính phát sinh Nợ hoặc Có của một tài khoản trong năm.
        loai_ps = 'NO' hoặc 'CO'
        """
        ngay_dau_nam = date(nam, 1, 1)
        ngay_ket_nam = date(nam, 12, 31)
        all_entries = self.repository.get_all_posted_in_range(ngay_dau_nam, ngay_ket_nam)
        tong = Decimal(0)
        for entry in all_entries:
            for line in entry.lines:
                if line.so_tai_khoan == so_tai_khoan:
                    if loai_ps == "NO":
                        tong += line.no
                    elif loai_ps == "CO":
                        tong += line.co
        return tong.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)