"""
Module: In-Memory Debt Repository

Implementation in-memory cho IDebtRepository.
Dùng cho test, demo, và phát triển ban đầu.
"""

from typing import List
from decimal import Decimal
from src.application.interfaces.i_debt_repository import IDebtRepository
from src.application.dtos.debt_creation_dto import DebtCreationDTO


class InMemoryDebtRepository(IDebtRepository):
    """
    Repository công nợ trong bộ nhớ.
    """

    def __init__(self):
        self._debts = []  # Danh sách công nợ (list of DebtCreationDTO)
        self._next_id = 1

    def save(self, dto: DebtCreationDTO) -> str:
        """
        Lưu công nợ mới.

        Args:
            dto (DebtCreationDTO): Dữ liệu công nợ

        Returns:
            str: ID duy nhất của công nợ
        """
        debt_id = f"DEBT-{self._next_id:06d}"
        self._next_id += 1

        # Lưu bản sao để tránh side effect
        saved_dto = DebtCreationDTO(
            party_id=dto.party_id,
            party_name=dto.party_name,
            party_tax_code=dto.party_tax_code,
            document_id=dto.document_id,
            document_type=dto.document_type,
            amount=dto.amount,
            due_date=dto.due_date,
            currency=dto.currency,
        )
        self._debts.append(saved_dto)
        return debt_id

    def find_by_party_id(self, party_id: str) -> List[DebtCreationDTO]:
        """
        Tìm tất cả công nợ theo mã đối tượng.

        Args:
            party_id (str): Mã khách hàng/NCC

        Returns:
            List[DebtCreationDTO]: Danh sách công nợ
        """
        return [debt for debt in self._debts if debt.party_id == party_id]

    def get_total_balance(self, party_id: str) -> Decimal:
        """
        Tính tổng số dư công nợ của đối tượng.

        Args:
            party_id (str): Mã khách hàng/NCC

        Returns:
            Decimal: Tổng số tiền còn phải thu/trả
        """
        debts = self.find_by_party_id(party_id)
        return sum(debt.amount for debt in debts)
