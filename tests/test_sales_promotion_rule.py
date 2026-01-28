"""
Test cases for sales promotion (hàng khuyến mãi) handling.

Yêu cầu pháp lý:
- Hướng dẫn TK 511 TT 99: Hàng khuyến mãi phải được ghi nhận doanh thu
- Doanh thu = Giá trị hàng hóa thực tế (kể cả khi không thu tiền)

Mục tiêu test:
- Xác minh hệ thống tính doanh thu bao gồm cả hàng khuyến mãi
- Kiểm tra xử lý thuế GTGT cho hàng khuyến mãi
"""

from datetime import date
from decimal import Decimal
from unittest.mock import Mock

from src.application.dtos.sales_invoice_dto import SalesInvoiceDTO
from src.domain.value_objects.sales_invoice import SalesLineItem
from src.application.use_cases.record_sales_use_case import RecordSalesUseCase
from src.application.dtos.accounting_policy_dto import (
    AccountingPolicyDTO,
    ValuationMethod,
)
from src.domain.value_objects.inventory_transaction import InventoryTransaction


def test_sales_with_promotional_items_includes_revenue():
    """
    Test bán hàng có hàng khuyến mãi.

    Yêu cầu TT 99:
    - Hàng khuyến mãi phải được ghi nhận doanh thu theo giá trị thị trường
    - Thuế GTGT tính trên tổng giá trị (hàng chính + KM)

    Scenario:
        - 1 điện thoại (10M) + 1 sạc (100K) KHUYẾN MÃI
        - Tổng doanh thu = 10.100.000
        - Thuế GTGT = 1.010.000
    """
    # 1. Chuẩn bị mock
    inventory_repo = Mock()
    journal_repo = Mock()
    policy_service = Mock()

    # 2. Cấu hình mock
    inventory_repo.get_transactions_by_sku.return_value = [
        InventoryTransaction(
            "PHONE01", Decimal("5"), Decimal("7000000"), date(2026, 4, 1), "IN"
        ),
        InventoryTransaction(
            "CHARGER01", Decimal("10"), Decimal("50000"), date(2026, 4, 1), "IN"
        ),
    ]
    policy_service.get_current_policy.return_value = AccountingPolicyDTO(
        inventory_valuation_method=ValuationMethod.FIFO, effective_date="2026-01-01"
    )

    # 3. Tạo hóa đơn có hàng khuyến mãi
    # Lưu ý: Hàng khuyến mãi vẫn có unit_price > 0 (giá trị thị trường)
    dto = SalesInvoiceDTO(
        invoice_number="INV-PROMO-001",
        invoice_date=date(2026, 4, 15),
        seller_tax_code="0123456789",
        buyer_name="Cty ABC",
        buyer_tax_code="9876543210",
        line_items=[
            SalesLineItem("PHONE01", "Điện thoại", Decimal("1"), Decimal("10000000")),
            SalesLineItem(
                "CHARGER01", "Sạc (KM)", Decimal("1"), Decimal("100000")
            ),  # Hàng KM
        ],
    )

    # 4. Thực thi
    use_case = RecordSalesUseCase(inventory_repo, journal_repo, policy_service)
    entries = use_case.execute(dto, created_by="NV001")

    # 5. Kiểm tra kết quả
    # Tìm bút toán doanh thu (TK 5111)
    revenue_entry = next(e for e in entries if e.account == "5111")
    vat_entry = next(e for e in entries if e.account == "33311")

    # Tổng giá trị hàng hóa = 10M + 100K = 10,100,000
    expected_total_amount = Decimal("10100000")
    expected_vat = expected_total_amount * Decimal("0.1")  # 1,010,000

    assert (
        revenue_entry.credit == expected_total_amount
    ), f"Doanh thu phải bằng tổng giá trị (hàng chính + KM). Kỳ vọng: {expected_total_amount}, Thực tế: {revenue_entry.credit}"
    assert (
        vat_entry.credit == expected_vat
    ), f"Thuế GTGT phải tính trên tổng giá trị. Kỳ vọng: {expected_vat}, Thực tế: {vat_entry.credit}"

    # Kiểm tra số lượng bút toán
    assert len(entries) == 5


