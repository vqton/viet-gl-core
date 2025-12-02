# app/presentation/api/v1/accounting/accounts.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.application.services.tai_khoan_service import TaiKhoanService
from app.domain.models.account import TaiKhoan as TaiKhoanDomain
from app.presentation.api.v1.accounting.dependencies import (
    get_tai_khoan_service,
)
from app.presentation.api.v1.accounting.schemas import (
    CreateTaiKhoanRequest,
    UpdateTaiKhoanRequest,
)

router = APIRouter(prefix="/accounts", tags=["Accounting - COA"])


@router.post(
    "", response_model=TaiKhoanDomain, status_code=status.HTTP_201_CREATED
)
def tao_tai_khoan(
    request: CreateTaiKhoanRequest,  # ✅ Thay bằng request model
    service: TaiKhoanService = Depends(get_tai_khoan_service),
):
    """
    [TT99-PL2] Tạo tài khoản kế toán cấp 1, 2, 3 theo hệ thống tài khoản chuẩn.
    - Không cho phép tài khoản nhóm 9xx.
    - Không cho phép trùng số tài khoản.
    """
    tai_khoan = request.to_domain()  # ✅ Chuyển từ request sang domain
    try:
        return service.tao_tai_khoan(tai_khoan)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{so_tai_khoan}", response_model=TaiKhoanDomain)
def lay_tai_khoan(
    so_tai_khoan: str,
    service: TaiKhoanService = Depends(get_tai_khoan_service),
):
    """
    [TT99-PL2] Lấy thông tin tài khoản theo số tài khoản.
    """
    tai_khoan = service.lay_tai_khoan_theo_so(so_tai_khoan)
    if not tai_khoan:
        raise HTTPException(status_code=404, detail="Tài khoản không tồn tại.")
    return tai_khoan


@router.get("", response_model=List[TaiKhoanDomain])
def lay_tat_ca_tai_khoan(
    limit: int = Query(
        100, ge=1, le=1000, description="Số lượng tối đa tài khoản trả về"
    ),
    offset: int = Query(0, ge=0, description="Vị trí bắt đầu trả về"),
    service: TaiKhoanService = Depends(get_tai_khoan_service),
):
    """
    [TT99-PL2] Lấy danh sách tất cả tài khoản trong hệ thống.
    - Hỗ trợ phân trang để tối ưu hiệu suất.
    """
    all_accounts = service.lay_tat_ca_tai_khoan()
    return all_accounts[offset : offset + limit]


# ✅ Thêm endpoint PUT (cập nhật)
@router.put("/{so_tai_khoan}", response_model=TaiKhoanDomain)
def cap_nhat_tai_khoan(
    so_tai_khoan: str,
    request: UpdateTaiKhoanRequest,
    service: TaiKhoanService = Depends(get_tai_khoan_service),
):
    """
    [TT99-PL2] Cập nhật thông tin tài khoản kế toán.
    - Không cho phép thay đổi `so_tai_khoan`.
    - Chỉ cho phép cập nhật khi tài khoản chưa có phát sinh.
    """
    tai_khoan_hien_tai = service.lay_tai_khoan_theo_so(so_tai_khoan)
    if not tai_khoan_hien_tai:
        raise HTTPException(status_code=404, detail="Tài khoản không tồn tại.")

    # Gộp dữ liệu mới vào tài khoản hiện tại
    updated_data = request.dict(exclude_unset=True)
    for k, v in updated_data.items():
        setattr(tai_khoan_hien_tai, k, v)

    try:
        return service.cap_nhat_tai_khoan(tai_khoan_hien_tai)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ✅ Thêm endpoint DELETE (xóa)
@router.delete("/{so_tai_khoan}", status_code=status.HTTP_204_NO_CONTENT)
def xoa_tai_khoan(
    so_tai_khoan: str,
    service: TaiKhoanService = Depends(get_tai_khoan_service),
):
    """
    [TT99-PL2] Xóa tài khoản kế toán.
    - Chỉ được phép xóa nếu tài khoản chưa có phát sinh.
    """
    tai_khoan = service.lay_tai_khoan_theo_so(so_tai_khoan)
    if not tai_khoan:
        raise HTTPException(status_code=404, detail="Tài khoản không tồn tại.")

    try:
        success = service.xoa_tai_khoan(so_tai_khoan)
        if not success:
            raise HTTPException(
                status_code=400,
                detail="Không thể xóa tài khoản vì đã có phát sinh.",
            )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
