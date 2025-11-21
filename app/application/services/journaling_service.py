# File: app/application/services/journaling_service.py

from datetime import date
from decimal import Decimal
from typing import List, Optional
from app.domain.models.journal_entry import JournalEntry as JournalEntryDomain
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.infrastructure.repositories.account_repository import AccountRepository # Thêm import để kiểm tra
from app.domain.models.journal_entry import JournalEntry
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine
from app.domain.models.account import TaiKhoan, LoaiTaiKhoan
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.infrastructure.repositories.account_repository import AccountRepository
class JournalingService:
    def __init__(self, repository: JournalEntryRepository, account_repository: AccountRepository):
        self.repository = repository
        self.account_repository = account_repository # Dùng để kiểm tra tài khoản trong service

    def tao_phieu_ke_toan(self, journal_entry_domain: JournalEntry) -> JournalEntry:
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
    def ket_chuyen_cuoi_ky(self, ky_hieu: str, ngay_ket_chuyen: date) -> List[JournalEntry]:
        """
        Tự động tạo bút toán kết chuyển cuối kỳ cho doanh thu, chi phí.
        Áp dụng theo nguyên tắc kế toán và TT99/2025/TT-BTC.

        Args:
            ky_hieu (str): Ký hiệu kỳ kế toán (ví dụ: "Q4-2025", "Năm 2025").
            ngay_ket_chuyen (date): Ngày thực hiện kết chuyển.

        Returns:
            List[JournalEntry]: Danh sách các bút toán kết chuyển đã tạo.
        """
        # Bước 1: Truy vấn tất cả các bút toán của kỳ cần kết chuyển (giả sử repository có phương thức lọc theo kỳ)
        # (Hiện tại, repository chưa có phương thức lọc theo kỳ cụ thể, ta giả định lấy tất cả hoặc sẽ bổ sung sau)
        # Để đơn giản trong ví dụ này, ta giả định tất cả các bút toán trong DB là của kỳ cần kết chuyển.
        all_entries = self.repository.get_all() # Cần có logic lọc theo kỳ thực tế sau

        # Bước 2: Tính tổng phát sinh Nợ/Có cho các tài khoản Doanh thu (5xx) và Chi phí (6xx, 811)
        # Sử dụng một dictionary để lưu tổng phát sinh
        phat_sinh_doanh_thu = {} # {so_tai_khoan: (tong_no, tong_co)}
        phat_sinh_chi_phi = {}

        for entry in all_entries:
            # Chỉ xét các bút toán đã "Posted"
            if entry.trang_thai != "Posted":
                continue # Bỏ qua bút toán chưa được ghi sổ chính thức

            for line in entry.lines:
                so_tai_khoan = line.so_tai_khoan
                tai_khoan_chi_tiet = self.account_repository.get_by_id(so_tai_khoan)
                if not tai_khoan_chi_tiet:
                    # Nên log hoặc báo lỗi nếu tài khoản trong bút toán không tồn tại
                    continue

                # Phân loại tài khoản
                if tai_khoan_chi_tiet.loai_tai_khoan == LoaiTaiKhoan.DOANH_THU:
                    if so_tai_khoan not in phat_sinh_doanh_thu:
                        phat_sinh_doanh_thu[so_tai_khoan] = [Decimal('0'), Decimal('0')]
                    phat_sinh_doanh_thu[so_tai_khoan][0] += line.no # Tổng phát sinh Nợ
                    phat_sinh_doanh_thu[so_tai_khoan][1] += line.co # Tổng phát sinh Có

                elif tai_khoan_chi_tiet.loai_tai_khoan == LoaiTaiKhoan.CHI_PHI:
                    if so_tai_khoan not in phat_sinh_chi_phi:
                        phat_sinh_chi_phi[so_tai_khoan] = [Decimal('0'), Decimal('0')]
                    phat_sinh_chi_phi[so_tai_khoan][0] += line.no # Tổng phát sinh Nợ
                    phat_sinh_chi_phi[so_tai_khoan][1] += line.co # Tổng phát sinh Có

        # Bước 3: Tạo bút toán kết chuyển
        danh_sach_buoc_toan_ket_chuyen = []

        # Kết chuyển Doanh thu (TK 5xx) sang Nợ TK 911
        # Tổng số dư Có của các TK 5xx sẽ được ghi Nợ TK 911
        tong_doanh_thu = Decimal('0')
        for so_tk, (tong_no, tong_co) in phat_sinh_doanh_thu.items():
            # Số dư cuối kỳ của TK Doanh thu = Tổng Có - Tổng Nợ (vì TK Doanh thu tăng bên Có)
            so_du = tong_co - tong_no
            if so_du > 0: # Có số dư Có -> cần kết chuyển
                tong_doanh_thu += so_du

        if tong_doanh_thu > 0:
            lines_ket_chuyen_dt = []
            # Ghi Nợ TK 911
            lines_ket_chuyen_dt.append(JournalEntryLine(
                so_tai_khoan="911",
                no=tong_doanh_thu,
                co=Decimal('0'),
                mo_ta=f"Kết chuyển doanh thu kỳ {ky_hieu}"
            ))
            # Ghi Có các TK 5xx
            for so_tk, (tong_no, tong_co) in phat_sinh_doanh_thu.items():
                so_du = tong_co - tong_no
                if so_du > 0:
                    lines_ket_chuyen_dt.append(JournalEntryLine(
                        so_tai_khoan=so_tk,
                        no=Decimal('0'),
                        co=so_du,
                        mo_ta=f"Kết chuyển doanh thu kỳ {ky_hieu}"
                    ))

            buoc_toan_ket_chuyen_dt = JournalEntry(
                ngay_ct=ngay_ket_chuyen,
                so_phieu=f"KT-DOANH-THU-{ky_hieu}",
                mo_ta=f"Bút toán kết chuyển doanh thu cuối kỳ {ky_hieu}",
                lines=lines_ket_chuyen_dt,
                trang_thai="Posted" # Bút toán kết chuyển thường được ghi nhận ngay là "Posted"
            )
            danh_sach_buoc_toan_ket_chuyen.append(buoc_toan_ket_chuyen_dt)

        # Kết chuyển Chi phí (TK 6xx, 811) sang Có TK 911
        # Tổng số dư Nợ của các TK 6xx, 811 sẽ được ghi Có TK 911
        tong_chi_phi = Decimal('0')
        for so_tk, (tong_no, tong_co) in phat_sinh_chi_phi.items():
            # Số dư cuối kỳ của TK Chi phí = Tổng Nợ - Tổng Có (vì TK Chi phí tăng bên Nợ)
            so_du = tong_no - tong_co
            if so_du > 0: # Có số dư Nợ -> cần kết chuyển
                tong_chi_phi += so_du

        if tong_chi_phi > 0:
            lines_ket_chuyen_cp = []
            # Ghi Nợ các TK 6xx, 811
            for so_tk, (tong_no, tong_co) in phat_sinh_chi_phi.items():
                so_du = tong_no - tong_co
                if so_du > 0:
                    lines_ket_chuyen_cp.append(JournalEntryLine(
                        so_tai_khoan=so_tk,
                        no=so_du,
                        co=Decimal('0'),
                        mo_ta=f"Kết chuyển chi phí kỳ {ky_hieu}"
                    ))
            # Ghi Có TK 911
            lines_ket_chuyen_cp.append(JournalEntryLine(
                so_tai_khoan="911",
                no=Decimal('0'),
                co=tong_chi_phi,
                mo_ta=f"Kết chuyển chi phí kỳ {ky_hieu}"
            ))

            buoc_toan_ket_chuyen_cp = JournalEntry(
                ngay_ct=ngay_ket_chuyen,
                so_phieu=f"KT-CHI-PHI-{ky_hieu}",
                mo_ta=f"Bút toán kết chuyển chi phí cuối kỳ {ky_hieu}",
                lines=lines_ket_chuyen_cp,
                trang_thai="Posted"
            )
            danh_sach_buoc_toan_ket_chuyen.append(buoc_toan_ket_chuyen_cp)

        # Bước 4: Tạo bút toán kết chuyển Lợi nhuận/Lỗ từ 911 sang 421 (giả sử không có thuế TNDN ở bước này, hoặc đã được kết chuyển riêng)
        # Lợi nhuận = Tổng Doanh thu - Tổng Chi phí
        # Bước 4: Tạo bút toán kết chuyển Lợi nhuận/Lỗ từ 911 sang 421
        loi_nhuan_truoc_thue = tong_doanh_thu - tong_chi_phi
        if loi_nhuan_truoc_thue != 0:
            lines_ket_chuyen_911 = []
            if loi_nhuan_truoc_thue > 0: # Lợi nhuận: SD 911 là Nợ (vì đã ghi Nợ DT, ghi Có CP). Kết chuyển SD Nợ: Ghi Có 911. Ghi nhận vào VCSH: Ghi Nợ 421.
                lines_ket_chuyen_911.append(JournalEntryLine(
                    so_tai_khoan="911",
                    no=Decimal('0'), # Sai trước đây
                    co=loi_nhuan_truoc_thue # Sai trước đây: Đây là cách kết chuyển SD Nợ của 911
                ))
                lines_ket_chuyen_911.append(JournalEntryLine(
                    so_tai_khoan="421",
                    no=loi_nhuan_truoc_thue, # Sai trước đây: Lợi nhuận làm tăng VCSH -> Ghi Nợ
                    co=Decimal('0')
                ))
            elif loi_nhuan_truoc_thue < 0: # Lỗ: SD 911 là Có (vì SD CP > SD DT). Kết chuyển SD Có: Ghi Nợ 911. Ghi nhận vào VCSH (giảm): Ghi Có 421.
                loi_nhuan_truoc_thue_abs = abs(loi_nhuan_truoc_thue)
                lines_ket_chuyen_911.append(JournalEntryLine(
                    so_tai_khoan="911",
                    no=loi_nhuan_truoc_thue_abs, # Sai trước đây: Đây là cách kết chuyển SD Có của 911
                    co=Decimal('0') # Sai trước đây
                ))
                lines_ket_chuyen_911.append(JournalEntryLine(
                    so_tai_khoan="421",
                    no=Decimal('0'), # Sai trước đây: Lỗ làm giảm VCSH -> Ghi Có
                    co=loi_nhuan_truoc_thue_abs
                ))

            buoc_toan_ket_chuyen_911 = JournalEntry(
                ngay_ct=ngay_ket_chuyen,
                so_phieu=f"KT-KQKD-{ky_hieu}",
                mo_ta=f"Bút toán kết chuyển kết quả kinh doanh cuối kỳ {ky_hieu}",
                lines=lines_ket_chuyen_911,
                trang_thai="Posted"
            )
            danh_sach_buoc_toan_ket_chuyen.append(buoc_toan_ket_chuyen_911)


        # Bước 5: Lưu các bút toán kết chuyển vào DB
        buoc_toan_da_luu = []
        for buoc_toan in danh_sach_buoc_toan_ket_chuyen:
            # Kiểm tra hợp lệ (cân bằng, tài khoản tồn tại) - có thể bỏ qua nếu chắc chắn logic tạo đúng
            # tao_phieu_ke_toan sẽ thực hiện kiểm tra này
            buoc_toan_luu = self.tao_phieu_ke_toan(buoc_toan)
            buoc_toan_da_luu.append(buoc_toan_luu)

        return buoc_toan_da_luu
    
    def _xac_dinh_ky_cho_ngay(self, ngay_ct: date) -> Optional[int]:
        """
        Xác định ID kỳ kế toán cho một ngày chứng từ.
        Trả về ID kỳ nếu tìm thấy, None nếu không tìm thấy kỳ phù hợp.
        """
        # Lấy danh sách tất cả các kỳ
        danh_sach_ky = self.accounting_period_service.lay_danh_sach_ky_ke_toan()
        for ky in danh_sach_ky:
            if ky.ngay_bat_dau <= ngay_ct <= ky.ngay_ket_thuc:
                return ky.id
        return None

    def tao_phieu_ke_toan(self, journal_entry_domain: JournalEntry) -> JournalEntry:
        """
        Tạo mới một bút toán kế toán.
        - Kiểm tra hợp lệ đã được thực hiện trong Domain Entity (kiem_tra_can_bang).
        - Kiểm tra tài khoản có tồn tại trong hệ thống hay không (tại Application Layer).
        - Kiểm tra xem kỳ của ngày chứng từ đã bị khóa chưa.
        - Gọi Repository để lưu vào DB.
        """
        # Kiểm tra khóa sổ
        id_ky = self._xac_dinh_ky_cho_ngay(journal_entry_domain.ngay_ct)
        if id_ky and self.accounting_period_service.is_ky_da_khoa(id_ky):
            raise ValueError(f"Không thể tạo bút toán cho ngày {journal_entry_domain.ngay_ct.strftime('%Y-%m-%d')}. Kỳ kế toán đã bị khóa.")

        # Kiểm tra tài khoản tồn tại cho từng dòng trong bút toán
        for line in journal_entry_domain.lines:
            tai_khoan = self.account_repository.get_by_id(line.so_tai_khoan)
            if not tai_khoan:
                raise ValueError(f"Tài khoản '{line.so_tai_khoan}' không tồn tại trong hệ thống.")

        # Gọi Repository để thêm vào DB
        # (Lưu ý: Logic kiểm tra cân bằng `kiem_tra_can_bang` đã được thực hiện
        # trong `__post_init__` của `JournalEntryDomain` khi nó được tạo ra từ API)
        return self.repository.add(journal_entry_domain)

    def cap_nhat_phieu_ke_toan(self, id: int, journal_entry_domain_updated: JournalEntry) -> Optional[JournalEntry]:
        """
        Cập nhật một bút toán kế toán.
        - Kiểm tra xem bút toán có tồn tại không.
        - Kiểm tra xem kỳ của ngày chứng từ đã bị khóa chưa.
        - Kiểm tra hợp lệ (cân bằng, tài khoản tồn tại).
        - Gọi Repository để cập nhật.
        """
        # Lấy bút toán hiện tại để kiểm tra ngày
        journal_entry_hien_tai = self.repository.get_by_id(id)
        if not journal_entry_hien_tai:
            return None

        # Kiểm tra khóa sổ
        id_ky = self._xac_dinh_ky_cho_ngay(journal_entry_hien_tai.ngay_ct)
        if id_ky and self.accounting_period_service.is_ky_da_khoa(id_ky):
            raise ValueError(f"Không thể cập nhật bút toán {id} cho ngày {journal_entry_hien_tai.ngay_ct.strftime('%Y-%m-%d')}. Kỳ kế toán đã bị khóa.")

        # Kiểm tra tài khoản tồn tại cho từng dòng mới
        for line in journal_entry_domain_updated.lines:
            tai_khoan = self.account_repository.get_by_id(line.so_tai_khoan)
            if not tai_khoan:
                raise ValueError(f"Tài khoản '{line.so_tai_khoan}' không tồn tại trong hệ thống.")

        # Gọi Repository để cập nhật DB
        return self.repository.update(id, journal_entry_domain_updated)

    def xoa_phieu_ke_toan(self, id: int) -> bool:
        """
        Xóa một bút toán kế toán.
        - Kiểm tra xem bút toán có tồn tại không.
        - Kiểm tra xem kỳ của ngày chứng từ đã bị khóa chưa.
        - Gọi Repository để xóa.
        """
        # Lấy bút toán để kiểm tra ngày
        journal_entry = self.repository.get_by_id(id)
        if not journal_entry:
            return False

        # Kiểm tra khóa sổ
        id_ky = self._xac_dinh_ky_cho_ngay(journal_entry.ngay_ct)
        if id_ky and self.accounting_period_service.is_ky_da_khoa(id_ky):
            raise ValueError(f"Không thể xóa bút toán {id} cho ngày {journal_entry.ngay_ct.strftime('%Y-%m-%d')}. Kỳ kế toán đã bị khóa.")

        # Gọi Repository để xóa DB
        return self.repository.delete(id)