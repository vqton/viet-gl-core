"""
Test cases for Record Sales Use Case.

Yêu cầu pháp lý:
- Thông tư 99/2025/TT-BTC: 
  - Điều 19: Ghi nhận doanh thu tại thời điểm giao hàng
  - Điều 27: Phải theo dõi công nợ chi tiết theo từng khách hàng
  - Hướng dẫn TK 511: Hàng khuyến mãi phải ghi nhận doanh thu

Mục tiêu test:
- Xác minh hệ thống tạo bút toán bán hàng đúng
- Kiểm tra việc tạo công nợ chi tiết cho khách hàng
- Đảm bảo audit trail đầy đủ
"""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from src.application.dtos.sales_invoice_dto import SalesInvoiceDTO
from src.domain.value_objects.inventory_transaction import InventoryTransaction
from src.domain.value_objects.sales_invoice import SalesLineItem
from src.application.use_cases.record_sales_use_case import RecordSalesUseCase
from src.application.dtos.accounting_policy_dto import AccountingPolicyDTO, ValuationMethod
from src.infrastructure.repositories.in_memory_debt_repository import InMemoryDebtRepository


def test_import_record_sales_use_case():
    """Kiểm tra không có ImportError khi import RecordSalesUseCase."""
    assert RecordSalesUseCase is not None


def test_record_sales_use_case_initialization():
    """
    Test khởi tạo RecordSalesUseCase thành công.
    
    Yêu cầu kỹ thuật:
    - Use case phải nhận đủ 4 dependencies
    - Không được phép thiếu debt_repo (bắt buộc từ TT 99)
    """
    inventory_repo = Mock()
    journal_repo = Mock()
    policy_service = Mock()
    debt_repo = InMemoryDebtRepository()

    use_case = RecordSalesUseCase(
        inventory_repo=inventory_repo,
        journal_entry_repo=journal_repo,
        policy_service=policy_service,
        debt_repo=debt_repo
    )

    assert use_case.inventory_repo == inventory_repo
    assert use_case.journal_entry_repo == journal_repo
    assert use_case.policy_service == policy_service
    assert use_case.debt_repo == debt_repo


def test_record_sales_use_case_executes_successfully():
    """
    Test toàn bộ luồng ghi nhận bán hàng.
    
    Yêu cầu pháp lý:
    - Điều 19 TT 99: Ghi nhận doanh thu = giá trị hàng hóa
    - Điều 27 TT 99: Tạo công nợ chi tiết cho khách hàng
    - Hướng dẫn TK 156: Tính giá vốn theo phương pháp FIFO
    
    Scenario:
        - Bán 2 điện thoại @10M → Doanh thu = 20M
        - Giá vốn FIFO = 14M (2 * 7M)
        - Công nợ = 22M (20M + 2M GTGT)
    """
    inventory_repo = Mock()
    journal_repo = Mock()
    policy_service = Mock()
    debt_repo = InMemoryDebtRepository()

    # Cấu hình mock tồn kho
    inventory_repo.get_transactions_by_sku.return_value = [
        InventoryTransaction("SKU01", Decimal('5'), Decimal('7000000'), date(2026, 4, 1), "IN")
    ]
    
    # Cấu hình mock chính sách kế toán
    policy_service.get_current_policy.return_value = AccountingPolicyDTO(
        inventory_valuation_method=ValuationMethod.FIFO,
        effective_date="2026-01-01"
    )

    # Tạo DTO đầu vào
    dto = SalesInvoiceDTO(
        invoice_number="INV-001",
        invoice_date=date(2026, 4, 15),
        seller_tax_code="0123456789",
        buyer_name="Cty ABC",
        buyer_tax_code="9876543210",
        line_items=[SalesLineItem("SKU01", "Điện thoại", Decimal('2'), Decimal('10000000'))]
    )

    # Thực thi
    use_case = RecordSalesUseCase(
        inventory_repo=inventory_repo,
        journal_entry_repo=journal_repo,
        policy_service=policy_service,
        debt_repo=debt_repo
    )
    entries = use_case.execute(dto, created_by="NV001")

    # Kiểm tra kết quả
    assert len(entries) == 5
    assert entries[1].credit == Decimal('20000000')  # Doanh thu (TK 5111)
    assert entries[3].debit == Decimal('14000000')   # Giá vốn (TK 632)
    
    # Kiểm tra đã gọi save()
    assert journal_repo.save.call_count == 5
    
    # Kiểm tra công nợ đã được tạo (Tuân thủ Điều 27 TT 99)
    total_debt = debt_repo.get_total_balance(f"CUST-{dto.buyer_tax_code}")
    expected_total = Decimal('20000000') + (Decimal('20000000') * Decimal('0.1'))  # 20M + 2M GTGT
    assert total_debt == expected_total