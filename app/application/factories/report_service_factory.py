# app/application/services/reports/service_factory.py

"""
Factory tạo và quản lý các service báo cáo theo TT99/2025/TT-BTC.
Tuân thủ DIP và SRP.
"""

from app.application.interfaces.account_repo import AccountRepositoryInterface
from app.application.interfaces.journal_entry_repo import (
    JournalEntryRepositoryInterface,
)
from app.application.services.reports.cash_flow_service import CashFlowService
from app.application.services.reports.disclosure_service import (
    DisclosureService,
)
from app.application.services.reports.financial_position_service import (
    FinancialPositionService,
)
from app.application.services.reports.performance_service import (
    PerformanceService,
)


class ReportServiceFactory:
    """
    Factory Pattern để tạo các service báo cáo nhỏ.
    Cho phép thay thế repository bằng mock khi testing.
    """

    def __init__(
        self,
        je_repo: JournalEntryRepositoryInterface,
        acc_repo: AccountRepositoryInterface,
    ):
        self._je_repo = je_repo
        self._acc_repo = acc_repo

    # --------------------------------------------------------
    # BÁO CÁO B01 – Tình hình tài chính
    # --------------------------------------------------------
    def create_financial_position_service(self) -> FinancialPositionService:
        return FinancialPositionService(
            journal_repo=self._je_repo,
            account_repo=self._acc_repo,
        )

    # --------------------------------------------------------
    # BÁO CÁO B02 – Kết quả hoạt động kinh doanh
    # --------------------------------------------------------
    def create_performance_service(self) -> PerformanceService:
        return PerformanceService(
            journal_repo=self._je_repo,
            account_repo=self._acc_repo,
        )

    # --------------------------------------------------------
    # BÁO CÁO B03 – Lưu chuyển tiền tệ
    # --------------------------------------------------------
    def create_cash_flow_service(self) -> CashFlowService:
        return CashFlowService(
            repo=self._je_repo,
        )

    # --------------------------------------------------------
    # BÁO CÁO B09 – Thuyết minh BCTC
    # --------------------------------------------------------
    def create_disclosure_service(self) -> DisclosureService:
        return DisclosureService(
            journal_repo=self._je_repo,
            account_repo=self._acc_repo,
        )
