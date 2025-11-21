# File: app/presentation/api/v1/accounting.py

from fastapi import APIRouter, Depends, HTTPException, Body,Query
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional

from app.application.services.tai_khoan_service import TaiKhoanService
from app.application.services.journaling_service import JournalingService
from app.application.services.reporting_service import ReportingService
from app.application.services.accounting_period_service import AccountingPeriodService

from app.domain.models.account import TaiKhoan as TaiKhoanDomain
from app.domain.models.journal_entry import JournalEntry as JournalEntryDomain
from app.domain.models.report import (
    BaoCaoTinhHinhTaiChinh,
    BaoCaoKetQuaHDKD,
    BaoCaoLuuChuyenTienTe,
    BaoCaoThuyetMinh,
)
from app.domain.models.accounting_period import KyKeToan as KyKeToanDomain

from app.infrastructure.repositories.account_repository import AccountRepository
from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
from app.infrastructure.repositories.accounting_period_repository import AccountingPeriodRepository
from app.infrastructure.database import get_db

router = APIRouter(prefix="/accounting", tags=["Accounting - Kế toán"])

# --- Dependencies ---
def get_tai_khoan_service(db: Session = Depends(get_db)) -> TaiKhoanService:
    repository = AccountRepository(db_session=db)
    return TaiKhoanService(repository=repository)

def get_journaling_service(db: Session = Depends(get_db)) -> JournalingService:
    je_repo = JournalEntryRepository(db_session=db)
    acc_repo = AccountRepository(db_session=db)
    ap_repo = AccountingPeriodRepository(db_session=db)
    ap_service = AccountingPeriodService(repository=ap_repo, journal_entry_repo=je_repo)
    return JournalingService(
        repository=je_repo,
        account_repository=acc_repo,
        accounting_period_service=ap_service # Truyền AP Service vào JS
    )

def get_reporting_service(db: Session = Depends(get_db)) -> ReportingService:
    je_repo = JournalEntryRepository(db_session=db)
    acc_repo = AccountRepository(db_session=db)
    # Có thể cần thêm AccountingPeriodService hoặc AccountTypeService nếu RPT cần
    return ReportingService(journal_entry_repo=je_repo, account_repo=acc_repo)

def get_accounting_period_service(db: Session = Depends(get_db)) -> AccountingPeriodService:
    je_repo = JournalEntryRepository(db_session=db)
    ap_repo = AccountingPeriodRepository(db_session=db)
    return AccountingPeriodService(repository=ap_repo, journal_entry_repo=je_repo)

# --- API cho Danh mục Tài khoản (MST-03) ---
@router.post("/accounts/", response_model=TaiKhoanDomain, tags=["Accounting - Master Data"])
def tao_tai_khoan(tai_khoan: TaiKhoanDomain, service: TaiKhoanService = Depends(get_tai_khoan_service)):
    """
    Tạo mới một tài khoản kế toán (MST-03).
    """
    try:
        tai_khoan_moi = service.tao_tai_khoan(tai_khoan)
        return tai_khoan_moi
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi tạo tài khoản.")

@router.get("/accounts/{so_tai_khoan}", response_model=Optional[TaiKhoanDomain], tags=["Accounting - Master Data"])
def lay_tai_khoan_theo_so(so_tai_khoan: str, service: TaiKhoanService = Depends(get_tai_khoan_service)):
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

