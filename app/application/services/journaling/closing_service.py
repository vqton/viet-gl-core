# app/application/services/journaling/closing_service.py
"""
[SRP] Service kết chuyển cuối kỳ theo TT99/2025/TT-BTC.
[TT99-Đ24] Yêu cầu:
  - Không sử dụng tài khoản 911 ("Xác định kết quả kinh doanh").
  - Kết chuyển trực tiếp Doanh thu/Chi phí vào tài khoản 421 ("Lợi nhuận sau thuế chưa phân phối").
  - Hỗ trợ kết chuyển theo **kỳ tùy biến** (không chỉ năm dương lịch) → linh hoạt cho doanh nghiệp.

🎯 Mục tiêu:
  - Tính phát sinh Doanh thu/Chi phí trong khoảng [ngay_bat_dau, ngay_ket_thuc].
  - Tạo 1–2 bút toán kết chuyển:
      1. Kết chuyển Doanh thu: Nợ các TK Doanh thu → Có 421
      2. Kết chuyển Chi phí: Nợ 421 → Có các TK Chi phí
  - Trả về danh sách bút toán đã ghi sổ.
"""

import logging
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import List

from app.application.interfaces.account_repo import AccountRepositoryInterface
from app.application.interfaces.journal_entry_repo import (
    JournalEntryRepositoryInterface,
)
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine

logger = logging.getLogger(__name__)


