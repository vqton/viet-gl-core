# tests/test_api_endpoints.py
"""
Integration Tests cho các API endpoint liên quan đến quản lý tài khoản kế toán.

📋 TT99/2025/TT-BTC:
- Điều 8–10: Chứng từ gốc là bắt buộc.
- Điều 24: Bút toán kép (Nợ = Có), không dùng TK 911.
- Phụ lục II: Hệ thống tài khoản kế toán.
- Phụ lục IV: Báo cáo tài chính.

🎯 Mục tiêu:
- Kiểm tra toàn bộ luồng từ API → Service → Response.
- Đảm bảo các nghiệp vụ kế toán được thực hiện đúng.
- Đảm bảo API phản hồi lỗi đúng theo TT99.
"""

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.domain.models.account import LoaiTaiKhoan, TaiKhoan
from app.domain.models.accounting_period import KyKeToan
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine
from app.domain.models.report import (
    BaoCaoLuuChuyenTienTe,
    BaoCaoTinhHinhTaiChinh,
    LuuChuyenTienTeHDDT,
    LuuChuyenTienTeHDKD,
    LuuChuyenTienTeHDTC,
    NoPhaiTraDaiHan,
    NoPhaiTraNganHan,
    TaiSanDaiHan,
    TaiSanNganHan,
    TienVaCacKhoanTgTien,
    TongNguonVon,
    TongTaiSan,
    VonChuSoHuu,
)
from app.main import app
from app.presentation.api.v1.accounting.dependencies import (
    get_lock_period_service,
)


@pytest.fixture
def client_with_mock_create_account_service():
    from app.presentation.api.v1.accounting.dependencies import (
        get_create_tai_khoan_service,
    )

    mock_service = MagicMock()
    app.dependency_overrides[get_create_tai_khoan_service] = lambda: mock_service

    with TestClient(app) as client:
        yield client, mock_service

    app.dependency_overrides.clear()


@pytest.fixture
def client_with_mock_lock_period_service():
    """
    [TT99-Đ25] Fixture chuẩn bị môi trường test cho API khóa kỳ kế toán.

    📌 Mục tiêu:
    - Mock `LockAccountingPeriodService` để kiểm thử logic khóa kỳ (kiểm tra bút toán Draft).
    - Đảm bảo không phụ thuộc vào DB thật hoặc trạng thái kỳ thật trong hệ thống.

    📝 Luồng hoạt động:
    1. Endpoint `/accounting-periods/{id}/lock` inject `LockAccountingPeriodService`.
    2. Ta override để dùng mock_service thay vì service thật.
    3. Mock có thể được cấu hình trả về `True` (thành công) hoặc `raise ValueError` (thất bại).
    4. Kiểm tra phản hồi API và xác minh hành vi.

    📚 Cơ sở pháp lý:
    - TT99/2025/TT-BTC Điều 25: Quản lý kỳ kế toán.
    - "Không được khóa kỳ nếu vẫn còn bút toán ở trạng thái Draft."

    🔧 Cách dùng:
    - Trong test: `client, mock_service = client_with_mock_lock_period_service`.
    - Cấu hình: `mock_service.execute.return_value = True`.
    - Gọi: `response = client.post("/lock", json=...)`.
    - Kiểm tra: `assert response.status_code == 200`.
    """
    # 👇 Import đúng service được inject trong route
    from app.application.services.accounting_periods.lock_service import (
        LockAccountingPeriodService,
    )

    # 👇 Tạo mock
    mock_service = MagicMock()

    # 👇 Override dependency
    app.dependency_overrides[get_lock_period_service] = lambda: mock_service

    with TestClient(app) as client:
        yield client, mock_service

    app.dependency_overrides.clear()