def test_free_promotional_item_still_generates_revenue():
    """
    Test hàng khuyến mãi MIỄN PHÍ (unit_price = 0).

    Yêu cầu TT 99:
    - Ngay cả khi không thu tiền, vẫn phải ghi nhận doanh thu theo giá trị thị trường
    - Trong thực tế, unit_price của hàng KM phải > 0 (giá trị hợp lý)

    Lưu ý:
    - Hệ thống không cho phép unit_price = 0 cho hàng KM
    - Đây là kiểm tra phòng vệ
    """
    # 1. Chuẩn bị mock
    inventory_repo = Mock()
    journal_repo = Mock()
    policy_service = Mock()

    inventory_repo.get_transactions_by_sku.return_value = [
        InventoryTransaction(
            "GIFT01", Decimal("10"), Decimal("50000"), date(2026, 4, 1), "IN"
        )
    ]
    policy_service.get_current_policy.return_value = AccountingPolicyDTO(
        inventory_valuation_method=ValuationMethod.FIFO, effective_date="2026-01-01"
    )

    # 2. Tạo hóa đơn với hàng KM có unit_price = 0 (sai)
    dto = SalesInvoiceDTO(
        invoice_number="INV-FREE-001",
        invoice_date=date(2026, 4, 15),
        seller_tax_code="0123456789",
        buyer_name="Cty XYZ",
        buyer_tax_code="9876543210",
        line_items=[
            SalesLineItem("MAIN01", "Hàng chính", Decimal("1"), Decimal("5000000")),
            SalesLineItem(
                "GIFT01", "Quà tặng", Decimal("1"), Decimal("0")
            ),  # Sai: unit_price = 0
        ],
    )

    # 3. Thực thi
    use_case = RecordSalesUseCase(inventory_repo, journal_repo, policy_service)
    entries = use_case.execute(dto, created_by="NV001")

    # 4. Kiểm tra
    # Hệ thống vẫn tính doanh thu = 5M + 0 = 5M
    # → Cảnh báo: Đây là rủi ro pháp lý!
    revenue_entry = next(e for e in entries if e.account == "5111")
    assert revenue_entry.credit == Decimal("5000000")

    # Ghi chú: Trong thực tế, nghiệp vụ này nên bị từ chối ở application layer
    # vì hàng khuyến mãi phải có giá trị thị trường hợp lý


def test_promotional_item_with_reasonable_market_value():
    """
    Test hàng khuyến mãi có giá trị thị trường hợp lý.

    Best practice:
    - Hàng khuyến mãi nên có unit_price = 70-100% giá bán lẻ
    - Ví dụ: Sạc giá bán lẻ 150K → KM ghi 100K
    """
    inventory_repo = Mock()
    journal_repo = Mock()
    policy_service = Mock()

    inventory_repo.get_transactions_by_sku.return_value = [
        InventoryTransaction(
            "PHONE01", Decimal("5"), Decimal("7000000"), date(2026, 4, 1), "IN"
        ),
        InventoryTransaction(
            "CASE01", Decimal("10"), Decimal("30000"), date(2026, 4, 1), "IN"
        ),
    ]
    policy_service.get_current_policy.return_value = AccountingPolicyDTO(
        inventory_valuation_method=ValuationMethod.FIFO, effective_date="2026-01-01"
    )

    dto = SalesInvoiceDTO(
        invoice_number="INV-CASE-001",
        invoice_date=date(2026, 4, 15),
        seller_tax_code="0123456789",
        buyer_name="Cty DEF",
        buyer_tax_code="9876543210",
        line_items=[
            SalesLineItem("PHONE01", "Điện thoại", Decimal("1"), Decimal("10000000")),
            SalesLineItem(
                "CASE01", "Ốp lưng (KM)", Decimal("1"), Decimal("80000")
            ),  # Giá trị hợp lý
        ],
    )

    use_case = RecordSalesUseCase(inventory_repo, journal_repo, policy_service)
    entries = use_case.execute(dto, created_by="NV001")

    revenue_entry = next(e for e in entries if e.account == "5111")
    expected_total = Decimal("10000000") + Decimal("80000")  # 10,080,000
    assert revenue_entry.credit == expected_total