# --- API cho Bút toán kế toán (GL-01), có kiểm tra khóa sổ (GL-05) ---
@router.post("/journal-entries/", response_model=JournalEntryDomain, tags=["Accounting - General Ledger"])
def tao_phieu_ke_toan(journal_entry: JournalEntryDomain, service: JournalingService = Depends(get_journaling_service)):
    """
    Tạo mới một bút toán kế toán (GL-01).
    - Kiểm tra khóa sổ trước khi tạo.
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

@router.put("/journal-entries/{id}", response_model=Optional[JournalEntryDomain], tags=["Accounting - General Ledger"])
def cap_nhat_phieu_ke_toan(id: int, journal_entry: JournalEntryDomain, service: JournalingService = Depends(get_journaling_service)):
    """
    Cập nhật một bút toán kế toán (GL-01).
    - Kiểm tra khóa sổ trước khi cập nhật.
    """
    try:
        phieu_cap_nhat = service.cap_nhat_phieu_ke_toan(id, journal_entry)
        if not phieu_cap_nhat:
            raise HTTPException(status_code=404, detail="Bút toán không tồn tại.")
        return phieu_cap_nhat
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi cập nhật bút toán.")

@router.delete("/journal-entries/{id}", tags=["Accounting - General Ledger"])
def xoa_phieu_ke_toan(id: int, service: JournalingService = Depends(get_journaling_service)):
    """
    Xóa một bút toán kế toán (GL-01).
    - Kiểm tra khóa sổ trước khi xóa.
    """
    try:
        success = service.xoa_phieu_ke_toan(id)
        if not success:
            raise HTTPException(status_code=404, detail="Bút toán không tồn tại.")
        return {"message": f"Bút toán {id} đã được xóa thành công."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi xóa bút toán.")

# --- API cho Kết chuyển cuối kỳ (GL-04) ---
@router.post("/journal-entries/ket-chuyen-cuoi-ky", response_model=List[JournalEntryDomain], tags=["Accounting - General Ledger"])
def ket_chuyen_cuoi_ky(
    ky_hieu: str = Body(..., embed=True), # Nhận kỳ từ body
    ngay_ket_chuyen: date = Body(default_factory=date.today, embed=True), # Nhận ngày, mặc định là hôm nay
    service: JournalingService = Depends(get_journaling_service)
):
    """
    Tự động tạo bút toán kết chuyển cuối kỳ (GL-04).
    """
    try:
        danh_sach_buoc_toan_moi = service.ket_chuyen_cuoi_ky(ky_hieu=ky_hieu, ngay_ket_chuyen=ngay_ket_chuyen)
        return danh_sach_buoc_toan_moi
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi thực hiện kết chuyển.")

# --- API cho Báo cáo tài chính (GL-RPT) ---
@router.get("/reports/b01-dn", response_model=BaoCaoTinhHinhTaiChinh, tags=["Accounting - Reports"])
def lay_bao_cao_tinh_hinh_tai_chinh(
    ky_hieu: str = Query(default="Năm 2025", description="Ký hiệu kỳ kế toán (ví dụ: Q1-2025, Năm 2025)"),
    ngay_lap: date = Query(default_factory=date.today, description="Ngày lập báo cáo"),
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Lấy Báo cáo tình hình tài chính (B01-DN) theo TT99/2025/TT-BTC Phụ lục III.
    """
    return service.lay_bao_cao_tinh_hinh_tai_chinh(ky_hieu=ky_hieu, ngay_lap=ngay_lap)

