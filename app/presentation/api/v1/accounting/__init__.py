# app/presentation/api/v1/accounting/__init__.py
from fastapi import APIRouter

from . import accounts, entries, periods, reports

router = APIRouter(prefix="/accounting/v1")

router.include_router(accounts.router)
router.include_router(periods.router)
router.include_router(entries.router)
router.include_router(reports.router)
