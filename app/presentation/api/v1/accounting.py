# File: app/presentation/api/v1/accounting.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.application.services.tai_khoan_service import TaiKhoanService
from app.domain.models.account import TaiKhoan as TaiKhoanDomain
from app.infrastructure.repositories.account_repository import AccountRepository
from app.infrastructure.database import get_db # Import dependency để lấy DB session

router = APIRouter(prefix="/accounting", tags=["Accounting - Kế toán"])

# Dependency để lấy TaiKhoanService
def get_tai_khoan_service(db: Session = Depends(get_db)) -> TaiKhoanService:
    repository = AccountRepository(db_session=db)
    return TaiKhoanService(repository=repository)

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

@router.get("/accounts/{so_tai_khoan}", response_model=TaiKhoanDomain)
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

# (Có thể thêm các endpoint khác như PUT /accounts/{id}, DELETE /accounts/{id} nếu cần)