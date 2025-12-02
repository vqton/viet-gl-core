# File: tests.py
# Tập hợp các Unit, Integration và Infrastructure Tests

from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, create_autospec

import pytest

# 4. Imports cho Presentation (API) - FastAPI Test Client
from fastapi.testclient import TestClient
from test_db import (
    TestingSessionLocal,
    override_get_db,
    setup_test_db,
    teardown_test_db,
)

# 2. Imports cho Application Services
from app.application.services.accounting_period_service import (
    AccountingPeriodService,
)
from app.application.services.journaling_service import JournalingService
from app.application.services.reporting_service import ReportingService
from app.application.services.tai_khoan_service import TaiKhoanService
from app.domain.models.account import LoaiTaiKhoan, TaiKhoan

# 1. Imports cho Domain Models
from app.domain.models.accounting_period import KyKeToan
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine
from app.infrastructure.database import get_db
from app.infrastructure.models.sql_account import SQLAccount
from app.infrastructure.repositories.account_repository import (
    AccountRepository,
)

# 3. Imports cho Infrastructure Repositories
from app.infrastructure.repositories.accounting_period_repository import (
    AccountingPeriodRepository,
)
from app.infrastructure.repositories.journal_entry_repository import (
    JournalEntryRepository,
)
from app.main import app  # Import FastAPI app

# Dữ liệu mẫu (theo TT99): Tài khoản 111 (Tiền mặt - Tài sản), 331 (Phải trả người bán - Nợ)
MOCK_TK_111 = TaiKhoan(
    so_tai_khoan="111",
    ten_tai_khoan="Tiền mặt",
    loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
    la_tai_khoan_tong_hop=False,
)
MOCK_TK_331 = TaiKhoan(
    so_tai_khoan="331",
    ten_tai_khoan="Phải trả người bán",
    loai_tai_khoan=LoaiTaiKhoan.NO_PHAI_TRA,
    la_tai_khoan_tong_hop=False,
)


# --- SETUP & TEARDOWN CHO TOÀN BỘ TEST SUITE ---
# Thiết lập FastAPITestClient và Database Overrides
client = TestClient(app)
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_and_teardown_db():
    """Thiết lập và xóa DB cho toàn bộ session."""
    setup_test_db()
    # Thêm tài khoản mẫu vào DB để các bài test Repository/Service có thể chạy
    db = TestingSessionLocal()
    db.add(
        SQLAccount(
            so_tai_khoan="111",
            ten_tai_khoan="Tiền mặt",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
            cap_tai_khoan=1,
            la_tai_khoan_tong_hop=False,
        )
    )
    db.add(
        SQLAccount(
            so_tai_khoan="331",
            ten_tai_khoan="Phải trả người bán",
            loai_tai_khoan=LoaiTaiKhoan.NO_PHAI_TRA,
            cap_tai_khoan=1,
            la_tai_khoan_tong_hop=False,
        )
    )
    db.commit()
    db.close()
    yield
    teardown_test_db()


