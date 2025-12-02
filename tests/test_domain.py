# tests/test_domain.py
from datetime import date
from decimal import Decimal

import pytest

from app.domain.models.account import LoaiTaiKhoan, TaiKhoan
from app.domain.models.accounting_period import KyKeToan
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine

# --- TEST TÀI KHOẢN (Phụ lục II TT99) ---


def test_tai_khoan_chuan_tt99():
    """
    [TT99-PL2] Kiểm tra hệ thống tài khoản theo Phụ lục II.
    - Điều 11: Áp dụng hệ thống tài khoản tại Phụ lục II.
    - Không có nhóm 9xx → không tồn tại TK 911.
    """
    # TÀI SẢN (1xx)
    tk_111 = TaiKhoan(
        so_tai_khoan="111",
        ten_tai_khoan="Tiền mặt",
        loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
        cap_tai_khoan=1,
    )
    assert tk_111.loai_tai_khoan == LoaiTaiKhoan.TAI_SAN

    # VỐN CHỦ SỞ HỮU (4xx)
    tk_421 = TaiKhoan(
        so_tai_khoan="421",
        ten_tai_khoan="Lợi nhuận sau thuế chưa phân phối",
        loai_tai_khoan=LoaiTaiKhoan.VON_CHU_SO_HUU,
        cap_tai_khoan=1,
    )
    assert tk_421.loai_tai_khoan == LoaiTaiKhoan.VON_CHU_SO_HUU

    # DOANH THU (5xx)
    tk_511 = TaiKhoan(
        so_tai_khoan="511",
        ten_tai_khoan="Doanh thu bán hàng",
        loai_tai_khoan=LoaiTaiKhoan.DOANH_THU,
        cap_tai_khoan=1,
    )
    assert tk_511.loai_tai_khoan == LoaiTaiKhoan.DOANH_THU

    # CHI PHÍ (6xx)
    tk_632 = TaiKhoan(
        so_tai_khoan="632",
        ten_tai_khoan="Giá vốn hàng bán",
        loai_tai_khoan=LoaiTaiKhoan.CHI_PHI,
        cap_tai_khoan=1,
    )
    assert tk_632.loai_tai_khoan == LoaiTaiKhoan.CHI_PHI

    # KHÔNG TỒN TẠI TK 911
    # --> Không có validation trong domain model, nhưng trong seeder không thêm TK 911
    # --> Hệ thống không bao giờ sử dụng TK 911 → tuân thủ TT99.


def test_tai_khoan_cap_bac_hop_le():
    """
    [TT99-PL2] Kiểm tra cấp tài khoản hợp lệ (1-3).
    Tài khoản cấp con phải có tài khoản cha.
    """
    tk_3331 = TaiKhoan(
        so_tai_khoan="3331",
        ten_tai_khoan="Thuế GTGT phải nộp",
        loai_tai_khoan=LoaiTaiKhoan.NO_PHAI_TRA,
        cap_tai_khoan=2,
        so_tai_khoan_cha="333",
    )
    assert tk_3331.so_tai_khoan_cha == "333"
    assert tk_3331.cap_tai_khoan == 2


def test_tai_khoan_cap_2_khong_co_cha_that_bai():
    """
    [TT99-PL2] Tài khoản cấp 2 phải có tài khoản cha.
    """
    with pytest.raises(ValueError, match="Tài khoản cấp con"):
        TaiKhoan(
            so_tai_khoan="1111",
            ten_tai_khoan="Tiền mặt chi nhánh A",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
            cap_tai_khoan=2,
            so_tai_khoan_cha=None,
        )


# --- TEST BÚT TOÁN (Điều 24 TT99) ---


def test_journal_entry_can_bang():
    """
    [TT99-Đ24] Bút toán phải cân bằng Nợ = Có.
    """
    entry = JournalEntry(
        so_phieu="PT-001",
        ngay_ct=date.today(),
        lines=[
            JournalEntryLine(
                so_tai_khoan="111", no=Decimal("100"), co=Decimal("0")
            ),
            JournalEntryLine(
                so_tai_khoan="331", no=Decimal("0"), co=Decimal("100")
            ),
        ],
    )
    assert entry.tong_no == entry.tong_co


def test_journal_entry_khong_can_bang_that_bai():
    """
    [TT99-Đ24] Bút toán không cân bằng → lỗi.
    """
    with pytest.raises(ValueError, match="Bút toán không cân bằng"):
        JournalEntry(
            so_phieu="PT-002",
            ngay_ct=date.today(),
            lines=[
                JournalEntryLine(
                    so_tai_khoan="111", no=Decimal("100"), co=Decimal("0")
                ),
                JournalEntryLine(
                    so_tai_khoan="331", no=Decimal("0"), co=Decimal("90")
                ),
            ],
        )


def test_journal_entry_line_khong_duoc_ghi_ca_no_va_co():
    """
    [TT99-Đ24] Mỗi dòng bút toán chỉ được ghi Nợ hoặc Có.
    """
    with pytest.raises(ValueError, match="chỉ được ghi Nợ hoặc Có"):
        JournalEntryLine(
            so_tai_khoan="111", no=Decimal("100"), co=Decimal("100")
        )


def test_journal_entry_it_nhat_2_dong():
    """
    [TT99-Đ24] Bút toán phải có ít nhất 2 dòng.
    """
    with pytest.raises(ValueError, match="ít nhất 2 dòng"):
        JournalEntry(
            so_phieu="PT-003",
            ngay_ct=date.today(),
            lines=[
                JournalEntryLine(
                    so_tai_khoan="111", no=Decimal("100"), co=Decimal("0")
                )
            ],
        )


# --- TEST KỲ KẾ TOÁN (Điều 25 TT99) ---


def test_ky_ke_toan_hop_le():
    """
    [TT99-Đ25] Kỳ kế toán có ngày bắt đầu <= ngày kết thúc.
    """
    ky = KyKeToan(
        ten_ky="Q1-2025",
        ngay_bat_dau=date(2025, 1, 1),
        ngay_ket_thuc=date(2025, 3, 31),
        trang_thai="Open",
    )
    assert ky.ngay_bat_dau <= ky.ngay_ket_thuc


def test_ky_ke_toan_ngay_sai_that_bai():
    """
    [TT99-Đ25] Ngày bắt đầu > kết thúc → lỗi.
    """
    with pytest.raises(
        ValueError, match="Ngày bắt đầu không thể sau ngày kết thúc"
    ):
        KyKeToan(
            ten_ky="Q2-2025",
            ngay_bat_dau=date(2025, 4, 1),
            ngay_ket_thuc=date(2025, 3, 31),
            trang_thai="Open",
        )
