from fastapi import APIRouter, Depends

from app.application.services.journaling.create_service import (
    CreateJournalEntryService,
)
from app.domain.models.journal_entry import JournalEntry
from app.presentation.api.v1.accounting.dependencies import (
    get_create_journal_service,
)

router = APIRouter()


@router.post("/journal-entries", ...)
def create_journal_entry(
    entry: JournalEntry,
    service: CreateJournalEntryService = Depends(get_create_journal_service),
):
    return service.execute(entry)