class ClosingJournalEntryService:
    """[SRP] Chỉ chịu trách nhiệm kết chuyển cuối kỳ theo TT99 (không dùng TK 911)."""

    def __init__(
        self,
        journal_repo: JournalEntryRepositoryInterface,
        account_repo: AccountRepositoryInterface,
    ):
        self.journal_repo = journal_repo
        self.account_repo = account_repo

    def execute(
        self, ky_hieu: str, ngay_bat_dau: date, ngay_ket_thuc: date
    ) -> List[JournalEntry]:
        """
        [TT99-Đ24] Kết chuyển Doanh thu/Chi phí vào 421 trong khoảng [ngay_bat_dau, ngay_ket_thuc].

        Quy trình nghiệp vụ:
        1. Chỉ xử lý các **bút toán đã ghi sổ (Posted)** trong kỳ.
        2. **Doanh thu** (511, 512, 515):
           - Phát sinh Có → kết chuyển bằng bút toán: **Nợ TK Doanh thu / Có 421**.
        3. **Chi phí** (632, 641, 642, 635, 811, 821):
           - Phát sinh Nợ → kết chuyển bằng bút toán: **Nợ 421 / Có TK Chi phí**.
        4. Không tạo bút toán nếu không có phát sinh.

        Args:
            ky_hieu: Ký hiệu kỳ kế toán (VD: "Q4-2025", "Năm 2025").
            ngay_bat_dau: Ngày bắt đầu kỳ (bao gồm).
            ngay_ket_thuc: Ngày kết thúc kỳ (bao gồm).

        Returns:
            Danh sách bút toán kết chuyển đã được ghi sổ.

        Raises:
            ValueError: Nếu có lỗi nghiệp vụ (ít xảy ra do đã validate ở tầng service).
        """
        # Danh sách tài khoản Doanh thu theo TT99 Phụ lục II
        tk_doanh_thu = ["511", "512", "515"]
        # Danh sách tài khoản Chi phí theo TT99 Phụ lục II
        tk_chi_phi = ["632", "641", "642", "635", "811", "821"]

        # Tính tổng phát sinh Có của Doanh thu trong kỳ
        doanh_thu_tong = sum(
            self._tinh_phat_sinh_tai_khoan(tk, "CO", ngay_bat_dau, ngay_ket_thuc)
            for tk in tk_doanh_thu
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        # Tính tổng phát sinh Nợ của Chi phí trong kỳ
        chi_phi_tong = sum(
            self._tinh_phat_sinh_tai_khoan(tk, "NO", ngay_bat_dau, ngay_ket_thuc)
            for tk in tk_chi_phi
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        ket_chuyen_entries = []

        # → KẾT CHUYỂN DOANH THU: Nợ TK Doanh thu → Có 421
        if doanh_thu_tong > 0:
            lines = [
                JournalEntryLine(so_tai_khoan="421", no=Decimal(0), co=doanh_thu_tong)
            ]
            for tk in tk_doanh_thu:
                ps_co = self._tinh_phat_sinh_tai_khoan(
                    tk, "CO", ngay_bat_dau, ngay_ket_thuc
                )
                if ps_co > 0:
                    lines.append(
                        JournalEntryLine(so_tai_khoan=tk, no=ps_co, co=Decimal(0))
                    )
            bt = JournalEntry(
                ngay_ct=ngay_ket_thuc,
                so_phieu=f"KC-DOANH-THU-{ky_hieu}",
                mo_ta=f"Kết chuyển doanh thu kỳ {ky_hieu} (TT99 Điều 24)",
                lines=lines,
                trang_thai="Draft",
            )
            bt = self.journal_repo.add(bt)
            self.journal_repo.update_status(bt.id, "Posted")
            ket_chuyen_entries.append(bt)

        # → KẾT CHUYỂN CHI PHÍ: Nợ 421 → Có TK Chi phí
        if chi_phi_tong > 0:
            lines = [
                JournalEntryLine(so_tai_khoan="421", no=chi_phi_tong, co=Decimal(0))
            ]
            for tk in tk_chi_phi:
                ps_no = self._tinh_phat_sinh_tai_khoan(
                    tk, "NO", ngay_bat_dau, ngay_ket_thuc
                )
                if ps_no > 0:
                    lines.append(
                        JournalEntryLine(so_tai_khoan=tk, no=Decimal(0), co=ps_no)
                    )
            bt = JournalEntry(
                ngay_ct=ngay_ket_thuc,
                so_phieu=f"KC-CHI-PHI-{ky_hieu}",
                mo_ta=f"Kết chuyển chi phí kỳ {ky_hieu} (TT99 Điều 24)",
                lines=lines,
                trang_thai="Draft",
            )
            bt = self.journal_repo.add(bt)
            self.journal_repo.update_status(bt.id, "Posted")
            ket_chuyen_entries.append(bt)

        logger.info(
            f"[KET_CHUYEN_THANH_CONG] Kỳ: {ky_hieu}, "
            f"Số bút toán: {len(ket_chuyen_entries)}"
        )
        return ket_chuyen_entries

    def _tinh_phat_sinh_tai_khoan(
        self, so_tai_khoan: str, loai_ps: str, bd: date, kt: date
    ) -> Decimal:
        """
        Tính phát sinh Nợ/Có của một tài khoản (hoặc nhóm tài khoản bắt đầu bằng `so_tai_khoan`)
        trong khoảng [bd, kt] từ các bút toán **đã ghi sổ**.

        Ví dụ:
          - `_tinh_phat_sinh_tai_khoan("511", "CO", ..., ...)` → tổng Có TK 511
          - `_tinh_phat_sinh_tai_khoan("131", "NO", ..., ...)` → tổng Nợ TK 131 (bao gồm 1311, 1312...)

        Args:
            so_tai_khoan: Mã tài khoản gốc (VD: "511", "131").
            loai_ps: "NO" hoặc "CO".
            bd: Ngày bắt đầu.
            kt: Ngày kết thúc.

        Returns:
            Tổng phát sinh (>=0), làm tròn 2 chữ số thập phân.
        """
        all_entries = self.journal_repo.get_all_posted_in_range(bd, kt)
        tong = Decimal(0)
        for entry in all_entries:
            for line in entry.lines:
                if line.so_tai_khoan.startswith(so_tai_khoan):
                    tong += line.no if loai_ps == "NO" else line.co
        return tong.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
