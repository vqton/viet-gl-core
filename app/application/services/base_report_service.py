# app/application/services/base_report_service.py
from abc import ABC

from app.application.interfaces.reporting_repository import ReportingRepository


class BaseReportService(ABC):
    """
    Lớp cơ sở cho các service báo cáo.
    """

    def __init__(self, repo: ReportingRepository):
        self.repo = repo
