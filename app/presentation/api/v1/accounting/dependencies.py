# app/presentation/api/v1/accounting/dependencies.py
"""
Dependency Injection (DI) container cho các service kế toán theo TT99/2025/TT-BTC.

🎯 Mục tiêu:
- Cung cấp các service instance cho API endpoints.
- Đảm bảo mỗi service được inject đúng repository interface (DIP).
- Dễ dàng mock trong test bằng cách override function này.
- Tách biệt logic khởi tạo khỏi logic nghiệp vụ (SRP).
"""
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from app.infrastructure.database import get_db

# Factories (nằm trong app/application/)
from app.application.factories.tai_khoan_service_factory import TaiKhoanServiceFactory
from app.application.factories.accounting_periods_service_factory import AccountingPeriodServiceFactory
from app.application.factories.report_service_factory import ReportServiceFactory


# ————————————————————————————————————————————————————————————————————————————————
# FACTORY DEPENDENCIES
# ————————————————————————————————————————————————————————————————————————————————

def get_tai_khoan_service_factory(
    db: Session = Depends(get_db)
) -> TaiKhoanServiceFactory:
    """
    [TT99-PL2] Cung cấp factory cho các service quản lý tài khoản kế toán.
    """
    from app.infrastructure.repositories.account_repository import AccountRepository
    from app.application.validators.tt99_account_validator import TT99TaiKhoanValidator

    repo = AccountRepository(db)
    validator = TT99TaiKhoanValidator()
    return TaiKhoanServiceFactory(repo=repo, validator=validator)


def get_period_service_factory(
    db: Session = Depends(get_db)
) -> AccountingPeriodServiceFactory:
    """
    [TT99-Đ25] Cung cấp factory cho các service quản lý kỳ kế toán.
    """
    from app.infrastructure.repositories.accounting_period_repository import AccountingPeriodRepository
    from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository

    period_repo = AccountingPeriodRepository(db)
    je_repo = JournalEntryRepository(db)
    return AccountingPeriodServiceFactory(period_repo=period_repo, je_repo=je_repo)


def get_report_service_factory(
    db: Session = Depends(get_db)
) -> ReportServiceFactory:
    """
    [TT99-PL4] Cung cấp factory cho các service tạo báo cáo tài chính.
    """
    from app.infrastructure.repositories.journal_entry_repository import JournalEntryRepository
    from app.infrastructure.repositories.account_repository import AccountRepository

    je_repo = JournalEntryRepository(db)
    acc_repo = AccountRepository(db)
    return ReportServiceFactory(je_repo=je_repo, acc_repo=acc_repo)


# ————————————————————————————————————————————————————————————————————————————————
# TÀI KHOẢN SERVICES
# ————————————————————————————————————————————————————————————————————————————————

def get_create_tai_khoan_service(
    factory: TaiKhoanServiceFactory = Depends(get_tai_khoan_service_factory)
):
    """
    [SRP] Service chỉ để tạo tài khoản kế toán.
    """
    return factory.create_create_service()


def get_query_tai_khoan_service(
    factory: TaiKhoanServiceFactory = Depends(get_tai_khoan_service_factory)
):
    """
    [SRP] Service chỉ để truy vấn tài khoản kế toán.
    """
    return factory.create_query_service()


def get_update_tai_khoan_service(
    factory: TaiKhoanServiceFactory = Depends(get_tai_khoan_service_factory)
):
    """
    [SRP] Service chỉ để cập nhật tài khoản kế toán.
    """
    return factory.create_update_service()


def get_delete_tai_khoan_service(
    factory: TaiKhoanServiceFactory = Depends(get_tai_khoan_service_factory)
):
    """
    [SRP] Service chỉ để xóa tài khoản kế toán.
    """
    return factory.create_delete_service()


# ————————————————————————————————————————————————————————————————————————————————
# KỲ KẾ TOÁN SERVICES
# ————————————————————————————————————————————————————————————————————————————————

def get_create_period_service(
    factory: AccountingPeriodServiceFactory = Depends(get_period_service_factory)
):
    """
    [SRP] Service chỉ để tạo kỳ kế toán.
    """
    return factory.create_create_service()


def get_lock_period_service(
    factory: AccountingPeriodServiceFactory = Depends(get_period_service_factory)
):
    """
    [SRP] Service chỉ để khóa kỳ kế toán.
    """
    return factory.create_lock_service()


def get_unlock_period_service(
    factory: AccountingPeriodServiceFactory = Depends(get_period_service_factory)
):
    """
    [SRP] Service chỉ để mở kỳ kế toán.
    """
    return factory.create_unlock_service()


def get_query_period_service(
    factory: AccountingPeriodServiceFactory = Depends(get_period_service_factory)
):
    """
    [SRP] Service chỉ để truy vấn kỳ kế toán.
    """
    return factory.create_query_service()


# ————————————————————————————————————————————————————————————————————————————————
# BÁO CÁO SERVICES
# ————————————————————————————————————————————————————————————————————————————————

def get_financial_position_service(
    factory: ReportServiceFactory = Depends(get_report_service_factory)
):
    """
    [TT99-PL4] Service tạo Báo cáo tình hình tài chính (B01-DN).
    """
    return factory.create_financial_position_service()


def get_performance_service(
    factory: ReportServiceFactory = Depends(get_report_service_factory)
):
    """
    [TT99-PL4] Service tạo Báo cáo kết quả HĐKD (B02-DN).
    """
    return factory.create_performance_service()


def get_cash_flow_service(
    factory: ReportServiceFactory = Depends(get_report_service_factory)
):
    """
    [TT99-PL4] Service tạo Báo cáo lưu chuyển tiền tệ (B03-DN).
    """
    return factory.create_cash_flow_service()


def get_disclosure_service(
    factory: ReportServiceFactory = Depends(get_report_service_factory)
):
    """
    [TT99-PL4] Service tạo Bản thuyết minh BCTC (B09-DN).
    """
    return factory.create_disclosure_service()