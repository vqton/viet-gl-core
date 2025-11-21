# File: app/presentation/api/v1/accounting.py

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.application.services.tai_khoan_service import TaiKhoanService
from app.application.services.journaling_service import JournalingService
from app.application.services.reporting_service import ReportingService
from app.application.services.accounting_period_service import AccountingPeriodService # Thêm import
from app.domain.models.account import TaiKhoan as TaiKhoanDomain
from app.domain.models.journal_entry import JournalEntry as JournalEntryDomain
from app.domain.models.report import ( # Import các model báo cáo
    BaoCaoTinhHinhTaiChinh,
    BaoCaoKetQuaHDKD,
    BaoCaoLuuChuyenTienTe,
    BaoCaoThuyetMinh,
)
from app.infrastructure.repositories.account_repository import AccountRepository
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.infrastructure.database import get_db
from typing import List, Optional
from datetime import date # Thêm import date

router = APIRouter(prefix="/accounting", tags=["Accounting - Kế toán"])

# Dependency để lấy TaiKhoanService
def get_tai_khoan_service(db: Session = Depends(get_db)) -> TaiKhoanService:
    repository = AccountRepository(db_session=db)
    return TaiKhoanService(repository=repository)

# Dependency để lấy JournalingService
def get_journaling_service(db: Session = Depends(get_db)) -> JournalingService:
    je_repo = JournalEntryRepository(db_session=db)
    acc_repo = AccountRepository(db_session=db)
    return JournalingService(repository=je_repo, account_repository=acc_repo)

# Dependency để lấy ReportingService
def get_reporting_service(db: Session = Depends(get_db)) -> ReportingService:
    je_repo = JournalEntryRepository(db_session=db)
    acc_repo = AccountRepository(db_session=db)
    return ReportingService(journal_entry_repo=je_repo, account_repo=acc_repo)

# Dependency để lấy AccountingPeriodService
def get_accounting_period_service(db: Session = Depends(get_db)) -> AccountingPeriodService:
    je_repo = JournalEntryRepository(db_session=db) # Có thể cần repo khác nếu AccountingPeriod có repo riêng
    return AccountingPeriodService(journal_entry_repo=je_repo)


# --- API cho Danh mục Tài khoản (MST-03) ---
@router.post("/accounts/", response_model=TaiKhoanDomain, tags=["Accounting - Master Data"])
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
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi tạo tài khoản.")

@router.get("/accounts/{so_tai_khoan}", response_model=Optional[TaiKhoanDomain], tags=["Accounting - Master Data"])
def lay_tai_khoan(so_tai_khoan: str, service: TaiKhoanService = Depends(get_tai_khoan_service)):
    """
    Lấy thông tin tài khoản theo số tài khoản.
    """
    tai_khoan = service.lay_tai_khoan_theo_so(so_tai_khoan)
    if not tai_khoan:
        raise HTTPException(status_code=404, detail="Tài khoản không tồn tại.")
    return tai_khoan

@router.get("/accounts/", response_model=List[TaiKhoanDomain], tags=["Accounting - Master Data"])
def lay_danh_sach_tai_khoan(service: TaiKhoanService = Depends(get_tai_khoan_service)):
    """
    Lấy danh sách tất cả tài khoản.
    """
    danh_sach = service.lay_danh_sach_tai_khoan()
    return danh_sach


# --- API cho Bút toán kế toán (GL-01) ---
@router.post("/journal-entries/", response_model=JournalEntryDomain, tags=["Accounting - General Ledger"])
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
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi tạo bút toán.")

@router.get("/journal-entries/{id}", response_model=Optional[JournalEntryDomain], tags=["Accounting - General Ledger"])
def lay_phieu_ke_toan_theo_id(id: int, service: JournalingService = Depends(get_journaling_service)):
    """
    Lấy thông tin bút toán theo ID.
    """
    phieu = service.lay_phieu_ke_toan_theo_id(id)
    if not phieu:
        raise HTTPException(status_code=404, detail="Bút toán không tồn tại.")
    return phieu

