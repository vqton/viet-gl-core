from datetime import date
from unittest.mock import MagicMock, create_autospec

import pytest

# Interfaces và Domain Models
from app.application.interfaces.accounting_period_service import (
    AccountingPeriodServiceInterface,
)
from app.application.interfaces.journal_entry_repo import (
    JournalEntryRepositoryInterface,
)
from app.application.services.journaling.posting_service import (
    PostingJournalEntryService,
)
from app.domain.models.journal_entry import JournalEntry, JournalEntryLine

# Dữ liệu mẫu
DRAFT_ENTRY = JournalEntry(
    id=1,
    ngay_ct=date(2025, 11, 15),
    so_phieu="BT001",
    mo_ta="Thanh toán tiền mặt",
    lines=[
        JournalEntryLine(so_tai_khoan="111", no=10000, co=0),
        JournalEntryLine(so_tai_khoan="642", no=0, co=10000),
    ],
    trang_thai="Draft",
)

POSTED_ENTRY = DRAFT_ENTRY.model_copy(update={"trang_thai": "Posted"})


@pytest.fixture
def mock_repo():
    """Mock JournalEntryRepositoryInterface."""
    return create_autospec(JournalEntryRepositoryInterface)


@pytest.fixture
def mock_period_service():
    """Mock AccountingPeriodServiceInterface."""
    # Đảm bảo phương thức có thể được mock và gọi
    return create_autospec(AccountingPeriodServiceInterface)


@pytest.fixture
def posting_service(mock_repo, mock_period_service):
    """Cung cấp instance của PostingJournalEntryService."""
    return PostingJournalEntryService(
        repo=mock_repo, period_service=mock_period_service
    )


class TestPostingJournalEntryService:
    def test_execute_success(self, posting_service, mock_repo):
        """Kiểm tra việc ghi sổ thành công (Draft -> Posted)."""
        # Giả lập: repo.get_by_id trả về bút toán nháp
        mock_repo.get_by_id.return_value = DRAFT_ENTRY.model_copy()
        # Giả lập: repo.update_status trả về bút toán đã ghi sổ
        mock_repo.update_status.return_value = POSTED_ENTRY.model_copy()

        result = posting_service.execute(id=1)

        # 1. Kết quả trả về phải là Posted
        assert result.trang_thai == "Posted"
        # 2. Phương thức get_by_id phải được gọi
        mock_repo.get_by_id.assert_called_once_with(1)
        # 3. Phương thức update_status phải được gọi với trạng thái "Posted"
        mock_repo.update_status.assert_called_once_with(1, "Posted")
        # 4. Period service phải được kiểm tra khóa sổ
        posting_service.period_service.check_if_period_is_locked.assert_called_once_with(
            DRAFT_ENTRY.ngay_ct
        )

    def test_execute_entry_not_found(self, posting_service, mock_repo):
        """Kiểm tra lỗi khi không tìm thấy bút toán."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(ValueError) as excinfo:
            posting_service.execute(id=999)

        assert "không tồn tại" in str(excinfo.value)
        mock_repo.update_status.assert_not_called()

    def test_execute_already_posted(self, posting_service, mock_repo):
        """Kiểm tra lỗi khi bút toán đã được ghi sổ."""
        mock_repo.get_by_id.return_value = POSTED_ENTRY.model_copy()

        with pytest.raises(ValueError) as excinfo:
            posting_service.execute(id=1)

        assert "đã được ghi sổ rồi" in str(excinfo.value)
        mock_repo.update_status.assert_not_called()

    def test_execute_period_locked(self, posting_service, mock_repo):
        """Kiểm tra lỗi khi kỳ kế toán bị khóa."""
        mock_repo.get_by_id.return_value = DRAFT_ENTRY.model_copy()
        # Giả lập: check_if_period_is_locked ném ra lỗi (để mô phỏng kỳ bị khóa)
        # Lưu ý: Trong thực tế, Period Service nên ném ra một exception cụ thể.
        posting_service.period_service.check_if_period_is_locked.side_effect = (
            ValueError("Kỳ kế toán đã bị khóa.")
        )

        with pytest.raises(ValueError) as excinfo:
            posting_service.execute(id=1)

        assert "Kỳ kế toán đã bị khóa." in str(excinfo.value)
        mock_repo.update_status.assert_not_called()

    def test_unpost_success(self, posting_service, mock_repo):
        """Kiểm tra việc hủy ghi sổ thành công (Posted -> Draft)."""
        # Giả lập: repo.get_by_id trả về bút toán đã ghi sổ
        mock_repo.get_by_id.return_value = POSTED_ENTRY.model_copy()
        # Giả lập: repo.update_status trả về bút toán nháp
        mock_repo.update_status.return_value = DRAFT_ENTRY.model_copy()

        result = posting_service.unpost(id=1)

        # 1. Kết quả trả về phải là Draft
        assert result.trang_thai == "Draft"
        # 2. Phương thức update_status phải được gọi với trạng thái "Draft"
        mock_repo.update_status.assert_called_once_with(1, "Draft")
        # 3. Period service phải được kiểm tra khóa sổ
        posting_service.period_service.check_if_period_is_locked.assert_called_once_with(
            DRAFT_ENTRY.ngay_ct
        )

    def test_unpost_entry_is_draft(self, posting_service, mock_repo):
        """Kiểm tra lỗi khi hủy ghi sổ một bút toán đã ở trạng thái Draft."""
        mock_repo.get_by_id.return_value = DRAFT_ENTRY.model_copy()

        with pytest.raises(ValueError) as excinfo:
            posting_service.unpost(id=1)

        assert "đã ở trạng thái Draft" in str(excinfo.value)
        mock_repo.update_status.assert_not_called()

    def test_unpost_entry_is_locked(self, posting_service, mock_repo):
        """Kiểm tra lỗi khi hủy ghi sổ một bút toán đã bị Locked."""
        LOCKED_ENTRY = DRAFT_ENTRY.model_copy(update={"trang_thai": "Locked"})
        mock_repo.get_by_id.return_value = LOCKED_ENTRY

        with pytest.raises(ValueError) as excinfo:
            posting_service.unpost(id=1)

        assert "Bút toán đã bị khóa" in str(excinfo.value)
        mock_repo.update_status.assert_not_called()
