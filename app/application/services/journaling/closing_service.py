# app/application/services/journaling/closing_service.py
import logging
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from app.application.interfaces.account_repo import AccountRepositoryInterface
from app.application.interfaces.journal_entry_repo import (
    JournalEntryRepositoryInterface,
)
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine

logger = logging.getLogger(__name__)


class ClosingJournalEntryService:
    """
    [SRP] Chỉ chịu trách nhiệm kết chuyển cuối kỳ theo TT99 (không dùng TK 911).
    """

    def __init__(
        self,
        journal_repo: JournalEntryRepositoryInterface,
        account_repo: AccountRepositoryInterface,
    ):
        self.journal_repo = journal_repo
        self.account_repo = account_repo

    def execute(
        self, ky_hieu: str, ngay_ket_chuyen: date
    ) -> list[JournalEntry]:
        """
        [TT99-Đ24] Kết chuyển Doanh thu/Chi phí vào 421.
        """
        nam = ngay_ket_chuyen.year

        tk_doanh_thu = ["511", "512", "515"]
        tk_chi_phi = ["632", "641", "642", "635", "811", "821"]

        doanh_thu_tong = sum(
            self._tinh_phat_sinh_tai_khoan(tk, "CO", nam)
            for tk in tk_doanh_thu
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        chi_phi_tong = sum(
            self._tinh_phat_sinh_tai_khoan(tk, "NO", nam) for tk in tk_chi_phi
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        ket_chuyen_entries = []

        # Kết chuyển doanh thu: Nợ 511 → Có 421
        if doanh_thu_tong > 0:
            lines = [
                JournalEntryLine(
                    so_tai_khoan="421", no=Decimal(0), co=doanh_thu_tong
                )
            ]
            for tk in tk_doanh_thu:
                ps_co = self._tinh_phat_sinh_tai_khoan(tk, "CO", nam)
                if ps_co > 0:
                    lines.append(
                        JournalEntryLine(
                            so_tai_khoan=tk, no=ps_co, co=Decimal(0)
                        )
                    )

            bt = JournalEntry(
                ngay_ct=ngay_ket_chuyen,
                so_phieu=f"KC-DOANH-THU-{ky_hieu}",
                mo_ta=f"Kết chuyển doanh thu kỳ {ky_hieu} (TT99 Điều 24)",
                lines=lines,
                trang_thai="Draft",
            )
            bt = self.journal_repo.add(bt)
            self.journal_repo.update_status(bt.id, "Posted")
            ket_chuyen_entries.append(bt)

        # Kết chuyển chi phí: Nợ 421 → Có 632, 641...
        if chi_phi_tong > 0:
            lines = [
                JournalEntryLine(
                    so_tai_khoan="421", no=chi_phi_tong, co=Decimal(0)
                )
            ]
            for tk in tk_chi_phi:
                ps_no = self._tinh_phat_sinh_tai_khoan(tk, "NO", nam)
                if ps_no > 0:
                    lines.append(
                        JournalEntryLine(
                            so_tai_khoan=tk, no=Decimal(0), co=ps_no
                        )
                    )

            bt = JournalEntry(
                ngay_ct=ngay_ket_chuyen,
                so_phieu=f"KC-CHI-PHI-{ky_hieu}",
                mo_ta=f"Kết chuyển chi phí kỳ {ky_hieu} (TT99 Điều 24)",
                lines=lines,
                trang_thai="Draft",
            )
            bt = self.journal_repo.add(bt)
            self.journal_repo.update_status(bt.id, "Posted")
            ket_chuyen_entries.append(bt)

        logger.info(
            f"[KET_CHUYEN_THANH_CONG] Ky: {ky_hieu}, So bút toán: {len(ket_chuyen_entries)}"
        )
        return ket_chuyen_entries

    def _tinh_phat_sinh_tai_khoan(
        self, so_tai_khoan: str, loai_ps: str, nam: int
    ) -> Decimal:
        # Tính phát sinh Nợ hoặc Có của tài khoản trong năm
        ngay_dau = date(nam, 1, 1)
        ngay_ket = date(nam, 12, 31)
        all_entries = self.journal_repo.get_all_posted_in_range(
            ngay_dau, ngay_ket
        )
        tong = Decimal(0)
        for entry in all_entries:
            for line in entry.lines:
                if line.so_tai_khoan == so_tai_khoan:
                    tong += line.no if loai_ps == "NO" else line.co
        return tong.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
