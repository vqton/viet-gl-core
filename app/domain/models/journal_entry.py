# app/domain/models/journal_entry.py
"""
Mô hình nghiệp vụ cho Bút toán kế toán theo Thông tư 99/2025/TT-BTC.

🎯 Mục tiêu:
  - Tuân thủ TT99 Điều 24: Bút toán kép (Nợ = Có).
  - Tuân thủ TT99 Điều 10: Mọi bút toán phải có chứng từ gốc.
  - Hỗ trợ sổ chi tiết theo đối tượng (khách hàng, nhà cung cấp...).

📌 Giải thích cho developer không chuyên kế toán:

1. **BÚT TOÁN (GhiSoKeToan)**:
   - Là đơn vị ghi chép cơ bản nhất trong kế toán.
   - Luôn gồm **ít nhất 2 dòng**: 1 dòng Nợ + 1 dòng Có → **tổng Nợ = tổng Có**.
   - Ví dụ: "Thu tiền bán hàng 10 triệu" → Nợ TK 111 (Tiền) 10tr / Có TK 511 (Doanh thu) 10tr.

2. **DÒNG BÚT TOÁN (ButToanLine)**:
   - Mỗi dòng ghi vào **1 tài khoản** cụ thể.
   - Có 2 loại: **Nợ** (tăng tài sản, giảm nguồn vốn) và **Có** (giảm tài sản, tăng nguồn vốn).

3. **CHỨNG TỪ GỐC**:
   - Là hóa đơn, phiếu thu, phiếu chi... → bắt buộc theo TT99 Điều 10.
   - Mỗi dòng bút toán **phải có số và ngày chứng từ gốc**.

4. **CHI TIẾT THEO ĐỐI TƯỢNG**:
   - Ví dụ: TK 131 (Phải thu khách hàng) → cần lưu "KH001" để lập sổ chi tiết khách hàng.
   - Các đối tượng: khách hàng, nhà cung cấp, hàng hóa, TSCĐ...
"""

import uuid
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum


class LoaiDoiTuongChiTiet(Enum):
    """
    Các loại đối tượng cần theo dõi chi tiết (sub-ledger).
    Giúp lập sổ chi tiết cho từng đối tượng (VD: sổ chi tiết khách hàng).
    """
    KHONG_YEU_CAU = "NONE"          # Không cần chi tiết (VD: TK 111)
    KHACH_HANG = "KHACH_HANG"       # Dùng cho TK 131 (Phải thu KH)
    NHA_CUNG_CAP = "NHA_CUNG_CAP"   # Dùng cho TK 331 (Phải trả NCC)
    HANG_HOA = "HANG_HOA"           # Dùng cho TK 152, 156 (Hàng tồn kho)
    DOI_TUONG_CHI_PHI = "DOI_TUONG_CHI_PHI"  # Dùng cho TK 621, 627 (Tập hợp CP)
    TAI_SAN_CO_DINH = "TAI_SAN_CO_DINH"      # Dùng cho TK 211, 213 (TSCĐ)


class LoaiGiaoDich(Enum):
    """Loại giao dịch trong dòng bút toán (Nợ/Có)."""
    NO = "Nợ"    # Ghi Nợ: Tăng tài sản, giảm nguồn vốn
    CO = "Có"    # Ghi Có: Giảm tài sản, tăng nguồn vốn


@dataclass(frozen=True)
class ButToanLine:
    """
    Một dòng trong bút toán kế toán.

    💡 Quy tắc:
      - Mỗi dòng **chỉ ghi vào 1 tài khoản**.
      - Mỗi dòng **phải có chứng từ gốc** (số + ngày).
      - Nếu tài khoản yêu cầu chi tiết (VD: TK 131), **phải có mã đối tượng** (VD: "KH001").
    """

    # --- CÁC TRƯỜNG BẮT BUỘC ---
    so_tai_khoan: str
    """Số tài khoản (VD: "111", "331", "511") – tuân thủ Phụ lục II TT99."""

    so_tien: Decimal
    """Số tiền ghi Nợ hoặc ghi Có (luôn >= 0)."""

    loai_giao_dich: LoaiGiaoDich
    """Loại giao dịch: "Nợ" hoặc "Có"."""

    so_chung_tu_goc: str
    """Số chứng từ gốc (VD: "HD-2025-001") – bắt buộc theo TT99 Điều 10."""

    ngay_chung_tu_goc: date
    """Ngày chứng từ gốc – bắt buộc theo TT99 Điều 10."""

    # --- CÁC TRƯỜNG TÙY CHỌN (dùng khi tài khoản yêu cầu chi tiết) ---
    loai_doi_tuong_chi_tiet: LoaiDoiTuongChiTiet = field(default=LoaiDoiTuongChiTiet.KHONG_YEU_CAU)
    """Loại đối tượng chi tiết (khách hàng, NCC...)."""

    ma_doi_tuong_chi_tiet: str | None = field(default=None)
    """Mã cụ thể của đối tượng chi tiết (VD: "KH001", "NCC005")."""


@dataclass(frozen=True)
class GhiSoKeToan:
    """
    Bút toán kế toán (Journal Entry) – đơn vị ghi sổ cơ bản.

    💡 Quy tắc:
      - Phải có **ít nhất 2 dòng** (1 Nợ + 1 Có).
      - **Tổng số tiền Nợ = Tổng số tiền Có**.
      - Mỗi dòng phải có **chứng từ gốc**.
      - Ngày chứng từ phải nằm trong **kỳ kế toán đang mở**.
    """

    # --- CÁC TRƯỜNG BẮT BUỘC ---
    ngay_chung_tu: date
    """Ngày lập chứng từ (VD: ngày hóa đơn)."""

    loai_chung_tu: str
    """Loại chứng từ (VD: "PT" = Phiếu thu, "PC" = Phiếu chi, "HD" = Hóa đơn)."""

    so_chung_tu: str
    """Số chứng từ duy nhất (VD: "PT-2025-001")."""

    dien_giai: str
    """Diễn giải nghiệp vụ (VD: "Thu tiền bán hàng")."""

    cac_dong_but_toan: list[ButToanLine]
    """Danh sách các dòng bút toán (phải có ít nhất 2 dòng)."""

    # --- CÁC TRƯỜNG TÙY CHỌN ---
    ma_but_toan: str = field(default_factory=lambda: str(uuid.uuid4()))
    """Mã định danh duy nhất cho bút toán (tự sinh)."""

    ngay_tao: date = field(default_factory=date.today)
    """Ngày hệ thống tạo bút toán (khác với ngày chứng từ)."""
