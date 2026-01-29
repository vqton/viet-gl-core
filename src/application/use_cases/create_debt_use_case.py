"""
Module: Create Debt Use Case

Tạo công nợ chi tiết theo Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Điều 27 TT 99: Phải theo dõi công nợ theo từng đối tượng
- Phải ghi rõ hạn thanh toán và loại chứng từ gốc

Trách nhiệm:
- Tạo bản ghi công nợ khi phát sinh nghiệp vụ mua/bán
- Đảm bảo dữ liệu đầy đủ để xuất báo cáo B01-DN
"""

from datetime import datetime
from src.application.interfaces.i_debt_repository import IDebtRepository
from src.application.dtos.debt_creation_dto import DebtCreationDTO


class CreateDebtUseCase:
    """
    Use case tạo công nợ mới.

    Attributes:
        debt_repo (IDebtRepository): Lưu trữ công nợ
    """

    def __init__(self, debt_repo: IDebtRepository):
        self.debt_repo = debt_repo

    def execute(self, dto: DebtCreationDTO) -> str:
        """
        Thực thi tạo công nợ.

        Args:
            dto (DebtCreationDTO): Dữ liệu công nợ

        Returns:
            str: ID của công nợ đã tạo

        Raises:
            ValueError: Nếu dữ liệu không hợp lệ
        """
        # Kiểm tra dữ liệu đầu vào
        if dto.amount <= 0:
            raise ValueError("Số tiền công nợ phải lớn hơn 0")

        if dto.due_date < dto.document_date if hasattr(dto, "document_date") else False:
            raise ValueError("Hạn thanh toán không được sớm hơn ngày chứng từ")

        # Tự động thêm metadata
        enriched_dto = DebtCreationDTO(
            party_id=dto.party_id,
            party_name=dto.party_name,
            party_tax_code=dto.party_tax_code,
            document_id=dto.document_id,
            document_type=dto.document_type,
            amount=dto.amount,
            due_date=dto.due_date,
            currency=dto.currency,
        )

        # Lưu công nợ
        debt_id = self.debt_repo.save(enriched_dto)
        return debt_id