@pytest.fixture(scope="function")
def db_session():
    """Cung cấp một session DB mới cho mỗi test function và rollback/reset sau đó."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()  # Hoàn tác mọi thay đổi để không ảnh hưởng đến test khác
        db.close()


# =========================================================================
# I. DOMAIN UNIT TESTS (Kiểm tra Logic Nghiệp Vụ Thuần túy - TT99 Compliance)
# =========================================================================


class TestDomainLogic:
    def test_journal_entry_can_bang(self):
        """TT99 Rule: Ghi sổ kép (Tổng Nợ = Tổng Có)"""
        lines = [
            JournalEntryLine(
                so_tai_khoan="111", no=Decimal(100), co=Decimal(0)
            ),
            JournalEntryLine(
                so_tai_khoan="331", no=Decimal(0), co=Decimal(100)
            ),
        ]
        # Bút toán hợp lệ (Cân bằng)
        entry = JournalEntry(
            ngay_ct=date.today(), so_phieu="TEST001", lines=lines
        )
        entry.kiem_tra_can_bang()  # Không raise exception
        assert sum(line.no for line in entry.lines) == sum(
            line.co for line in entry.lines
        )

    def test_journal_entry_khong_can_bang(self):
        """TT99 Rule: Tổng Nợ != Tổng Có -> raise ValueError"""
        lines = [
            JournalEntryLine(
                so_tai_khoan="111", no=Decimal(100), co=Decimal(0)
            ),
            JournalEntryLine(
                so_tai_khoan="331", no=Decimal(0), co=Decimal(99)
            ),  # Thiếu 1
        ]
        with pytest.raises(ValueError, match="Tổng Nợ không bằng Tổng Có"):
            JournalEntry(ngay_ct=date.today(), so_phieu="TEST002", lines=lines)

    def test_journal_line_no_va_co_cung_lon_hon_khong(self):
        """TT99 Rule: Một dòng bút toán chỉ được ghi Nợ hoặc Có (không đồng thời)"""
        lines = [
            JournalEntryLine(
                so_tai_khoan="111", no=Decimal(100), co=Decimal(1)
            )  # Lỗi ở đây
        ]
        with pytest.raises(
            ValueError, match="chỉ được ghi Nợ hoặc Có, không đồng thời cả hai"
        ):
            JournalEntry(ngay_ct=date.today(), so_phieu="TEST003", lines=lines)

    def test_ky_ke_toan_ngay_bat_dau_sau_ket_thuc(self):
        """Rule: Ngày bắt đầu kỳ kế toán phải trước hoặc bằng ngày kết thúc"""
        with pytest.raises(
            ValueError, match="Ngày bắt đầu không thể sau ngày kết thúc"
        ):
            KyKeToan(
                ten_ky="Invalid",
                ngay_bat_dau=date(2025, 12, 1),
                ngay_ket_thuc=date(2025, 11, 30),
            )

    def test_ky_ke_toan_trang_thai_khong_hop_le(self):
        """Rule: Trạng thái kỳ kế toán chỉ là 'Open' hoặc 'Locked'"""
        with pytest.raises(
            ValueError, match="Trạng thái kỳ phải là 'Open' hoặc 'Locked'"
        ):
            KyKeToan(ten_ky="Invalid", trang_thai="Closed")


# =========================================================================
# II. APPLICATION INTEGRATION TESTS (Kiểm tra Logic Services)
# =========================================================================


class TestApplicationServices:

    def test_tai_khoan_service_tao_tk_cap_con_thanh_cong(self, db_session):
        """Rule: Tài khoản con phải có tài khoản cha tồn tại."""
        repo = AccountRepository(db_session)
        service = TaiKhoanService(repo)

        # Tài khoản 111 đã tồn tại trong setup_test_db
        tk_con = TaiKhoan(
            so_tai_khoan="1112",
            ten_tai_khoan="Tiền mặt VND",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
            cap_tai_khoan=2,
            so_tai_khoan_cha="111",
            la_tai_khoan_tong_hop=False,
        )
        result = service.tao_tai_khoan(tk_con)
        assert result.so_tai_khoan == "1112"
        assert result.so_tai_khoan_cha == "111"

    def test_tai_khoan_service_tao_tk_cap_con_that_bai(self, db_session):
        """Rule: Không thể tạo tài khoản con nếu tài khoản cha không tồn tại."""
        repo = AccountRepository(db_session)
        service = TaiKhoanService(repo)

        # Tài khoản cha "999" không tồn tại
        tk_con = TaiKhoan(
            so_tai_khoan="1113",
            ten_tai_khoan="Tiền mặt USD",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
            cap_tai_khoan=2,
            so_tai_khoan_cha="999",
            la_tai_khoan_tong_hop=False,
        )
        with pytest.raises(
            ValueError, match="Tài khoản cha '999' không tồn tại."
        ):
            service.tao_tai_khoan(tk_con)

    def test_journaling_service_tao_phieu_tk_khong_ton_tai(self, db_session):
        """Rule: Bút toán phải sử dụng các tài khoản có tồn tại."""
        journal_repo = JournalEntryRepository(db_session)
        account_repo = AccountRepository(db_session)
        service = JournalingService(journal_repo, account_repo)

        # Tài khoản "999" không tồn tại trong DB mẫu
        lines = [
            JournalEntryLine(
                so_tai_khoan="111", no=Decimal(100), co=Decimal(0)
            ),
            JournalEntryLine(
                so_tai_khoan="999", no=Decimal(0), co=Decimal(100)
            ),
        ]
        entry = JournalEntry(
            ngay_ct=date.today(), so_phieu="FAIL001", lines=lines
        )
        with pytest.raises(ValueError, match="Tài khoản '999' không tồn tại"):
            service.tao_phieu_ke_toan(entry)

    def test_accounting_period_service_khoa_ky_that_bai_vi_con_phieu_nhap(
        self, db_session
    ):
        """Rule GL-05 (Locking): Không được khóa kỳ khi còn bút toán chưa được Posted/Locked."""

        # Mocks
        ky_repo_mock = create_autospec(AccountingPeriodRepository)
        phieu_repo_mock = create_autospec(JournalEntryRepository)

        # Mock dữ liệu kỳ kế toán
        ky_mock = KyKeToan(
            id=1,
            ten_ky="Q1-2025",
            ngay_bat_dau=date(2025, 1, 1),
            ngay_ket_thuc=date(2025, 3, 31),
            trang_thai="Open",
        )
        ky_repo_mock.get_by_id.return_value = ky_mock
        ky_repo_mock.get_ky_by_date.return_value = ky_mock

        # Mock dữ liệu bút toán (còn 1 bút toán Draft)
        phieu_draft_mock = JournalEntry(
            id=101,
            ngay_ct=date(2025, 2, 15),
            so_phieu="DRAFT01",
            lines=[],
            trang_thai="Draft",
        )
        phieu_repo_mock.get_all_in_period.return_value = [phieu_draft_mock]

        service = AccountingPeriodService(ky_repo_mock, phieu_repo_mock)

        # Kiểm tra: Phải raise Exception vì còn bút toán Draft
        with pytest.raises(
            ValueError, match="vẫn còn 1 bút toán ở trạng thái 'Draft'"
        ):
            service.khoa_ky(1, nguoi_thuc_hien="Tester")

        # Kiểm tra: Phải gọi đúng hàm kiểm tra
        phieu_repo_mock.get_all_in_period.assert_called_once_with(
            ky_mock.ngay_bat_dau, ky_mock.ngay_ket_thuc
        )
        # Kiểm tra: Hàm update_trang_thai KHÔNG được gọi
        ky_repo_mock.update_trang_thai.assert_not_called()


# =========================================================================
# III. INFRASTRUCTURE TESTS (Kiểm tra Repository/Mapper)
# =========================================================================


class TestInfrastructureRepositories:

    def test_account_repository_add_and_get(self, db_session):
        """Kiểm tra việc chuyển đổi (mapping) và lưu trữ Tài khoản."""
        repo = AccountRepository(db_session)
        # 1. Tạo Domain Entity
        new_account = TaiKhoan(
            so_tai_khoan="131",
            ten_tai_khoan="Phải thu khách hàng",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
        )

        # 2. Add vào DB (mapper chạy)
        added_account = repo.add(new_account)
        assert added_account.so_tai_khoan == "131"

        # 3. Get từ DB (mapper chạy ngược)
        retrieved_account = repo.get_by_id("131")
        assert retrieved_account.ten_tai_khoan == "Phải thu khách hàng"
        assert retrieved_account.loai_tai_khoan == LoaiTaiKhoan.TAI_SAN
        assert (
            retrieved_account.la_tai_khoan_tong_hop is True
        )  # Giá trị mặc định

    def test_accounting_period_repository_add_and_update(self, db_session):
        """Kiểm tra việc lưu và cập nhật Kỳ kế toán."""
        repo = AccountingPeriodRepository(db_session)

        # 1. Add
        new_ky = KyKeToan(
            ten_ky="Thang 1-2026",
            ngay_bat_dau=date(2026, 1, 1),
            ngay_ket_thuc=date(2026, 1, 31),
        )
        added_ky = repo.add(new_ky)
        assert added_ky.id is not None
        assert added_ky.trang_thai == "Open"

        # 2. Update trạng thái
        updated_ky = repo.update_trang_thai(added_ky.id, "Locked")
        assert updated_ky.trang_thai == "Locked"

        # 3. Get lại để xác nhận
        confirmed_ky = repo.get_by_id(added_ky.id)
        assert confirmed_ky.trang_thai == "Locked"


# =========================================================================
# IV. PRESENTATION (API) END-TO-END TESTS (Kiểm tra HTTP Response/Exception)
# =========================================================================


class TestPresentationAPI:

    def test_api_tao_phieu_ke_toan_thanh_cong(self):
        """E2E: Tạo bút toán thành công và kiểm tra response."""
        data = {
            "ngay_ct": "2025-11-27",
            "so_phieu": "API001",
            "mo_ta": "Thu tiền bán hàng",
            "lines": [
                {"so_tai_khoan": "111", "no": 1000000.0, "co": 0.0},
                {"so_tai_khoan": "331", "no": 0.0, "co": 1000000.0},
            ],
            "trang_thai": "Draft",
        }

        # Thử gọi API POST
        response = client.post("/accounting/journal-entries", json=data)

        # Kiểm tra: Mã trạng thái 201 (Created)
        assert response.status_code == 201

        # Kiểm tra: Dữ liệu trả về (DTO) phải đúng và cân bằng
        json_response = response.json()
        assert json_response["so_phieu"] == "API001"
        assert json_response["lines"][0]["no"] == 1000000.0
        assert json_response["lines"][1]["co"] == 1000000.0

    def test_api_tao_phieu_ke_toan_khong_can_bang(self):
        """E2E: Tạo bút toán KHÔNG cân bằng (Vi phạm Domain Rule) -> HTTP 400."""
        data = {
            "ngay_ct": "2025-11-27",
            "so_phieu": "API002",
            "mo_ta": "Phieu khong can bang",
            "lines": [
                {"so_tai_khoan": "111", "no": 1000000.0, "co": 0.0},
                {"so_tai_khoan": "331", "no": 0.0, "co": 999999.0},  # Lỗi
            ],
            "trang_thai": "Draft",
        }

        # Thử gọi API POST
        response = client.post("/accounting/journal-entries", json=data)

        # Kiểm tra: Mã trạng thái 400 (Bad Request)
        assert response.status_code == 400

        # Kiểm tra: Thông báo lỗi từ Domain Entity được truyền qua Exception Handler
        assert "Tổng Nợ không bằng Tổng Có" in response.json()["detail"]

    def test_api_tao_ky_ke_toan_trung_ten(self):
        """E2E: Tạo kỳ kế toán bị trùng tên (Vi phạm Application Service Rule) -> HTTP 400."""
        data = {
            "ten_ky": "KY_TRUNG_LAP",
            "ngay_bat_dau": "2026-01-01",
            "ngay_ket_thuc": "2026-01-31",
            "trang_thai": "Open",
        }

        # 1. Tạo kỳ đầu tiên (thành công)
        response_1 = client.post("/accounting/accounting-periods", json=data)
        assert response_1.status_code == 201

        # 2. Tạo kỳ thứ hai với cùng tên (thất bại)
        response_2 = client.post("/accounting/accounting-periods", json=data)

        # Kiểm tra: Mã trạng thái 400 (Bad Request)
        assert response_2.status_code == 400

        # Kiểm tra: Thông báo lỗi từ Service Layer được truyền qua
        assert "đã tồn tại" in response_2.json()["detail"]
