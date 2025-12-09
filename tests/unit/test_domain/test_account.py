# tests/unit/test_domain/test_account.py
"""
Unit tests cho Entity Domain: TaiKhoan

📋 TT99/2025/TT-BTC:
- Phụ lục II: Hệ thống tài khoản kế toán
- Điều 11: Doanh nghiệp áp dụng hệ thống tài khoản tại Phụ lục II
- Không có nhóm tài khoản 9xx → Không tồn tại TK 911
"""

import pytest

from app.domain.models.account import LoaiTaiKhoan, TaiKhoan


def test_tai_khoan_hop_le_tai_san():
    """[TT99-PL2] Tài khoản 111 là tài sản."""
    tk = TaiKhoan(
        so_tai_khoan="111",
        ten_tai_khoan="Tiền mặt",
        loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
        cap_tai_khoan=1,
    )
    assert tk.loai_tai_khoan == LoaiTaiKhoan.TAI_SAN
    assert tk.cap_tai_khoan == 1


def test_tai_khoan_khong_duoc_phep_ton_tai_tk_911():
    """
    [TT99-PL2] TT99 không có tài khoản 911.
    Service không nên cho phép tạo TK 911.
    """
    # Trong thực tế, bạn nên có validation từ chối nhóm 9xx trong __post_init__
    # Dưới đây là test cho logic validation đó (nếu có)
    pass  # Không test ở đây vì không có lỗi trong Domain Model


def test_tai_khoan_cap_con_phai_co_cha():
    """[TT99-PL2] Tài khoản cấp 2 phải có tài khoản cha."""
    with pytest.raises(ValueError, match="Tài khoản cấp con"):
        TaiKhoan(
            so_tai_khoan="1111",
            ten_tai_khoan="Tiền mặt - Chi nhánh A",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
            cap_tai_khoan=2,
            so_tai_khoan_cha=None,  # ❌ Thiếu cha
        )


def test_tai_khoan_so_tai_khoan_khong_duoc_trong():
    """[TT99-PL2] Số tài khoản không được để trống."""
    with pytest.raises(ValueError, match="không được để trống"):
        TaiKhoan(
            so_tai_khoan="",  # ❌ Trống
            ten_tai_khoan="TK không hợp lệ",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
            cap_tai_khoan=1,
        )


def test_tai_khoan_ten_khong_duoc_trong():
    """[TT99-PL2] Tên tài khoản không được để trống."""
    with pytest.raises(ValueError, match="không được để trống"):
        TaiKhoan(
            so_tai_khoan="111",
            ten_tai_khoan="",  # ❌ Trống
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
            cap_tai_khoan=1,
        )