@pytest.fixture
def client_with_mock_cash_flow_service():
    """
    [TT99-PL4] Fixture chuẩn bị môi trường test cho API lấy báo cáo lưu chuyển tiền tệ (B03-DN).

    📌 Mục tiêu:
    - Mock `CashFlowService` để kiểm thử API trả về báo cáo đúng theo phương pháp gián tiếp.
    - Không cần chạy logic tính toán phức tạp (lấy dữ liệu từ DB) → tăng tốc test.

    📝 Luồng hoạt động:
    1. Endpoint `/reports/cash-flow` inject `CashFlowService`.
    2. Ta override dependency để trả về `mock_service`.
    3. Mock trả về DTO `BaoCaoLuuChuyenTienTe` đã được cấu hình trước.
    4. Test kiểm tra dữ liệu trả về từ API có đúng không.

    📚 Cơ sở pháp lý:
    - TT99/2025/TT-BTC Phụ lục IV: Mẫu B03-DN (Lưu chuyển tiền tệ).
    - "Báo cáo B03-DN phải lập theo phương pháp gián tiếp."

    🔧 Cách dùng:
    - Trong test: `client, mock_service = client_with_mock_cash_flow_service`.
    - Cấu hình: `mock_service.lay_bao_cao.return_value = fake_report`.
    - Gọi: `response = client.get("/reports/cash-flow?...")`.
    - Kiểm tra: `assert response.status_code == 200`.
    """
    # 👇 Import đúng service được inject trong route
    from app.application.services.reports.cash_flow_service import (
        CashFlowService,
    )

    # 👇 Tạo mock
    mock_service = MagicMock()

    # 👇 Override dependency
    app.dependency_overrides[CashFlowService] = lambda: mock_service

    with TestClient(app) as client:
        yield client, mock_service

    app.dependency_overrides.clear()


# ————————————————————————————————————————————————————————————————————————————————
# 1. TEST API TÀI KHOẢN (ACCOUNTING - COA)
# ————————————————————————————————————————————————————————————————————————————————


