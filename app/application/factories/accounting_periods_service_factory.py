# app/application/services/accounting_periods/service_factory.py
"""
Factory tạo các service nhỏ cho kỳ kế toán.
[OCP] Dễ mở rộng thêm service mới nếu cần.
[DIP] Tránh phụ thuộc trực tiếp vào implementation.
"""
from app.application.interfaces.period_repo import AccountingPeriodRepositoryInterface
from app.application.services.accounting_periods.unlock_service import UnlockAccountingPeriodService
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.application.services.accounting_periods.create_service import CreateAccountingPeriodService
from app.application.services.accounting_periods.lock_service import LockAccountingPeriodService
from app.application.services.accounting_periods.query_service import QueryAccountingPeriodService

class AccountingPeriodServiceFactory:
    def __init__(self, period_repo: AccountingPeriodRepositoryInterface, je_repo: JournalEntryRepository):
        self.period_repo = period_repo
        self.je_repo = je_repo

    def create_create_service(self) -> CreateAccountingPeriodService:
        return CreateAccountingPeriodService(self.period_repo)

    def create_lock_service(self) -> LockAccountingPeriodService:
        return LockAccountingPeriodService(self.period_repo, self.je_repo)

    def create_query_service(self) -> QueryAccountingPeriodService:
        return QueryAccountingPeriodService(self.period_repo)
    
    def create_unlock_service(self) -> UnlockAccountingPeriodService:
        return UnlockAccountingPeriodService(self.period_repo) 