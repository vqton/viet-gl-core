# app/application/services/reports/service_factory.py
"""
Factory tạo các service báo cáo theo TT99/2025/TT-BTC.
Tuân thủ nguyên tắc DIP (Dependency Inversion Principle).
"""
from app.application.interfaces.report_repo import ReportRepositoryInterface
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
    [DIP] Factory để tạo các service báo cáo nhỏ.
    Tránh việc một service lớn làm nhiều việc (vi phạm SRP).
    """

    def __init__(self, repo: ReportRepositoryInterface):
        self.repo = repo

    def create_financial_position_service(self) -> FinancialPositionService:
        return FinancialPositionService(self.repo)

    def create_performance_service(self) -> PerformanceService:
        return PerformanceService(self.repo)

    def create_cash_flow_service(self) -> CashFlowService:
        return CashFlowService(self.repo)

    def create_disclosure_service(self) -> DisclosureService:
        return DisclosureService(self.repo)
