# app/presentation/api/v1/accounting/entries.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.application.services.journaling_service import JournalingService
from app.domain.models.journal_entry import JournalEntry as JournalEntryDomain
from app.presentation.api.v1.accounting.dependencies import (
    get_journaling_service,
)

router = APIRouter(
    prefix="/journal-entries", tags=["Accounting - Journal Entries"]
)


@router.post("", response_model=JournalEntryDomain, status_code=201)
def tao_phieu_ke_toan(
    entry: JournalEntryDomain,
    service: JournalingService = Depends(get_journaling_service),
):
    """
    [TT99-Đ24] Tạo bút toán kế toán.
    - Phải cân bằng Nợ = Có.
    - Có chứng từ gốc.
    """
    try:
        return service.tao_phieu_ke_toan(entry)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id}", response_model=JournalEntryDomain)
def lay_phieu_ke_toan(
    id: int, service: JournalingService = Depends(get_journaling_service)
):
    return service.lay_phieu_ke_toan_theo_id(id)


@router.get("", response_model=List[JournalEntryDomain])
def lay_tat_ca_phieu_ke_toan(
    ky_id: int = Query(None),
    service: JournalingService = Depends(get_journaling_service),
):
    if ky_id:
        return service.lay_tat_ca_phieu_ke_toan_theo_ky(ky_id)
    return service.lay_tat_ca_phieu_ke_toan()


@router.post("/{id}/post", response_model=JournalEntryDomain)
def ghi_so_phieu_ke_toan(
    id: int, service: JournalingService = Depends(get_journaling_service)
):
    """
    [TT99-Đ24] Ghi sổ bút toán (Draft → Posted).
    """
    try:
        return service.ghi_so_phieu_ke_toan(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ... các endpoint khác: PUT, DELETE, unpost...
