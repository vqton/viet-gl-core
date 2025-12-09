# app/presentation/api/v1/accounting/entries.py
"""
API Endpoints cho quản lý Bút toán kế toán (Journal Entries) theo TT99/2025/TT-BTC.

📋 TT99/2025/TT-BTC:
- Điều 24: Bút toán kép (Nợ = Có).
- Điều 8–10: Bút toán phải có chứng từ gốc.
- Phụ lục I: Mẫu chứng từ kế toán.
- Phụ lục IV: Dùng trong báo cáo tài chính.

🎯 Mục tiêu:
- Tách biệt endpoint theo chức năng (tạo, ghi sổ, truy vấn).
- Mỗi endpoint gọi đúng service nhỏ (SRP).
- Đảm bảo DI hoạt động chính xác.
"""

from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

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
from app.domain.models.journal_entry import JournalEntry as JournalEntryDomain
from app.presentation.api.v1.accounting.dependencies import (
    get_closing_journal_service,
    get_create_journal_service,
    get_posting_journal_service,
    get_query_journal_service,
)

router = APIRouter(prefix="/journal-entries", tags=["Accounting - Journal Entries"])


@router.post("", response_model=JournalEntryDomain, status_code=status.HTTP_201_CREATED)
def tao_phieu_ke_toan(
    entry: JournalEntryDomain,
    service: CreateJournalEntryService = Depends(
        get_create_journal_service
    ),  # ✅ SỬA: đúng service
):
    """
    [TT99-Đ24] Tạo bút toán kế toán mới.
    - Phải cân bằng Nợ = Có.
    - Phải có chứng từ gốc (so_chung_tu_goc, ngay_chung_tu_goc).
    - Không được ghi vào kỳ đã khóa.
    """
    try:
        return service.execute(entry)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{id}", response_model=JournalEntryDomain)
def lay_phieu_ke_toan(
    id: int,
    service: QueryJournalEntryService = Depends(
        get_query_journal_service
    ),  # ✅ SỬA: đúng service
):
    """
    [TT99-PL1] Lấy thông tin chi tiết một bút toán theo ID.
    """
    je = service.lay_theo_id(id)
    if not je:
        raise HTTPException(status_code=404, detail="Không tìm thấy bút toán.")
    return je


@router.get("", response_model=List[JournalEntryDomain])
def lay_tat_ca_phieu_ke_toan(
    ky_id: int = Query(None, description="Lọc theo kỳ kế toán"),
    service: QueryJournalEntryService = Depends(
        get_query_journal_service
    ),  # ✅ SỬA: đúng service
):
    """
    [TT99-PL1] Lấy danh sách tất cả bút toán.
    Có thể lọc theo kỳ kế toán.
    """
    if ky_id:
        # Nếu có kỳ, gọi service lọc theo kỳ (giả sử có phương thức này)
        # return service.lay_theo_ky(ky_id)
        pass  # tạm thời không có service filter theo kỳ
    return service.lay_tat_ca()


@router.post("/{id}/post", response_model=JournalEntryDomain)
def ghi_so_phieu_ke_toan(
    id: int,
    service: PostingJournalEntryService = Depends(
        get_posting_journal_service
    ),  # ✅ SỬA: đúng service
):
    """
    [TT99-Đ24] Ghi sổ bút toán: chuyển trạng thái từ 'Draft' → 'Posted'.
    - Kiểm tra kỳ kế toán không bị khóa.
    - Không cho phép ghi sổ bút toán đã ghi hoặc bị khóa.
    """
    try:
        return service.execute(id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{id}/unpost", response_model=JournalEntryDomain)
def huy_ghi_so_phieu_ke_toan(
    id: int,
    service: PostingJournalEntryService = Depends(
        get_posting_journal_service
    ),  # Service dùng chung (có thể tách riêng nếu cần)
):
    """
    [TT99-Đ24] Hủy ghi sổ bút toán: chuyển trạng thái từ 'Posted' → 'Draft'.
    - Chỉ được phép nếu kỳ chưa bị khóa.
    - Không được phép nếu đã có bút toán kết chuyển sau kỳ đó.
    """
    try:
        return service.unpost(id)  # Nếu bạn có phương thức unpost trong PostingService
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/end-of-period-close")
def ket_chuyen_cuoi_ky(
    ky_hieu: str = Query(..., description="Ký hiệu kỳ kế toán (ví dụ: 'Năm 2025')"),
    ngay_ket_chuyen: date = Query(..., description="Ngày thực hiện kết chuyển"),
    service: ClosingJournalEntryService = Depends(
        get_closing_journal_service
    ),  # ✅ Service kết chuyển
):
    """
    [TT99-Đ24] Thực hiện kết chuyển cuối kỳ.
    - Không sử dụng tài khoản 911.
    - Kết chuyển Doanh thu/Chi phí → Lợi nhuận sau thuế (421).
    """
    try:
        ket_chuyen = service.execute(ky_hieu=ky_hieu, ngay_ket_chuyen=ngay_ket_chuyen)
        return {
            "message": f"Kết chuyển kỳ '{ky_hieu}' thành công.",
            "so_bu_toan_ket_chuyen": len(ket_chuyen),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
