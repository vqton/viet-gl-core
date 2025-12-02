# app/presentation/api/v1/accounting/reports.py
from datetime import date

from fastapi import APIRouter, Depends

from app.application.services.reports.cash_flow_service import CashFlowService
from app.application.services.reports.financial_position_service import (
    FinancialPositionService,
)
from app.domain.models.report import (
    BaoCaoLuuChuyenTienTe,
    BaoCaoTinhHinhTaiChinh,
)
from app.presentation.api.v1.accounting.dependencies import (
    get_cash_flow_service,
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