@router.get("/reports/b02-dn", response_model=BaoCaoKetQuaHDKD, tags=["Accounting - Reports"])
def lay_bao_cao_ket_qua_hdkd(
    ky_hieu: str = Query(default="Năm 2025", description="Ký hiệu kỳ kế toán"),
    ngay_lap: date = Query(default_factory=date.today, description="Ngày lập báo cáo"),
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Lấy Báo cáo kết quả hoạt động kinh doanh (B02-DN) theo TT99/2025/TT-BTC Phụ lục III.
    """
    return service.lay_bao_cao_ket_qua_hdkd(ky_hieu=ky_hieu, ngay_lap=ngay_lap)

@router.get("/reports/b03-dn", response_model=BaoCaoLuuChuyenTienTe, tags=["Accounting - Reports"])
def lay_bao_cao_luu_chuyen_tien_te(
    ky_hieu: str = Query(default="Năm 2025", description="Ký hiệu kỳ kế toán"),
    ngay_lap: date = Query(default_factory=date.today, description="Ngày lập báo cáo"),
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Lấy Báo cáo lưu chuyển tiền tệ (B03-DN) theo TT99/2025/TT-BTC Phụ lục III.
    """
    return service.lay_bao_cao_luu_chuyen_tien_te(ky_hieu=ky_hieu, ngay_lap=ngay_lap)

@router.get("/reports/b09-dn", response_model=BaoCaoThuyetMinh, tags=["Accounting - Reports"])
def lay_bao_cao_thuyet_minh(
    ky_hieu: str = Query(default="Năm 2025", description="Ký hiệu kỳ kế toán"),
    ngay_lap: date = Query(default_factory=date.today, description="Ngày lập báo cáo"),
    service: ReportingService = Depends(get_reporting_service)
):
    """
    Lấy Bản thuyết minh Báo cáo tài chính (B09-DN) theo TT99/2025/TT-BTC Phụ lục III.
    """
    return service.lay_bao_cao_thuyet_minh(ky_hieu=ky_hieu, ngay_lap=ngay_lap)

# --- API cho Kỳ kế toán & Khóa sổ (GL-05) ---
@router.post("/accounting-periods/", response_model=KyKeToanDomain, tags=["Accounting - Period Control"])
def tao_ky_ke_toan(ky: KyKeToanDomain, service: AccountingPeriodService = Depends(get_accounting_period_service)):
    """
    Tạo mới một kỳ kế toán.
    """
    try:
        ky_moi = service.tao_ky_ke_toan(ky)
        return ky_moi
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi tạo kỳ kế toán.")

@router.get("/accounting-periods/{id}", response_model=Optional[KyKeToanDomain], tags=["Accounting - Period Control"])
def lay_ky_ke_toan_theo_id(id: int, service: AccountingPeriodService = Depends(get_accounting_period_service)):
    """
    Lấy thông tin kỳ kế toán theo ID.
    """
    ky = service.lay_ky_ke_toan_theo_id(id)
    if not ky:
        raise HTTPException(status_code=404, detail="Kỳ kế toán không tồn tại.")
    return ky

@router.get("/accounting-periods/", response_model=List[KyKeToanDomain], tags=["Accounting - Period Control"])
def lay_danh_sach_ky_ke_toan(service: AccountingPeriodService = Depends(get_accounting_period_service)):
    """
    Lấy danh sách tất cả kỳ kế toán.
    """
    danh_sach = service.lay_danh_sach_ky_ke_toan()
    return danh_sach

@router.post("/accounting-periods/{id}/lock", tags=["Accounting - Period Control"])
def khoa_ky(
    id: int,
    nguoi_thuc_hien: str = Body(default="System", embed=True), # Nhận người thực hiện từ body (tùy chọn)
    service: AccountingPeriodService = Depends(get_accounting_period_service)
):
    """
    Khóa sổ kế toán cho kỳ đã cho (GL-05).
    Yêu cầu: Phải có quyền Admin hoặc kế toán trưởng.
    """
    try:
        success = service.khoa_ky(id, nguoi_thuc_hien=nguoi_thuc_hien)
        if success:
            return {"message": f"Kỳ {id} đã được khóa thành công."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi khóa kỳ.")

@router.post("/accounting-periods/{id}/unlock", tags=["Accounting - Period Control"])
def mo_ky(
    id: int,
    reason: str = Body(..., embed=True), # Lý do mở lại (bắt buộc)
    nguoi_thuc_hien: str = Body(default="System", embed=True), # Nhận người thực hiện từ body (tùy chọn)
    service: AccountingPeriodService = Depends(get_accounting_period_service)
):
    """
    Mở sổ kế toán cho kỳ đã cho (GL-05).
    Yêu cầu: Phải có quyền Admin và lý do chính đáng.
    """
    try:
        success = service.mo_ky(id, ly_do=reason, nguoi_thuc_hien=nguoi_thuc_hien)
        if success:
            return {"message": f"Kỳ {id} đã được mở thành công."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Lỗi hệ thống khi mở kỳ.")

# (Có thể thêm các endpoint khác như GET /accounting-periods/{id}/status để kiểm tra trạng thái)

# ... (Các endpoint khác nếu có)