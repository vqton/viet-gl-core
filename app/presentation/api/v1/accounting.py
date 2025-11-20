# File: app/presentation/api/v1/accounting.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.application.services.tai_khoan_service import TaiKhoanService
from app.application.services.journaling_service import JournalingService # Import service mới
from app.domain.models.account import TaiKhoan as TaiKhoanDomain
from app.domain.models.journal_entry import JournalEntry as JournalEntryDomain # Import domain mới
from app.infrastructure.repositories.account_repository import AccountRepository
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository # Import repo mới
from app.infrastructure.database import get_db
from typing import List, Optional # Đảm bảo Optional đã được import

router = APIRouter(prefix="/accounting", tags=["Accounting - Kế toán"])

# Dependency để lấy TaiKhoanService
def get_tai_khoan_service(db: Session = Depends(get_db)) -> TaiKhoanService:
    repository = AccountRepository(db_session=db)
    return TaiKhoanService(repository=repository)

# Dependency để lấy JournalingService
def get_journaling_service(db: Session = Depends(get_db)) -> JournalingService:
    je_repo = JournalEntryRepository(db_session=db)
    acc_repo = AccountRepository(db_session=db) # Cung cấp repo tài khoản cho service
    return JournalingService(repository=je_repo, account_repository=acc_repo)

@router.post("/accounts/", response_model=TaiKhoanDomain)
def tao_tai_khoan(tai_khoan: TaiKhoanDomain, service: TaiKhoanService = Depends(get_tai_khoan_service)):
    """
    Tạo mới một tài khoản kế toán.
    """
    try:
        tai_khoan_moi = service.tao_tai_khoan(tai_khoan)
        return tai_khoan_moi
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Có thể log lỗi ở đây
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi tạo tài khoản.")

@router.get("/accounts/{so_tai_khoan}", response_model=Optional[TaiKhoanDomain])
def lay_tai_khoan(so_tai_khoan: str, service: TaiKhoanService = Depends(get_tai_khoan_service)):
    """
    Lấy thông tin tài khoản theo số tài khoản.
    """
    tai_khoan = service.lay_tai_khoan_theo_so(so_tai_khoan)
    if not tai_khoan:
        raise HTTPException(status_code=404, detail="Tài khoản không tồn tại.")
    return tai_khoan

@router.get("/accounts/", response_model=List[TaiKhoanDomain])
def lay_danh_sach_tai_khoan(service: TaiKhoanService = Depends(get_tai_khoan_service)):
    """
    Lấy danh sách tất cả tài khoản.
    """
    danh_sach = service.lay_danh_sach_tai_khoan()
    return danh_sach

# --- API cho Journal Entry ---
@router.post("/journal-entries/", response_model=JournalEntryDomain)
def tao_phieu_ke_toan(journal_entry: JournalEntryDomain, service: JournalingService = Depends(get_journaling_service)):
    """
    Tạo mới một bút toán kế toán.
    """
    try:
        phieu_moi = service.tao_phieu_ke_toan(journal_entry)
        return phieu_moi
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Có thể log lỗi ở đây
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi tạo bút toán.")

@router.get("/journal-entries/{id}", response_model=Optional[JournalEntryDomain])
def lay_phieu_ke_toan_theo_id(id: int, service: JournalingService = Depends(get_journaling_service)):
    """
    Lấy thông tin bút toán theo ID.
    """
    phieu = service.lay_phieu_ke_toan_theo_id(id)
    if not phieu:
        raise HTTPException(status_code=404, detail="Bút toán không tồn tại.")
    return phieu

@router.get("/journal-entries/", response_model=List[JournalEntryDomain])
def lay_danh_sach_phieu_ke_toan(service: JournalingService = Depends(get_journaling_service)):
    """
    Lấy danh sách tất cả bút toán.
    """
    danh_sach = service.lay_danh_sach_phieu_ke_toan()
    return danh_sach

# (Có thể thêm các endpoint khác như PUT /journal-entries/{id}, DELETE /journal-entries/{id} nếu cần)