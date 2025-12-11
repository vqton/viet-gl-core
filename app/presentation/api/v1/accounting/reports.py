# app/presentation/api/v1/accounting/reports.py
from datetime import date

from fastapi import APIRouter, Depends
from fastapi.temp_pydantic_v1_params import Query

from app.application.services.reports.cash_flow_service import CashFlowService
from app.application.services.reports.disclosure_service import (
    DisclosureService,
)
from app.application.services.reports.financial_position_service import (
    FinancialPositionService,
)
from app.domain.models.report import (
    BaoCaoLuuChuyenTienTe,
    BaoCaoThuyetMinh,
    BaoCaoTinhHinhTaiChinh,
)
from app.presentation.api.v1.accounting.dependencies import (
    get_cash_flow_service,
    get_disclosure_service,
    get_financial_position_service,
)

router = APIRouter()


@router.get(
    "/reports/financial-position", response_model=BaoCaoTinhHinhTaiChinh
)
def get_financial_position(
    ky_hieu: str,
    ngay_lap: date,
    ngay_ket_thuc: date,
    service: FinancialPositionService = Depends(
        get_financial_position_service
    ),
):
    return service.lay_bao_cao(ky_hieu, ngay_lap, ngay_ket_thuc)


@router.get("/reports/cash-flow", response_model=BaoCaoLuuChuyenTienTe)
def get_cash_flow(
    ky_hieu: str,
    ngay_lap: date,
    ngay_bat_dau: date,
    ngay_ket_thuc: date,
    service: CashFlowService = Depends(get_cash_flow_service),
):
    return service.lay_bao_cao(ky_hieu, ngay_lap, ngay_bat_dau, ngay_ket_thuc)


@router.get("/reports/disclosure", response_model=BaoCaoThuyetMinh)
def lay_thuyet_minh(
    ky_hieu: str,
    ngay_lap: date = date.today(),
    ngay_bat_dau: date = Query(..., description="Ngày bắt đầu kỳ"),
    ngay_ket_thuc: date = Query(..., description="Ngày kết thúc kỳ"),
    service: DisclosureService = Depends(get_disclosure_service),
):
    """
    [TT99-PL4] Lấy Bản thuyết minh BCTC (B09-DN).
    """
    return service.lay_bao_cao(ky_hieu, ngay_lap, ngay_bat_dau, ngay_ket_thuc)
