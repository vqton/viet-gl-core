# tests/test_reporting_service.py

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, Mock

import pytest

# Import các thành phần cần test
from app.application.services.reporting_service import ReportingService
from app.domain.models.account import LoaiTaiKhoan, TaiKhoan
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine

# Import DTOs để kiểm tra output
from app.domain.models.report import (
    BaoCaoKetQuaHDKD,
    BaoCaoLuuChuyenTienTe,
    BaoCaoThuyetMinh,
    BaoCaoTinhHinhTaiChinh,
)


@pytest.fixture
def mock_repos():
    """Mock các repository cần thiết."""
    journal_repo = Mock()
    account_repo = Mock()
    period_service = Mock()
    return journal_repo, account_repo, period_service


@pytest.fixture
def sample_accounts():
    """Dữ liệu mẫu: danh sách tài khoản theo hệ thống TT99."""
    return [
        # --- TÀI SẢN ---
        TaiKhoan(
            so_tai_khoan="111",
            ten_tai_khoan="Tiền mặt",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
        ),
        TaiKhoan(
            so_tai_khoan="112",
            ten_tai_khoan="Tiền gửi NH",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
        ),
        TaiKhoan(
            so_tai_khoan="156",
            ten_tai_khoan="Hàng hóa",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
        ),
        # --- NỢ PHẢI TRẢ ---
        TaiKhoan(
            so_tai_khoan="331",
            ten_tai_khoan="Phải trả NCC",
            loai_tai_khoan=LoaiTaiKhoan.NO_PHAI_TRA,
        ),
        TaiKhoan(
            so_tai_khoan="333",
            ten_tai_khoan="Thuế và các khoản phải nộp NN",
            loai_tai_khoan=LoaiTaiKhoan.NO_PHAI_TRA,
        ),
        TaiKhoan(
            so_tai_khoan="3331",
            ten_tai_khoan="Thuế GTGT phải nộp",
            loai_tai_khoan=LoaiTaiKhoan.NO_PHAI_TRA,
        ),
        # --- VỐN CHỦ SỞ HỮU ---
        TaiKhoan(
            so_tai_khoan="411",
            ten_tai_khoan="Vốn đầu tư CSH",
            loai_tai_khoan=LoaiTaiKhoan.VON_CHU_SO_HUU,
        ),
        TaiKhoan(
            so_tai_khoan="421",
            ten_tai_khoan="Lợi nhuận sau thuế chưa phân phối",
            loai_tai_khoan=LoaiTaiKhoan.VON_CHU_SO_HUU,
        ),
        # --- DOANH THU / CHI PHÍ (cho BCTC KQHDKD) ---
        TaiKhoan(
            so_tai_khoan="511",
            ten_tai_khoan="Doanh thu bán hàng",
            loai_tai_khoan=LoaiTaiKhoan.DOANH_THU,
        ),
        TaiKhoan(
            so_tai_khoan="632",
            ten_tai_khoan="Giá vốn hàng bán",
            loai_tai_khoan=LoaiTaiKhoan.GIA_VON,
        ),
        TaiKhoan(
            so_tai_khoan="821",
            ten_tai_khoan="Chi phí thuế TNDN",
            loai_tai_khoan=LoaiTaiKhoan.CHI_PHI,
        ),
    ]


@pytest.fixture
def sample_journal_entries():
    """Dữ liệu mẫu: các bút toán phát sinh."""
    return [
        JournalEntry(
            id=1,
            ngay_ct=date(2025, 6, 15),
            so_phieu="PN-2025-001",
            mo_ta="Bán hàng",
            lines=[
                JournalEntryLine(
                    so_tai_khoan="112",
                    no=Decimal("110000000"),
                    co=Decimal("0"),
                ),
                JournalEntryLine(
                    so_tai_khoan="511",
                    no=Decimal("0"),
                    co=Decimal("100000000"),
                ),
                JournalEntryLine(
                    so_tai_khoan="3331",
                    no=Decimal("0"),
                    co=Decimal("10000000"),
                ),
            ],
            trang_thai="Posted",
        ),
        JournalEntry(
            id=2,
            ngay_ct=date(2025, 6, 20),
            so_phieu="PM-2025-001",
            mo_ta="Mua hàng",
            lines=[
                JournalEntryLine(
                    so_tai_khoan="156", no=Decimal("60000000"), co=Decimal("0")
                ),
                JournalEntryLine(
                    so_tai_khoan="331", no=Decimal("0"), co=Decimal("60000000")
                ),
            ],
            trang_thai="Posted",
        ),
    ]


