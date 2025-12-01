from fastapi import APIRouter, Depends, HTTPException, Body, Query, status
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional

# Import Services
from app.application.services.tai_khoan_service import TaiKhoanService
from app.application.services.journaling_service import JournalingService
from app.application.services.reporting_service import ReportingService
from app.application.services.accounting_period_service import AccountingPeriodService

# Import Domain Models (Sử dụng làm DTOs)
from app.domain.models.account import TaiKhoan as TaiKhoanDomain
from app.domain.models.journal_entry import JournalEntry as JournalEntryDomain
from app.domain.models.report import (
    BaoCaoTinhHinhTaiChinh,
    BaoCaoKetQuaHDKD,
    BaoCaoLuuChuyenTienTe,
    BaoCaoThuyetMinh,
)
from app.domain.models.accounting_period import KyKeToan as KyKeToanDomain

# Import Repositories (cần cho DI)
from app.infrastructure.repositories.account_repository import AccountRepository
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.infrastructure.repositories.accounting_period_repository import AccountingPeriodRepository
from app.infrastructure.database import get_db

router = APIRouter(prefix="/accounting/v1", tags=["Accounting - Kế toán"])

# --- Dependencies Setup ---
# Cung cấp TaiKhoanService
def get_tai_khoan_service(db: Session = Depends(get_db)) -> TaiKhoanService:
    repo = AccountRepository(db)
    return TaiKhoanService(repository=repo)

# Cung cấp AccountingPeriodService
def get_accounting_period_service(db: Session = Depends(get_db)) -> AccountingPeriodService:
    period_repo = AccountingPeriodRepository(db)
    journal_repo = JournalEntryRepository(db)
    return AccountingPeriodService(repository=period_repo, journal_entry_repo=journal_repo)

# Cung cấp JournalingService
def get_journaling_service(
    db: Session = Depends(get_db),
    accounting_period_service: AccountingPeriodService = Depends(get_accounting_period_service)
) -> JournalingService:
    journal_repo = JournalEntryRepository(db)
    account_repo = AccountRepository(db)
    # Inject AccountingPeriodService vào JournalingService để kiểm tra khóa sổ
    return JournalingService(repository=journal_repo, account_repository=account_repo, accounting_period_service=accounting_period_service)

# Cung cấp ReportingService
def get_reporting_service(db: Session = Depends(get_db)) -> ReportingService:
    journal_repo = JournalEntryRepository(db)
    account_repo = AccountRepository(db)
    return ReportingService(journal_entry_repo=journal_repo, account_repo=account_repo)


# ==============================================================================
# 1. TÀI KHOẢN (CHART OF ACCOUNTS - COA)
# ==============================================================================

@router.post("/accounts", response_model=TaiKhoanDomain, status_code=status.HTTP_201_CREATED, tags=["Accounting - COA"])
def tao_tai_khoan(
    tai_khoan: TaiKhoanDomain,
    service: TaiKhoanService = Depends(get_tai_khoan_service)
):
    """
    Tạo mới một tài khoản kế toán (GL-01).
    """
    try:
        return service.tao_tai_khoan(tai_khoan)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {e}")

@router.get("/accounts/{so_tai_khoan}", response_model=TaiKhoanDomain, tags=["Accounting - COA"])
def lay_tai_khoan(
    so_tai_khoan: str,
    service: TaiKhoanService = Depends(get_tai_khoan_service)
):
    """
    Lấy thông tin chi tiết của một tài khoản theo số tài khoản (GL-02).
    """
    tai_khoan = service.lay_tai_khoan_theo_so(so_tai_khoan)
    if not tai_khoan:
        raise HTTPException(status_code=404, detail="Không tìm thấy tài khoản")
    return tai_khoan

@router.get("/accounts", response_model=List[TaiKhoanDomain], tags=["Accounting - COA"])
def lay_tat_ca_tai_khoan(
    service: TaiKhoanService = Depends(get_tai_khoan_service)
):
    """
    Lấy danh sách tất cả các tài khoản trong hệ thống (GL-02).
    """
    return service.lay_tat_ca_tai_khoan()

# ==============================================================================
# 2. KỲ KẾ TOÁN (ACCOUNTING PERIODS)
# ==============================================================================

@router.post("/accounting-periods", response_model=KyKeToanDomain, status_code=status.HTTP_201_CREATED, tags=["Accounting - Period Control"])
def tao_ky_ke_toan(
    ky_ke_toan: KyKeToanDomain,
    service: AccountingPeriodService = Depends(get_accounting_period_service)
):
    """
    Tạo mới một kỳ kế toán (GL-04).
    """
    try:
        return service.tao_ky_ke_toan(ky_ke_toan)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {e}")

