"""Test import RecordSalesUseCase không lỗi."""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from src.application.dtos.accounting_policy_dto import AccountingPolicyDTO
from src.application.dtos.sales_invoice_dto import SalesInvoiceDTO
from src.domain.rules.inventory_valuation_strategy import ValuationMethod
from src.domain.value_objects.inventory_transaction import InventoryTransaction
from src.domain.value_objects.sales_invoice import SalesLineItem
from src.application.use_cases.record_sales_use_case import RecordSalesUseCase


def test_import_record_sales_use_case():
    """Kiểm tra không có ImportError."""
    from src.application.use_cases.record_sales_use_case import RecordSalesUseCase
    assert RecordSalesUseCase is not None
    
def test_record_sales_use_case_initialization():
    """Kiểm tra khởi tạo Use Case thành công."""
    # Mock dependencies
    inventory_repo = Mock()
    journal_repo = Mock()
    policy_service = Mock()
    
    # Khởi tạo
    use_case = RecordSalesUseCase(inventory_repo, journal_repo, policy_service)
    
    # Kiểm tra
    assert use_case.inventory_repo == inventory_repo
    assert use_case.journal_entry_repo == journal_repo
    assert use_case.policy_service == policy_service
    
def test_record_sales_use_case_executes_successfully():
    """Test toàn bộ luồng ghi nhận bán hàng."""
    # 1. Chuẩn bị mock
    inventory_repo = Mock()
    journal_repo = Mock()
    policy_service = Mock()
    
    # 2. Cấu hình mock trả về dữ liệu mẫu
    inventory_repo.get_transactions_by_sku.return_value = [
        InventoryTransaction("SKU01", Decimal('5'), Decimal('7000000'), date(2026, 4, 1), "IN")
    ]
    policy_service.get_current_policy.return_value = AccountingPolicyDTO(
        inventory_valuation_method=ValuationMethod.FIFO,
        effective_date="2026-01-01"
    )
    
    # 3. Tạo DTO đầu vào
    dto = SalesInvoiceDTO(
        invoice_number="INV-001",
        invoice_date=date(2026, 4, 15),
        seller_tax_code="0123456789",
        buyer_name="Cty ABC",
        buyer_tax_code="9876543210",
        line_items=[SalesLineItem("SKU01", "Điện thoại", Decimal('2'), Decimal('10000000'))]
    )
    
    # 4. Thực thi
    use_case = RecordSalesUseCase(inventory_repo, journal_repo, policy_service)
    entries = use_case.execute(dto, created_by="NV001")
    
    # 5. Kiểm tra kết quả
    assert len(entries) == 5
    assert entries[1].credit == Decimal('20000000')  # Doanh thu
    assert entries[3].debit == Decimal('14000000')   # Giá vốn
    
    # 6. Kiểm tra đã gọi save()
    assert journal_repo.save.call_count == 5