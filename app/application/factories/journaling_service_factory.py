# app/application/factories/journaling_service_factory.py
from app.application.interfaces.account_repo import AccountRepositoryInterface
from app.application.interfaces.accounting_period_service import (
    AccountingPeriodServiceInterface,
)
from app.application.interfaces.journal_entry_repo import (
    JournalEntryRepositoryInterface,
)
from app.application.services.journaling.closing_service import (
    ClosingJournalEntryService,
)
from app.application.services.journaling.create_service import (
    CreateJournalEntryService,
)
from app.application.services.journaling.posting_service import (
    PostingJournalEntryService,
)
from app.application.services.journaling.query_service import (
    QueryJournalEntryService,
)


class JournalingServiceFactory:
    def __init__(
        self,
        je_repo: JournalEntryRepositoryInterface,
        acc_repo: AccountRepositoryInterface,
        period_service: AccountingPeriodServiceInterface,
    ):
        self.je_repo = je_repo
        self.acc_repo = acc_repo
        self.period_service = period_service

    def create_create_service(self):
        return CreateJournalEntryService(
            self.je_repo, self.acc_repo, self.period_service
        )

    def create_posting_service(self):
        return PostingJournalEntryService(self.je_repo, self.period_service)

    def create_query_service(self):
        return QueryJournalEntryService(self.je_repo)

    def create_closing_service(self):
        return ClosingJournalEntryService(self.je_repo, self.acc_repo)
