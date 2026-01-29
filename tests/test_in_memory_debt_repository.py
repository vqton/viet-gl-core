"""
Test cases for InMemoryDebtRepository.
"""

from datetime import date
from decimal import Decimal
from src.application.dtos.debt_creation_dto import DebtCreationDTO
from src.infrastructure.repositories.in_memory_debt_repository import (
    InMemoryDebtRepository,
)


def test_save_debt():
    """Test lưu công nợ mới."""
    repo = InMemoryDebtRepository()

    dto = DebtCreationDTO(
        party_id="CUST-9876543210",
        party_name="Cty ABC",
        party_tax_code="9876543210",
        document_id="INV-001",
        document_type="SALES",
        amount=Decimal("11000000"),
        due_date=date(2026, 5, 15),
    )

    debt_id = repo.save(dto)
    assert debt_id.startswith("DEBT-")
    assert len(repo._debts) == 1


def test_find_by_party_id():
    """Test tìm công nợ theo đối tượng."""
    repo = InMemoryDebtRepository()

    # Lưu 2 công nợ cho cùng 1 KH
    dto1 = DebtCreationDTO(
        party_id="CUST-9876543210",
        party_name="Cty ABC",
        party_tax_code="9876543210",
        document_id="INV-001",
        document_type="SALES",
        amount=Decimal("10000000"),
        due_date=date(2026, 5, 15),
    )
    dto2 = DebtCreationDTO(
        party_id="CUST-9876543210",
        party_name="Cty ABC",
        party_tax_code="9876543210",
        document_id="INV-002",
        document_type="SALES",
        amount=Decimal("5000000"),
        due_date=date(2026, 5, 20),
    )

    repo.save(dto1)
    repo.save(dto2)

    results = repo.find_by_party_id("CUST-9876543210")
    assert len(results) == 2
    assert results[0].amount == Decimal("10000000")
    assert results[1].amount == Decimal("5000000")


def test_get_total_balance():
    """Test tính tổng số dư công nợ."""
    repo = InMemoryDebtRepository()

    dto1 = DebtCreationDTO(
        party_id="CUST-9876543210",
        party_name="Cty ABC",
        party_tax_code="9876543210",
        document_id="INV-001",
        document_type="SALES",
        amount=Decimal("10000000"),
        due_date=date(2026, 5, 15),
    )
    dto2 = DebtCreationDTO(
        party_id="CUST-9876543210",
        party_name="Cty ABC",
        party_tax_code="9876543210",
        document_id="INV-002",
        document_type="SALES",
        amount=Decimal("5000000"),
        due_date=date(2026, 5, 20),
    )

    repo.save(dto1)
    repo.save(dto2)

    total = repo.get_total_balance("CUST-9876543210")
    assert total == Decimal("15000000")