def test_create_account_success(client_with_mock_create_account_service):
    """
    [TT99-PL2] Test tạo tài khoản thành công qua API.

    📝 Kịch bản:
        - Gửi payload hợp lệ: số tài khoản, tên, loại, cấp.
        - Service trả về tài khoản đã tạo.
        - API trả về 201 Created.
    """
    client, mock_service = client_with_mock_create_account_service

    payload = {
        "so_tai_khoan": "11311",
        "ten_tai_khoan": "Tiền gửi ngân hàng",
        "loai_tai_khoan": "TAI_SAN",
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    }

    fake_account = TaiKhoan(
        so_tai_khoan="11311",
        ten_tai_khoan="Tiền gửi ngân hàng",
        loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
        cap_tai_khoan=1,
        so_tai_khoan_cha=None,
        la_tai_khoan_tong_hop=True,
    )

    mock_service.execute.return_value = fake_account

    response = client.post("/accounting/v1/accounts/", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["so_tai_khoan"] == "11311"
    assert data["loai_tai_khoan"] == "TAI_SAN"

    # Xác minh service được gọi đúng
    mock_service.execute.assert_called_once()


def test_create_account_invalid_data(client_with_mock_create_account_service):
    """
    [Pydantic Validation] Test tạo tài khoản với dữ liệu không hợp lệ (số tài khoản trống).
    """
    client, _ = client_with_mock_create_account_service

    response = client.post(
        "/accounting/v1/accounts/",
        json={
            "so_tai_khoan": "",  # ❌ Không hợp lệ
            "ten_tai_khoan": "Tên không hợp lệ",
            "loai_tai_khoan": "TAI_SAN",
        },
    )

    # FastAPI/Pydantic sẽ trả về 422 Unprocessable Entity
    assert response.status_code == 422


# ————————————————————————————————————————————————————————————————————————————————
# 2. TEST API KỲ KẾ TOÁN (ACCOUNTING PERIOD)
# ————————————————————————————————————————————————————————————————————————————————


def test_lock_accounting_period_success(client_with_mock_lock_period_service):
    """
    [TT99-Đ25] Test khóa kỳ kế toán thành công.
    """
    client, mock_service = client_with_mock_lock_period_service

    mock_service.execute.return_value = True

    response = client.post(
        "/accounting/v1/accounting-periods/1/lock",
        json={"nguoi_thuc_hien": "Admin"},
    )

    assert response.status_code == 200
    assert "đã được khóa" in response.json()["message"]


# ————————————————————————————————————————————————————————————————————————————————
# 4. TEST API BÁO CÁO (REPORTING)
# ————————————————————————————————————————————————————————————————————————————————


def test_get_financial_position_report_success(
    client_with_mock_create_account_service,
):
    """
    [TT99-PL4] Test lấy báo cáo tình hình tài chính (B01-DN).
    """
    client, _ = client_with_mock_create_account_service  # ✅ SỬA: dùng fixture đúng

    from app.application.services.reports.financial_position_service import (
        FinancialPositionService,
    )

    mock_service = MagicMock()
    from app.presentation.api.v1.accounting.dependencies import (
        get_financial_position_service,
    )

    app.dependency_overrides[get_financial_position_service] = lambda: mock_service

    fake_report = BaoCaoTinhHinhTaiChinh(
        ngay_lap=date.today(),
        ky_hieu="Năm 2025",
        tai_san=TongTaiSan(
            tai_san_ngan_han=TaiSanNganHan(
                tien_va_cac_khoan_tuong_duong_tien=TienVaCacKhoanTgTien(
                    tien_mat=Decimal("100000000"),
                    tien_gui_ngan_hang=Decimal("50000000"),
                    tien_dang_chuyen=Decimal("0"),
                ),
                tong_tai_san_ngan_han=Decimal("150000000"),
            ),
            tai_san_dai_han=TaiSanDaiHan(  # ✅ SỬA: Thêm field này để không lỗi "Field required"
                tai_san_co_dinh_huu_hinh=Decimal("50000000"),
                tai_san_co_dinh_vo_hinh=Decimal("0"),
                tong_tai_san_dai_han=Decimal("50000000"),
            ),
            tong_cong_tai_san=Decimal("200000000"),
        ),
        nguon_von=TongNguonVon(
            no_phai_tra_ngan_han=NoPhaiTraNganHan(tong_no_ngan_han=Decimal("50000000")),
            no_phai_tra_dai_han=NoPhaiTraDaiHan(tong_no_dai_han=Decimal("0")),
            von_chu_so_huu=VonChuSoHuu(tong_von_chu_so_huu=Decimal("150000000")),
            tong_cong_nguon_von=Decimal("200000000"),
        ),
    )
    mock_service.lay_bao_cao.return_value = fake_report

    response = client.get(
        "/accounting/v1/reports/financial-position?ky_hieu=Năm 2025&ngay_lap=2025-12-31"
        + "&ngay_bat_dau=2025-01-01&ngay_ket_thuc=2025-12-31"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ky_hieu"] == "Năm 2025"

    app.dependency_overrides.clear()


def test_get_cash_flow_report_success(client_with_mock_cash_flow_service):
    """
    [TT99-PL4] Test lấy báo cáo lưu chuyển tiền tệ (B03-DN).
    """
    client, mock_service = client_with_mock_cash_flow_service

    fake_report = BaoCaoLuuChuyenTienTe(
        ngay_lap=date.today(),
        ky_hieu="Năm 2025",
        luu_chuyen_tien_te_hdkd=LuuChuyenTienTeHDKD(
            loi_nhuan_truoc_thue=Decimal("40000000"),
            dieu_chinh_khau_hao_ts_co_dinh=Decimal("10000000"),
            luu_chuyen_tien_thuan_tu_hdkd=Decimal("50000000"),
        ),
        luu_chuyen_tien_te_hddt=LuuChuyenTienTeHDDT(
            luu_chuyen_thuan_tu_hddt=Decimal("0")  # Mock
        ),
        luu_chuyen_tien_te_hdtc=LuuChuyenTienTeHDTC(
            luu_chuyen_thuan_tu_hdtc=Decimal("0")  # Mock
        ),
        luu_chuyen_tien_thuan_trong_ky=Decimal("50000000"),
        tien_va_tuong_duong_tien_dau_ky=Decimal("100000000"),
        tien_va_tuong_duong_tien_cuoi_ky=Decimal("150000000"),
    )
    mock_service.lay_bao_cao.return_value = fake_report

    # ✅ SỬA: URL đúng cho endpoint B03-DN
    response = client.get(
        "/accounting/v1/reports/cash-flow?ky_hieu=Năm 2025&ngay_lap=2025-12-31"
        + "&ngay_bat_dau=2025-01-01&ngay_ket_thuc=2025-12-31"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ky_hieu"] == "Năm 2025"

    # ✅ Không cần clear ở đây vì fixture đã làm
