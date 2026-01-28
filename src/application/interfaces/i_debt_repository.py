"""
Module: Debt Repository Interface

Định nghĩa hợp đồng lưu trữ công nợ chi tiết.
"""

from typing import List
from decimal import Decimal
from src.application.dtos.debt_creation_dto import DebtCreationDTO

class IDebtRepository:
    """
    Interface quản lý công nợ chi tiết.
    
    Methods:
        save(dto: DebtCreationDTO) -> str:
            Lưu công nợ mới, trả về ID.
            
        find_by_party_id(party_id: str) -> List[DebtCreationDTO]:
            Tìm công nợ theo mã đối tượng.
            
        get_total_balance(party_id: str) -> Decimal:
            Lấy tổng số dư công nợ của đối tượng.
    """
    
    def save(self, dto: DebtCreationDTO) -> str:
        """Lưu công nợ mới."""
        raise NotImplementedError("Phải được triển khai trong infrastructure layer")
    
    def find_by_party_id(self, party_id: str) -> List[DebtCreationDTO]:
        """Tìm công nợ theo đối tượng."""
        raise NotImplementedError("Phải được triển khai trong infrastructure layer")
    
    def get_total_balance(self, party_id: str) -> Decimal:
        """Lấy tổng số dư công nợ."""
        raise NotImplementedError("Phải được triển khai trong infrastructure layer")