def test_lay_bao_cao_tinh_hinh_tai_chinh(
    mock_repos, sample_accounts, sample_journal_entries
):
    journal_repo, account_repo, period_service = mock_repos

    account_repo.get_all.return_value = sample_accounts
    account_repo.get_by_id = lambda code: next(
        (a for a in sample_accounts if a.so_tai_khoan == code), None
    )
    journal_repo.get_all_posted_in_range.return_value = sample_journal_entries

    service = ReportingService(journal_repo, account_repo, period_service)

    # 👇 MOCK HÀM TÍNH SỐ DƯ TÀI KHOẢN
    def mock_tinh_so_du(so_tai_khoan, ngay_bat_dau, ngay_ket_thuc):
        balance_map = {
            # Tài sản
            "111": (Decimal("50000000"), Decimal("0")),  # Tiền mặt
            "112": (Decimal("110000000"), Decimal("0")),  # Tiền gửi
            "156": (Decimal("60000000"), Decimal("0")),  # Hàng hóa
            # Nợ phải trả
            "331": (Decimal("0"), Decimal("60000000")),  # Phải trả NCC
            "3331": (
                Decimal("0"),
                Decimal("10000000"),
            ),  # Thuế GTGT → THIẾU DÒNG NÀY TRƯỚC ĐÂY!
            # Vốn CSH
            "411": (Decimal("0"), Decimal("60000000")),  # Vốn đầu tư
            "421": (Decimal("0"), Decimal("90000000")),  # Lợi nhuận
            # Doanh thu/Chi phí (cho KQHDKD, nhưng không dùng trong CĐKT)
            "511": (Decimal("0"), Decimal("100000000")),  # Doanh thu
            "632": (Decimal("0"), Decimal("0")),
            "821": (Decimal("0"), Decimal("10000000")),  # Thuế TNDN
        }
        sd_dau_ky = Decimal("0")
        ps_no = Decimal("0")
        ps_co = Decimal("0")
        sd_cuoi_ky_no, sd_cuoi_ky_co = balance_map.get(
            so_tai_khoan, (Decimal("0"), Decimal("0"))
        )
        return sd_dau_ky, ps_no, ps_co, sd_cuoi_ky_no, sd_cuoi_ky_co

    # Gán mock
    service._tinh_so_du_tai_khoan_theo_ngay = mock_tinh_so_du

    bao_cao = service.lay_bao_cao_tinh_hinh_tai_chinh(
        ky_hieu="Quý 2/2025",
        ngay_lap=date(2025, 6, 30),
        ngay_ket_thuc=date(2025, 6, 30),
    )

    assert isinstance(bao_cao, BaoCaoTinhHinhTaiChinh)
    assert bao_cao.ngay_lap == date(2025, 6, 30)
    assert bao_cao.ky_hieu == "Quý 2/2025"

    # Giờ đây TS = NV = 220,000,000
    balance_diff = (
        bao_cao.tai_san.tong_cong_tai_san
        - bao_cao.nguon_von.tong_cong_nguon_von
    )
    assert abs(balance_diff) < Decimal(
        "0.01"
    ), f"Cân đối kế toán không đúng: TS={bao_cao.tai_san.tong_cong_tai_san}, NV={bao_cao.nguon_von.tong_cong_nguon_von}"


