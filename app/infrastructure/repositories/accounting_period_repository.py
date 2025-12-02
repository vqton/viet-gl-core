# File: app/infrastructure/repositories/accounting_period_repository.py

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.models.accounting_period import KyKeToan as KyKeToanDomain
from app.infrastructure.models.sql_accounting_period import SQLAccountingPeriod


class AccountingPeriodRepository:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def add(self, ky_ke_toan_domain: KyKeToanDomain) -> KyKeToanDomain:
        """
        Thêm một kỳ kế toán mới vào cơ sở dữ liệu.
        """
        sql_ky = SQLAccountingPeriod(
            ten_ky=ky_ke_toan_domain.ten_ky,
            ngay_bat_dau=ky_ke_toan_domain.ngay_bat_dau,
            ngay_ket_thuc=ky_ke_toan_domain.ngay_ket_thuc,
            trang_thai=ky_ke_toan_domain.trang_thai,
            ghi_chu=ky_ke_toan_domain.ghi_chu,
        )
        self.db_session.add(sql_ky)
        self.db_session.commit()
        self.db_session.refresh(sql_ky)
        return KyKeToanDomain(
            id=sql_ky.id,
            ten_ky=sql_ky.ten_ky,
            ngay_bat_dau=sql_ky.ngay_bat_dau,
            ngay_ket_thuc=sql_ky.ngay_ket_thuc,
            trang_thai=sql_ky.trang_thai,
            ghi_chu=sql_ky.ghi_chu,
        )

    def get_by_id(self, id: int) -> Optional[KyKeToanDomain]:
        """
        Lấy thông tin kỳ kế toán theo ID.
        """
        sql_ky = (
            self.db_session.query(SQLAccountingPeriod)
            .filter(SQLAccountingPeriod.id == id)
            .first()
        )
        if not sql_ky:
            return None
        return KyKeToanDomain(
            id=sql_ky.id,
            ten_ky=sql_ky.ten_ky,
            ngay_bat_dau=sql_ky.ngay_bat_dau,
            ngay_ket_thuc=sql_ky.ngay_ket_thuc,
            trang_thai=sql_ky.trang_thai,
            ghi_chu=sql_ky.ghi_chu,
        )

    def get_by_ten_ky(self, ten_ky: str) -> Optional[KyKeToanDomain]:
        """
        Lấy thông tin kỳ kế toán theo tên kỳ.
        """
        sql_ky = (
            self.db_session.query(SQLAccountingPeriod)
            .filter(SQLAccountingPeriod.ten_ky == ten_ky)
            .first()
        )
        if not sql_ky:
            return None
        return KyKeToanDomain(
            id=sql_ky.id,
            ten_ky=sql_ky.ten_ky,
            ngay_bat_dau=sql_ky.ngay_bat_dau,
            ngay_ket_thuc=sql_ky.ngay_ket_thuc,
            trang_thai=sql_ky.trang_thai,
            ghi_chu=sql_ky.ghi_chu,
        )

    def update_trang_thai(
        self, id: int, trang_thai_moi: str
    ) -> Optional[KyKeToanDomain]:
        """
        Cập nhật trạng thái của kỳ kế toán.
        """
        sql_ky = (
            self.db_session.query(SQLAccountingPeriod)
            .filter(SQLAccountingPeriod.id == id)
            .first()
        )
        if not sql_ky:
            return None
        sql_ky.trang_thai = trang_thai_moi
        self.db_session.commit()
        self.db_session.refresh(sql_ky)
        return KyKeToanDomain(
            id=sql_ky.id,
            ten_ky=sql_ky.ten_ky,
            ngay_bat_dau=sql_ky.ngay_bat_dau,
            ngay_ket_thuc=sql_ky.ngay_ket_thuc,
            trang_thai=sql_ky.trang_thai,
            ghi_chu=sql_ky.ghi_chu,
        )

    def get_all(self) -> List[KyKeToanDomain]:
        """
        Lấy danh sách tất cả kỳ kế toán.
        """
        sql_kys = self.db_session.query(SQLAccountingPeriod).all()
        return [
            KyKeToanDomain(
                id=ky.id,
                ten_ky=ky.ten_ky,
                ngay_bat_dau=ky.ngay_bat_dau,
                ngay_ket_thuc=ky.ngay_ket_thuc,
                trang_thai=ky.trang_thai,
                ghi_chu=ky.ghi_chu,
            )
            for ky in sql_kys
        ]

    # (Có thể thêm các phương thức khác như update, delete, find_by_condition nếu cần)
