# app/presentation/api/v1/accounting/routes.py
from http.client import HTTPException

from fastapi import APIRouter, Depends

from app.application.services.tai_khoan.create_service import (
    CreateTaiKhoanService,
)
from app.application.services.tai_khoan.query_service import (
    QueryTaiKhoanService,
)
from app.domain.models.account import TaiKhoan
from app.presentation.api.v1.accounting.dependencies import (
    get_create_tai_khoan_service,
    get_query_tai_khoan_service,
)

router = APIRouter()


@router.post("/accounts", response_model=TaiKhoan)
def create_account(
    tai_khoan: TaiKhoan,
    service: CreateTaiKhoanService = Depends(get_create_tai_khoan_service),
):
    return service.execute(tai_khoan)


@router.get("/accounts/{so_tai_khoan}", response_model=TaiKhoan)
def get_account(
    so_tai_khoan: str,
    service: QueryTaiKhoanService = Depends(get_query_tai_khoan_service),
):
    tk = service.get_by_so(so_tai_khoan)
    if not tk:
        raise HTTPException(status_code=404, detail="Tài khoản không tồn tại.")
    return tk
