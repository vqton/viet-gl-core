"""Test cases for PurchaseInvoice value object."""

from datetime import date
from decimal import Decimal
from src.domain.value_objects.purchase_invoice import PurchaseInvoice, PurchaseLineItem


def test_purchase_invoice_creation():
    """
    Test tạo hóa đơn mua hàng hợp lệ.

    Yêu cầu pháp lý:
    - Luật Quản lý Thuế: Hóa đơn phải có MST nhà cung cấp, ngày hóa đơn
    - Thông tư 78/2021/TT-BTC: Định dạng hóa đơn điện tử

    Expected:
        - Tạo PurchaseInvoice thành công
        - Tính toán giá trị hàng hóa chính xác
    """
    line_items = [
        PurchaseLineItem("SKU01", "Điện thoại", Decimal("10"), Decimal("8000000")),
        PurchaseLineItem("SKU02", "Phụ kiện", Decimal("50"), Decimal("100000")),
    ]

    invoice = PurchaseInvoice(
        invoice_number="PO-001",
        invoice_date=date(2026, 4, 15),
        supplier_tax_code="9876543210",
        supplier_name="Cty ABC",
        line_items=line_items,
    )

    # Kiểm tra giá trị hàng hóa
    expected_goods_value = (Decimal("10") * Decimal("8000000")) + (
        Decimal("50") * Decimal("100000")
    )
    assert invoice.goods_value == expected_goods_value
    assert invoice.goods_value == Decimal("85000000")


def test_purchase_invoice_with_freight_cost():
    """
    Test hóa đơn mua hàng có chi phí vận chuyển.

    Yêu cầu TT 99:
    - Hướng dẫn TK 156: Chi phí thu mua (vận chuyển) được tính vào giá trị hàng hóa

    Expected:
        - freight_cost được lưu trữ đúng
        - Thuế GTGT tính trên tổng (hàng hóa + vận chuyển)
    """
    invoice = PurchaseInvoice(
        invoice_number="PO-002",
        invoice_date=date(2026, 4, 16),
        supplier_tax_code="9876543210",
        supplier_name="Cty XYZ",
        line_items=[
            PurchaseLineItem("SKU01", "Máy tính", Decimal("5"), Decimal("15000000"))
        ],
        freight_cost=Decimal("2000000"),
    )

    assert invoice.freight_cost == Decimal("2000000")
    assert invoice.goods_value == Decimal("75000000")  # 5 * 15M
    assert invoice.vat_amount == (Decimal("75000000") + Decimal("2000000")) * Decimal(
        "0.1"
    )
    assert invoice.vat_amount == Decimal("7700000")


def test_purchase_invoice_vat_calculation():
    """
    Test tính toán thuế GTGT trên hóa đơn mua hàng.

    Yêu cầu pháp lý:
    - Thuế GTGT = (Giá trị hàng hóa + Chi phí thu mua) * Thuế suất

    Expected:
        - vat_amount được tính chính xác theo công thức
    """
    invoice = PurchaseInvoice(
        invoice_number="PO-003",
        invoice_date=date(2026, 4, 17),
        supplier_tax_code="9876543210",
        supplier_name="NCC DEF",
        line_items=[
            PurchaseLineItem("SKU01", "Hàng A", Decimal("100"), Decimal("100000"))
        ],
        freight_cost=Decimal("500000"),
        vat_rate=Decimal("0.08"),  # Thuế suất 8%
    )

    expected_vat = (Decimal("10000000") + Decimal("500000")) * Decimal("0.08")
    assert invoice.vat_amount == expected_vat
    assert invoice.vat_amount == Decimal("840000")


def test_empty_line_items():
    """
    Test hóa đơn không có dòng hàng.

    Yêu cầu nghiệp vụ:
    - Hóa đơn mua hàng phải có ít nhất một dòng hàng

    Expected:
        - goods_value = 0
        - vat_amount = freight_cost * vat_rate
    """
    invoice = PurchaseInvoice(
        invoice_number="PO-004",
        invoice_date=date(2026, 4, 18),
        supplier_tax_code="9876543210",
        supplier_name="NCC GHI",
        line_items=[],  # Không có dòng hàng
        freight_cost=Decimal("1000000"),
    )

    assert invoice.goods_value == Decimal("0")
    assert invoice.vat_amount == Decimal("1000000") * Decimal("0.1")
    assert invoice.vat_amount == Decimal("100000")


def test_invalid_supplier_data():
    """
    Test phát hiện thiếu thông tin nhà cung cấp.

    Mục đích:
        - Phát hiện module quản lý nhà cung cấp chưa được tích hợp đầy đủ
        - Cần validate MST và tên NCC ở application layer

    Expected:
        - Core logic vẫn chấp nhận dữ liệu (vì là value object)
        - Nhưng hệ thống thực tế cần validation bổ sung
    """
    # Hóa đơn có MST rỗng
    invoice = PurchaseInvoice(
        invoice_number="PO-005",
        invoice_date=date(2026, 4, 19),
        supplier_tax_code="",  # Thiếu MST
        supplier_name="",
        line_items=[
            PurchaseLineItem("SKU01", "Hàng mẫu", Decimal("1"), Decimal("1000000"))
        ],
    )

    # Core logic không validate → chấp nhận
    assert invoice.supplier_tax_code == ""
    assert invoice.supplier_name == ""

    # Ghi chú: Đây là điểm cần cải thiện → thêm validation ở application layer
    # để đảm bảo tuân thủ Luật Quản lý Thuế


def test_future_invoice_date():
    """
    Test hóa đơn có ngày trong tương lai.

    Yêu cầu pháp lý:
    - Ngày hóa đơn không được lớn hơn ngày hiện tại (theo Thông tư 78/2021/TT-BTC)

    Expected:
        - Core logic không validate ngày
        - Validation này phải được thực hiện ở application layer
    """
    future_date = date(2027, 1, 1)
    invoice = PurchaseInvoice(
        invoice_number="PO-006",
        invoice_date=future_date,
        supplier_tax_code="9876543210",
        supplier_name="NCC JKL",
        line_items=[
            PurchaseLineItem("SKU01", "Hàng mẫu", Decimal("1"), Decimal("1000000"))
        ],
    )

    assert invoice.invoice_date == future_date
    # Ghi chú: Validation ngày hóa đơn phải được thực hiện ở lớp ứng dụng


def test_zero_quantity_items():
    """
    Test dòng hàng có số lượng bằng 0.

    Yêu cầu nghiệp vụ:
    - Số lượng hàng hóa phải lớn hơn 0

    Expected:
        - Core logic chấp nhận (vì là value object)
        - Application layer cần validate
    """
    invoice = PurchaseInvoice(
        invoice_number="PO-007",
        invoice_date=date(2026, 4, 20),
        supplier_tax_code="9876543210",
        supplier_name="NCC MNO",
        line_items=[
            PurchaseLineItem("SKU01", "Hàng lỗi", Decimal("0"), Decimal("1000000"))
        ],
    )

    assert invoice.goods_value == Decimal("0")
    # Ghi chú: Cần validation số lượng > 0 ở application layer