@router.get("/accounting-periods/{id}", response_model=KyKeToanDomain, tags=["Accounting - Period Control"])
def lay_ky_ke_toan(
    id: int,
    service: AccountingPeriodService = Depends(get_accounting_period_service)
):
    """
    Lấy thông tin chi tiết của một kỳ kế toán (GL-04).
    """
    ky = service.lay_ky_ke_toan_theo_id(id)
    if not ky:
        raise HTTPException(status_code=404, detail="Không tìm thấy kỳ kế toán")
    return ky

@router.get("/accounting-periods", response_model=List[KyKeToanDomain], tags=["Accounting - Period Control"])
def lay_tat_ca_ky_ke_toan(
    service: AccountingPeriodService = Depends(get_accounting_period_service)
):
    """
    Lấy danh sách tất cả các kỳ kế toán (GL-04).
    """
    return service.lay_tat_ca_ky_ke_toan()


@router.post("/accounting-periods/{id}/lock", tags=["Accounting - Period Control"])
def khoa_ky(
    id: int,
    nguoi_thuc_hien: str = Body(default="System", embed=True), # Nhận người thực hiện từ body (tùy chọn)
    service: AccountingPeriodService = Depends(get_accounting_period_service)
):
    """
    Khóa sổ kế toán cho kỳ đã cho (GL-05).
    Yêu cầu: Đảm bảo tất cả bút toán đã được ghi sổ.
    """
    try:
        success = service.khoa_ky(id, nguoi_thuc_hien=nguoi_thuc_hien)
        if success:
            return {"message": f"Kỳ {id} đã được khóa thành công."}
        else:
            raise HTTPException(status_code=400, detail="Không thể khóa kỳ (có thể đã bị khóa hoặc có bút toán chưa ghi sổ).")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống khi khóa kỳ: {e}")


@router.post("/accounting-periods/{id}/unlock", tags=["Accounting - Period Control"])
def mo_ky(
    id: int,
    reason: str = Body(..., embed=True), # Lý do mở lại (bắt buộc)
    nguoi_thuc_hien: str = Body(default="System", embed=True), # Nhận người thực hiện từ body (tùy chọn)
    service: AccountingPeriodService = Depends(get_accounting_period_service)
):
    """
    Mở sổ kế toán cho kỳ đã cho (GL-05).
    Yêu cầu: Phải có lý do chính đáng và quyền hạn.
    """
    try:
        success = service.mo_ky(id, ly_do=reason, nguoi_thuc_hien=nguoi_thuc_hien)
        if success:
            return {"message": f"Kỳ {id} đã được mở thành công. Lý do: {reason}"}
        else:
            raise HTTPException(status_code=400, detail="Không thể mở kỳ (có thể kỳ không ở trạng thái 'Locked').")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống khi mở kỳ: {e}")


# ==============================================================================
# 3. BÚT TOÁN KẾ TOÁN (JOURNAL ENTRIES)
# ==============================================================================

@router.post("/journal-entries", response_model=JournalEntryDomain, status_code=status.HTTP_201_CREATED, tags=["Accounting - Journal Entries"])
def tao_phieu_ke_toan(
    journal_entry: JournalEntryDomain,
    service: JournalingService = Depends(get_journaling_service)
):
    """
    Tạo mới một bút toán kế toán (GL-06).
    """
    try:
        return service.tao_phieu_ke_toan(journal_entry)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {e}")

@router.get("/journal-entries/{id}", response_model=JournalEntryDomain, tags=["Accounting - Journal Entries"])
def lay_phieu_ke_toan(
    id: int,
    service: JournalingService = Depends(get_journaling_service)
):
    """
    Lấy thông tin chi tiết của một bút toán (GL-07).
    """
    journal_entry = service.lay_phieu_ke_toan_theo_id(id)
    if not journal_entry:
        raise HTTPException(status_code=404, detail="Không tìm thấy bút toán")
    return journal_entry

@router.get("/journal-entries", response_model=List[JournalEntryDomain], tags=["Accounting - Journal Entries"])
def lay_tat_ca_phieu_ke_toan(
    ky_id: Optional[int] = Query(None, description="Lọc theo ID kỳ kế toán"),
    service: JournalingService = Depends(get_journaling_service)
):
    """
    Lấy danh sách tất cả các bút toán. Có thể lọc theo ID kỳ kế toán (GL-07).
    """
    if ky_id is not None:
        return service.lay_tat_ca_phieu_ke_toan_theo_ky(ky_id)
    return service.lay_tat_ca_phieu_ke_toan()

@router.put("/journal-entries/{id}", response_model=JournalEntryDomain, tags=["Accounting - Journal Entries"])
def cap_nhat_phieu_ke_toan(
    id: int,
    journal_entry: JournalEntryDomain,
    service: JournalingService = Depends(get_journaling_service)
):
    """
    Cập nhật nội dung bút toán (chỉ được phép khi trạng thái là 'Draft') (GL-08).
    """
    try:
        updated_entry = service.cap_nhat_phieu_ke_toan(id, journal_entry)
        if not updated_entry:
            raise HTTPException(status_code=404, detail="Không tìm thấy bút toán")
        return updated_entry
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {e}")

