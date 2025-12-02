# app/application/services/accounting_periods/unlock_service.py
import logging
from datetime import date

from app.application.interfaces.period_repo import (
    AccountingPeriodRepositoryInterface,
)
from app.domain.models.accounting_period import KyKeToan

logger = logging.getLogger(__name__)


class UnlockAccountingPeriodService:
    """
    [SRP] Chỉ chịu trách nhiệm mở kỳ kế toán (chuyển từ 'Locked' về 'Open').

    📌 TT99/2025/TT-BTC Điều 25:
    - Kỳ kế toán có thể được mở lại trong trường hợp cần điều chỉnh sai sót sau ngày khóa sổ.
    - Việc mở kỳ phải có lý do chính đáng và được ghi nhận đầy đủ (audit trail).
    """

    def __init__(self, repo: AccountingPeriodRepositoryInterface):
        self.repo = repo

    def execute(
        self, id: int, ly_do: str, nguoi_thuc_hien: str = "System"
    ) -> bool:
        """
        Mở kỳ kế toán đã khóa.

        Args:
            id: ID của kỳ cần mở.
            ly_do: Lý do mở kỳ (bắt buộc).
            nguoi_thuc_hien: Người thực hiện (mặc định là "System").

        Returns:
            True nếu mở kỳ thành công.

        Raises:
            ValueError: Nếu kỳ không tồn tại, không bị khóa, hoặc lý do trống.
        """
        if not ly_do or not ly_do.strip():
            raise ValueError("Lý do mở kỳ không được để trống.")

        ky = self.repo.get_by_id(id)
        if not ky:
            raise ValueError(f"Kỳ kế toán với ID {id} không tồn tại.")

        if ky.trang_thai != "Locked":
            raise ValueError(
                f"Kỳ '{ky.ten_ky}' không ở trạng thái 'Locked' nên không thể mở."
            )

        # Cập nhật trạng thái
        self.repo.update_trang_thai(id, "Open")

        logger.info(
            f"[MO_KY_THANH_CONG] Ky ID: {id}, Ly do: {ly_do}, Nguoi thuc hien: {nguoi_thuc_hien}"
        )
        return True