@router.get("/journal-entries/", response_model=List[JournalEntryDomain], tags=["Accounting - General Ledger"])
def lay_danh_sach_phieu_ke_toan(service: JournalingService = Depends(get_journaling_service)):
    """
    Lấy danh sách tất cả bút toán.
    """
    danh_sach = service.lay_danh_sach_phieu_ke_toan()
    return danh_sach


# --- API cho Báo cáo tài chính (GL-RPT) ---
@router.get("/reports/b01-dn", response_model=BaoCaoTinhHinhTaiChinh, tags=["Accounting - Reports"])
def lay_bao_cao_tinh_hinh_tai_chinh(
    ky_hieu: str = "Năm 2025",
    ngay_lap: date = date.today(),
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Lấy Báo cáo tình hình tài chính (B01-DN).
    """
    # Gọi phương thức từ service (cần được hoàn thiện logic tính toán)
    return service.lay_bao_cao_tinh_hinh_tai_chinh(ky_hieu=ky_hieu, ngay_lap=ngay_lap)

@router.get("/reports/b02-dn", response_model=BaoCaoKetQuaHDKD, tags=["Accounting - Reports"])
def lay_bao_cao_ket_qua_hdkd(
    ky_hieu: str = "Năm 2025",
    ngay_lap: date = date.today(),
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Lấy Báo cáo kết quả hoạt động kinh doanh (B02-DN).
    """
    # Gọi phương thức từ service (cần được hoàn thiện logic tính toán)
    return service.lay_bao_cao_ket_qua_hdkd(ky_hieu=ky_hieu, ngay_lap=ngay_lap)

@router.get("/reports/b03-dn", response_model=BaoCaoLuuChuyenTienTe, tags=["Accounting - Reports"])
def lay_bao_cao_luu_chuyen_tien_te(
    ky_hieu: str = "Năm 2025",
    ngay_lap: date = date.today(),
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Lấy Báo cáo lưu chuyển tiền tệ (B03-DN).
    """
    # Gọi phương thức từ service (cần được hoàn thiện logic tính toán)
    return service.lay_bao_cao_luu_chuyen_tien_te(ky_hieu=ky_hieu, ngay_lap=ngay_lap)

@router.get("/reports/b09-dn", response_model=BaoCaoThuyetMinh, tags=["Accounting - Reports"])
def lay_bao_cao_thuyet_minh(
    ky_hieu: str = "Năm 2025",
    ngay_lap: date = date.today(),
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Lấy Bản thuyết minh Báo cáo tài chính (B09-DN).
    """
    # Gọi phương thức từ service (cần được hoàn thiện logic tính toán)
    return service.lay_bao_cao_thuyet_minh(ky_hieu=ky_hieu, ngay_lap=ngay_lap)


# --- API cho Kết chuyển cuối kỳ (GL-04) ---
@router.post("/journal-entries/ket-chuyen-cuoi-ky", response_model=JournalEntryDomain, tags=["Accounting - General Ledger"])
def ket_chuyen_cuoi_ky(
    ky_hieu: str,
    ngay_ket_chuyen: date = date.today(),
    journaling_service: JournalingService = Depends(get_journaling_service),
    reporting_service: ReportingService = Depends(get_reporting_service) # Có thể cần để lấy số liệu trước kết chuyển
):
    """
    Tự động tạo bút toán kết chuyển cuối kỳ (GL-04).
    """
    try:
        # Gọi phương thức kết chuyển trong service (cần được hoàn thiện logic)
        # entry = journaling_service.ket_chuyen_tu_dong(ky_hieu, ngay_ket_chuyen)
        # Trả về mẫu giả lập
        from app.domain.models.journal_entry import JournalEntryLine # Import tạm thời nếu cần
        from decimal import Decimal
        return JournalEntryDomain( # Trả về mẫu giả lập
            id=999,
            ngay_ct=ngay_ket_chuyen,
            so_phieu=f"KT-{ky_hieu}",
            mo_ta=f"Bút toán kết chuyển kỳ {ky_hieu}",
            lines=[JournalEntryLine(so_tai_khoan="911", no=Decimal('0'), co=Decimal('1000000'))], # Ví dụ
            trang_thai="Posted"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi kết chuyển.")


# --- API cho Khóa/Mở kỳ kế toán (GL-05) ---
@router.post("/accounting-periods/{period_id}/lock", tags=["Accounting - Period Control"])
def khoa_ky(
    period_id: int,
    service: AccountingPeriodService = Depends(get_accounting_period_service)
):
    """
    Khóa sổ kế toán cho kỳ đã cho (GL-05).
    Yêu cầu: Phải có quyền Admin hoặc kế toán trưởng.
    """
    try:
        # service.khoa_ky(period_id) # Gọi phương thức trong service
        # Trả về thông tin kỳ đã khóa hoặc message thành công
        return {"message": f"Kỳ {period_id} đã được khóa thành công."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi khóa kỳ.")

@router.post("/accounting-periods/{period_id}/unlock", tags=["Accounting - Period Control"])
def mo_ky(
    period_id: int,
    reason: str = Body(..., embed=True), # Lý do mở lại
    service: AccountingPeriodService = Depends(get_accounting_period_service)
):
    """
    Mở sổ kế toán cho kỳ đã cho (GL-05).
    Yêu cầu: Phải có quyền Admin và lý do chính đáng.
    """
    try:
        # service.mo_ky(period_id, reason) # Gọi phương thức trong service
        # Trả về thông tin kỳ đã mở hoặc message thành công
        return {"message": f"Kỳ {period_id} đã được mở thành công."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi mở kỳ.")
@router.post("/journal-entries/ket-chuyen-cuoi-ky", response_model=List[JournalEntryDomain], tags=["Accounting - General Ledger"])
def ket_chuyen_cuoi_ky(
    ky_hieu: str = Body(..., embed=True), # Nhận kỳ như một trường trong body
    ngay_ket_chuyen: date = Body(default_factory=date.today, embed=True), # Nhận ngày kết chuyển, mặc định là hôm nay
    journaling_service: JournalingService = Depends(get_journaling_service)
):
    """
    Tự động tạo bút toán kết chuyển cuối kỳ (GL-04).
    """
    try:
        danh_sach_buoc_toan_moi = journaling_service.ket_chuyen_cuoi_ky(ky_hieu=ky_hieu, ngay_ket_chuyen=ngay_ket_chuyen)
        return danh_sach_buoc_toan_moi
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Có thể log lỗi ở đây
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi thực hiện kết chuyển.")

# --- API cho Khóa sổ (GL-05) ---
@router.post("/accounting-periods/{period_id}/lock", tags=["Accounting - Period Control"])
def khoa_ky(
    period_id: int,
    service: AccountingPeriodService = Depends(get_accounting_period_service)
):
    """
    Khóa sổ kế toán cho kỳ đã cho (GL-05).
    Yêu cầu: Phải có quyền Admin hoặc kế toán trưởng.
    """
    try:
        # service.khoa_ky(period_id) # Gọi phương thức trong service (chưa hoàn thiện)
        # Trả về thông tin kỳ đã khóa hoặc message thành công
        return {"message": f"Kỳ {period_id} đã được khóa thành công (mock)."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi khóa kỳ.")

@router.post("/accounting-periods/{period_id}/unlock", tags=["Accounting - Period Control"])
def mo_ky(
    period_id: int,
    reason: str = Body(..., embed=True), # Lý do mở lại
    service: AccountingPeriodService = Depends(get_accounting_period_service)
):
    """
    Mở sổ kế toán cho kỳ đã cho (GL-05).
    Yêu cầu: Phải có quyền Admin và lý do chính đáng.
    """
    try:
        # service.mo_ky(period_id, reason) # Gọi phương thức trong service (chưa hoàn thiện)
        # Trả về thông tin kỳ đã mở hoặc message thành công
        return {"message": f"Kỳ {period_id} đã được mở thành công (mock)."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi mở kỳ.")