def test_lay_bao_cao_ket_qua_hdkd(
    mock_repos, sample_accounts, sample_journal_entries
):
    journal_repo, account_repo, period_service = mock_repos

    account_repo.get_all.return_value = sample_accounts
    account_repo.get_by_id = lambda code: next(
        (a for a in sample_accounts if a.so_tai_khoan == code), None
    )
    journal_repo.get_all_posted_in_range.return_value = sample_journal_entries

    service = ReportingService(journal_repo, account_repo, period_service)

    bao_cao = service.lay_bao_cao_ket_qua_hdkd(
        ky_hieu="Quý 2/2025",
        ngay_lap=date(2025, 6, 30),
        ngay_bat_dau=date(2025, 4, 1),
        ngay_ket_thuc=date(2025, 6, 30),
    )

    assert isinstance(bao_cao, BaoCaoKetQuaHDKD)
    assert bao_cao.doanh_thu_ban_hang == Decimal("100000000")
    assert bao_cao.gia_von_hang_ban == Decimal(
        "0"
    )  # chưa có dữ liệu giá vốn trong sample
    # Kiểm tra công thức doanh thu thuần
    assert (
        bao_cao.doanh_thu_thuan
        == bao_cao.doanh_thu_ban_hang - bao_cao.cac_khoan_giam_tru_doanh_thu
    )


def test_lay_bao_cao_thuyet_minh(
    mock_repos, sample_accounts, sample_journal_entries
):
    journal_repo, account_repo, period_service = mock_repos

    account_repo.get_all.return_value = sample_accounts
    account_repo.get_by_id = lambda code: next(
        (a for a in sample_accounts if a.so_tai_khoan == code), None
    )
    journal_repo.get_all_posted_in_range.return_value = sample_journal_entries

    service = ReportingService(journal_repo, account_repo, period_service)
    service._get_opening_balance = lambda code, d: Decimal("0")

    bao_cao = service.lay_bao_cao_thuyet_minh(
        ky_hieu="Quý 2/2025",
        ngay_lap=date(2025, 6, 30),
        ngay_bat_dau=date(2025, 4, 1),
        ngay_ket_thuc=date(2025, 6, 30),
    )

    assert isinstance(bao_cao, BaoCaoThuyetMinh)
    assert bao_cao.chuan_muc_ke_toan_ap_dung == "VAS và TT99/2025/TT-BTC"
    assert (
        len(
            bao_cao.thuyet_minh_ket_qua_hoat_dong_kinh_doanh.chi_tiet_tai_khoan
        )
        > 0
    )


def test_lay_bang_can_doi_so_phat_sinh(
    mock_repos, sample_accounts, sample_journal_entries
):
    journal_repo, account_repo, period_service = mock_repos

    account_repo.get_all.return_value = sample_accounts
    account_repo.get_by_id = lambda code: next(
        (a for a in sample_accounts if a.so_tai_khoan == code), None
    )
    journal_repo.get_all_posted_in_range.return_value = sample_journal_entries

    service = ReportingService(journal_repo, account_repo, period_service)
    service._get_opening_balance = lambda code, d: (
        Decimal("50000000") if code == "111" else Decimal("0")
    )

    bang_can_doi = service.lay_bang_can_doi_so_phat_sinh(
        ky_hieu="Quý 2/2025",
        ngay_lap=date(2025, 6, 30),
        ngay_bat_dau=date(2025, 4, 1),
        ngay_ket_thuc=date(2025, 6, 30),
    )

    assert len(bang_can_doi) > 0
    account_112 = next(
        (a for a in bang_can_doi if a.so_tai_khoan == "112"), None
    )
    assert account_112
    assert account_112.phat_sinh_no == Decimal("110000000")
    assert account_112.so_du_dau_ky_co == Decimal(
        "0"
    )  # tài sản -> số dư đầu kỳ nợ


# Optional: skip cash flow test vì đang là placeholder
def test_lay_bao_cao_luu_chuyen_tien_te(mock_repos):
    journal_repo, account_repo, period_service = mock_repos
    service = ReportingService(journal_repo, account_repo, period_service)
    service._get_opening_balance = lambda code, d: (
        Decimal("100000000") if code in ("111", "112") else Decimal("0")
    )

    bao_cao = service.lay_bao_cao_luu_chuyen_tien_te(
        ky_hieu="Quý 2/2025",
        ngay_lap=date(2025, 6, 30),
        ngay_bat_dau=date(2025, 4, 1),
        ngay_ket_thuc=date(2025, 6, 30),
    )

    assert isinstance(bao_cao, BaoCaoLuuChuyenTienTe)
    assert bao_cao.tien_va_tuong_duong_tien_dau_ky == Decimal(
        "200000000"
    )  # 111 + 112 = 100M + 100M


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
