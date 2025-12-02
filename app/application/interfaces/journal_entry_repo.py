# app/application/interfaces/journal_entry_repo.py

from abc import ABC, abstractmethod
from datetime import date
from typing import List

from app.domain.models.journal_entry import JournalEntry


class JournalEntryRepositoryInterface(ABC):
    @abstractmethod
    def add(self, entry: JournalEntry) -> JournalEntry:
        pass

    @abstractmethod
    def get_by_id(self, id: int) -> JournalEntry:
        pass

    @abstractmethod
    def get_all(self) -> List[JournalEntry]:
        pass

    @abstractmethod
    def get_all_posted_in_range(
        self, start: date, end: date
    ) -> List[JournalEntry]:
        pass

    @abstractmethod
    def update_status(self, id: int, status: str) -> JournalEntry:
        pass
