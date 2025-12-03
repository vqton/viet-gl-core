# app/presentation/api/v1/accounting/periods.py
"""
API Endpoints cho quản lý Kỳ Kế Toán (Accounting Periods).

📋 TT99/2025/TT-BTC:
- Điều 25: Quản lý kỳ kế toán (mở/khóa).
- Phụ lục II: Không có tài khoản 911 → ảnh hưởng đến kết chuyển cuối kỳ.

🎯 Mục tiêu:
- Tách biệt logic nghiệp vụ ra service layer.
- Dễ mock trong test → dễ bảo trì.
- Tuân thủ nguyên tắc DIP (Dependency Inversion Principle).
"""
from datetime import date
from typing import List

from fastapi import APIRouter, Body, Depends, HTTPException, status

# ✅ Import đúng service classes (nếu bạn không có interface)
from app.application.services.accounting_periods.create_service import (
    CreateAccountingPeriodService,
)
from app.application.services.accounting_periods.lock_service import (
    LockAccountingPeriodService,
)
from app.application.services.accounting_periods.query_service import (
    QueryAccountingPeriodService,
)
from app.application.services.accounting_periods.unlock_service import (
    UnlockAccountingPeriodService,
)
from app.domain.models.accounting_period import KyKeToan as KyKeToanDomain
from app.presentation.api.v1.accounting.dependencies import (  # ✅ SỬA: Import đúng tên function từ dependencies
    get_create_period_service,
    get_lock_period_service,
    get_query_period_service,
    get_unlock_period_service,
)

# ❌ XÓA import sai
# from app.application.interfaces.period_repo import (
#     CreatePeriodServiceInterface,
#     LockPeriodServiceInterface,
#     QueryPeriodServiceInterface,
#     UnlockPeriodServiceInterface,
# )



# Tạo router cho nhóm API kỳ kế toán
router = APIRouter(
    prefix="/accounting-periods", tags=["Accounting - Period Control"]
)


# --- 1. TẠO KỲ KẾ TOÁN ---


@router.post(
    "", response_model=KyKeToanDomain, status_code=status.HTTP_201_CREATED
)
def tao_ky_ke_toan(
    payload: KyKeToanDomain,
    # ✅ SỬA: Dùng đúng tên service + interface (nếu có)
    service: CreateAccountingPeriodService = Depends(
        get_create_period_service
    ),
):
    """
    [TT99-Đ25] Tạo mới một kỳ kế toán.

    📌 Yêu cầu:
    - `ten_ky` không được trùng với kỳ đã tồn tại.
    - `ngay_bat_dau` <= `ngay_ket_thuc`.
    - `trang_thai` mặc định là "Open".

    📝 Luồng xử lý:
    1. FastAPI parse payload thành `KyKeToanDomain`.
    2. Gọi `CreatePeriodService.execute()` để xử lý nghiệp vụ.
    3. Service kiểm tra logic (trùng tên, ngày hợp lệ).
    4. Repository lưu vào DB.
    5. Trả về kỳ đã tạo.
    """
    try:
        return service.execute(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- 2. TRA CỨU KỲ KẾ TOÁN ---


@router.get("/{id}", response_model=KyKeToanDomain)
def lay_ky_ke_toan_theo_id(
    id: int,
    service: QueryAccountingPeriodService = Depends(get_query_period_service),
):
    """
    [TT99-Đ25] Lấy thông tin kỳ kế toán theo ID.

    📝 Luồng xử lý:
    - Gọi `QueryPeriodService.lay_theo_id()` để lấy dữ liệu.
    - Nếu không tìm thấy → trả về 404.
    """
    ky = service.lay_theo_id(id)
    if not ky:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Kỳ kế toán với ID {id} không tồn tại.",
        )
    return ky


@router.get("", response_model=List[KyKeToanDomain])
def lay_tat_ca_ky_ke_toan(
    service: QueryAccountingPeriodService = Depends(get_query_period_service),
):
    """
    [TT99-Đ25] Lấy danh sách tất cả kỳ kế toán.

    📝 Luồng xử lý:
    - Gọi `QueryPeriodService.lay_tat_ca()` để lấy danh sách.
    """
    return service.lay_tat_ca()


# --- 3. KHÓA KỲ KẾ TOÁN ---


@router.post("/{id}/lock")
def khoa_ky_ke_toan(
    id: int,
    nguoi_thuc_hien: str = Body(default="System", embed=True),
    service: LockAccountingPeriodService = Depends(get_lock_period_service),
):
    """
    [TT99-Đ25] Khóa kỳ kế toán.

    📌 Yêu cầu:
    - Kỳ chưa bị khóa.
    - Không còn bút toán ở trạng thái "Draft" trong kỳ.

    📝 Luồng xử lý:
    - Gọi `LockPeriodService.execute()` để xử lý nghiệp vụ.
    - Service kiểm tra điều kiện khóa kỳ.
    - Nếu hợp lệ → cập nhật trạng thái kỳ thành "Locked".
    - Trả về thông báo thành công.
    """
    try:
        success = service.execute(id, nguoi_thuc_hien=nguoi_thuc_hien)
        if success:
            return {"message": f"Kỳ {id} đã được khóa thành công.", "id": id}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể khóa kỳ (có thể đã bị khóa hoặc còn bút toán Draft).",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )


# --- 4. MỞ KỲ KẾ TOÁN ---


@router.post("/{id}/unlock")
def mo_ky_ke_toan(
    id: int,
    ly_do: str = Body(..., embed=True, description="Lý do mở kỳ (bắt buộc)"),
    nguoi_thuc_hien: str = Body(default="System", embed=True),
    service: UnlockAccountingPeriodService = Depends(
        get_unlock_period_service
    ),
):
    """
    [TT99-Đ25] Mở lại kỳ kế toán đã khóa.

    📌 Yêu cầu:
    - Kỳ phải đang ở trạng thái "Locked".
    - Phải có lý do hợp lệ (audit trail).
    - Có thể yêu cầu quyền admin hoặc phê duyệt đặc biệt (tùy doanh nghiệp).

    📝 Luồng xử lý:
    - Gọi `UnlockPeriodService.execute()` để xử lý.
    - Service kiểm tra điều kiện mở kỳ.
    - Nếu hợp lệ → cập nhật trạng thái kỳ thành "Open".
    - Trả về thông báo thành công.
    """
    try:
        success = service.execute(
            id, ly_do=ly_do, nguoi_thuc_hien=nguoi_thuc_hien
        )
        if success:
            return {
                "message": f"Kỳ {id} đã được mở thành công.",
                "ly_do": ly_do,
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Không thể mở kỳ (có thể kỳ không ở trạng thái 'Locked').",
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