@router.delete("/journal-entries/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Accounting - Journal Entries"])
def xoa_phieu_ke_toan(
    id: int,
    service: JournalingService = Depends(get_journaling_service)
):
    """
    Xóa một bút toán (chỉ được phép khi trạng thái là 'Draft') (GL-08).
    """
    try:
        success = service.xoa_phieu_ke_toan(id)
        if not success:
            raise HTTPException(status_code=404, detail="Không tìm thấy bút toán để xóa")
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {e}")

@router.post("/journal-entries/{id}/post", response_model=JournalEntryDomain, tags=["Accounting - Journal Entries"])
def ghi_so_phieu_ke_toan(
    id: int,
    service: JournalingService = Depends(get_journaling_service)
):
    """
    Ghi sổ (Post) một bút toán: chuyển trạng thái từ 'Draft' sang 'Posted' (GL-09).
    """
    try:
        posted_entry = service.ghi_so_phieu_ke_toan(id)
        if not posted_entry:
            raise HTTPException(status_code=404, detail="Không tìm thấy bút toán để ghi sổ")
        return posted_entry
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống khi ghi sổ: {e}")

@router.post("/journal-entries/{id}/unpost", response_model=JournalEntryDomain, tags=["Accounting - Journal Entries"])
def huy_ghi_so_phieu_ke_toan(
    id: int,
    service: JournalingService = Depends(get_journaling_service)
):
    """
    Hủy ghi sổ (Unpost) một bút toán: chuyển trạng thái từ 'Posted' trở lại 'Draft' (GL-09).
    """
    try:
        unposted_entry = service.huy_ghi_so_phieu_ke_toan(id)
        if not unposted_entry:
            raise HTTPException(status_code=404, detail="Không tìm thấy bút toán để hủy ghi sổ")
        return unposted_entry
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống khi hủy ghi sổ: {e}")

# ==============================================================================
# 4. BÁO CÁO TÀI CHÍNH (FINANCIAL REPORTS - Theo TT99/2025/TT-BTC)
# ==============================================================================

@router.get("/reports/financial-position", response_model=BaoCaoTinhHinhTaiChinh, tags=["Accounting - Reports"])
def lay_bao_cao_tinh_hinh_tai_chinh(
    ky_hieu: str = Query(..., description="Kỳ báo cáo (ví dụ: 'Q4/2025')"),
    ngay_lap: date = Query(..., description="Ngày lập báo cáo"),
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Lấy Báo cáo tình hình tài chính (B01-DN) (GL-10).
    """
    try:
        return service.lay_bao_cao_tinh_hinh_tai_chinh(ky_hieu=ky_hieu, ngay_lap=ngay_lap)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống khi tạo báo cáo: {e}")

@router.get("/reports/performance", response_model=BaoCaoKetQuaHDKD, tags=["Accounting - Reports"])
def lay_bao_cao_ket_qua_hdkd(
    ky_hieu: str = Query(..., description="Kỳ báo cáo (ví dụ: 'Năm 2025')"),
    ngay_lap: date = Query(..., description="Ngày lập báo cáo"),
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Lấy Báo cáo kết quả hoạt động kinh doanh (B02-DN) (GL-10).
    """
    try:
        return service.lay_bao_cao_ket_qua_hdkd(ky_hieu=ky_hieu, ngay_lap=ngay_lap)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống khi tạo báo cáo: {e}")

@router.get("/reports/cash-flow", response_model=BaoCaoLuuChuyenTienTe, tags=["Accounting - Reports"])
def lay_bao_cao_luu_chuyen_tien_te(
    ky_hieu: str = Query(..., description="Kỳ báo cáo (ví dụ: 'Q1/2025')"),
    ngay_lap: date = Query(..., description="Ngày lập báo cáo"),
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Lấy Báo cáo lưu chuyển tiền tệ (B03-DN) (GL-10).
    """
    try:
        return service.lay_bao_cao_luu_chuyen_tien_te(ky_hieu=ky_hieu, ngay_lap=ngay_lap)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống khi tạo báo cáo: {e}")

@router.get("/reports/disclosure", response_model=BaoCaoThuyetMinh, tags=["Accounting - Reports"])
def lay_ban_thuyet_minh(
    ky_hieu: str = Query(..., description="Kỳ báo cáo"),
    ngay_lap: date = Query(..., description="Ngày lập báo cáo"),
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Lấy Bản thuyết minh Báo cáo tài chính (B09-DN) (GL-10).
    """
    try:
        return service.lay_ban_thuyet_minh(ky_hieu=ky_hieu, ngay_lap=ngay_lap)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống khi tạo báo cáo: {e}")