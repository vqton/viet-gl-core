"""
Test cases for inventory valuation rules.

Yêu cầu pháp lý:
- Thông tư 99/2025/TT-BTC: Hướng dẫn TK 156 về 3 phương pháp tính giá vốn
- Phải kiểm thử đầy đủ từng phương pháp để đảm bảo tuân thủ pháp lý

Mục tiêu test:
- Xác minh tính toán giá vốn chính xác theo FIFO, bình quân, đích danh
- Kiểm tra xử lý lỗi khi tồn kho không đủ hoặc dữ liệu không hợp lệ
"""

import pytest
from datetime import date
from decimal import Decimal
from src.domain.value_objects.inventory_transaction import InventoryTransaction
from src.domain.rules.inventory_valuation_rules import (
    calculate_cogs_fifo,
    calculate_cogs_weighted_average,
    calculate_cogs_specific_identification,
)


# Dữ liệu test dùng chung
@pytest.fixture
def inventory_layers():
    return [
        InventoryTransaction(
            "SKU01", Decimal("5"), Decimal("7000000"), date(2026, 4, 1), "IN"
        ),
        InventoryTransaction(
            "SKU01", Decimal("3"), Decimal("7500000"), date(2026, 4, 10), "IN"
        ),
    ]


@pytest.fixture
def lot_based_layers():
    return [
        InventoryTransaction(
            "CAR01",
            Decimal("1"),
            Decimal("1000000000"),
            date(2026, 1, 1),
            "IN",
            "LOT-A",
        ),
        InventoryTransaction(
            "CAR01",
            Decimal("1"),
            Decimal("1050000000"),
            date(2026, 2, 1),
            "IN",
            "LOT-B",
        ),
    ]


# ──────────────── TEST FIFO ────────────────


def test_fifo_calculation(inventory_layers):
    """
    Test tính giá vốn theo FIFO.

    Yêu cầu TT 99: Giá vốn phải phản ánh giá thực tế nhập trước.

    Expected:
        - 6 đơn vị = (5 * 7M) + (1 * 7.5M) = 42.5M
    """
    cogs = calculate_cogs_fifo(inventory_layers, Decimal("6"))
    assert cogs == Decimal("42500000")


def test_fifo_insufficient_inventory(inventory_layers):
    """
    Test lỗi khi tồn kho không đủ cho FIFO.
    """
    with pytest.raises(ValueError, match="Tồn kho không đủ"):
        calculate_cogs_fifo(inventory_layers, Decimal("10"))


def test_fifo_zero_quantity():
    """
    Test lỗi khi số lượng bán <= 0.
    """
    layers = [
        InventoryTransaction(
            "SKU01", Decimal("1"), Decimal("1000000"), date.today(), "IN"
        )
    ]
    with pytest.raises(ValueError, match="Số lượng bán phải lớn hơn 0"):
        calculate_cogs_fifo(layers, Decimal("0"))


# ──────────────── TEST BÌNH QUÂN ────────────────


def test_weighted_average_calculation(inventory_layers):
    """
    Test tính giá vốn theo bình quân gia quyền.

    Yêu cầu TT 99: Giá bình quân = Tổng giá trị / Tổng số lượng.

    Expected:
        - Tổng giá trị = 5*7M + 3*7.5M = 57.5M
        - Tổng số lượng = 8
        - Giá bình quân = 57.5M / 8 = 7,187,500
        - Giá vốn 6 đơn vị = 43,125,000 → làm tròn = 43,125,000
    """
    cogs = calculate_cogs_weighted_average(inventory_layers, Decimal("6"))
    expected = (Decimal("57500000") / Decimal("8")) * Decimal("6")
    expected_rounded = expected.quantize(Decimal("1"))
    assert cogs == expected_rounded


def test_weighted_average_no_inventory():
    """
    Test lỗi khi không có tồn kho cho bình quân.
    """
    empty_layers = []
    with pytest.raises(ValueError, match="Không có tồn kho"):
        calculate_cogs_weighted_average(empty_layers, Decimal("1"))


# ──────────────── TEST ĐÍCH DANH ────────────────


def test_specific_identification_valid(lot_based_layers):
    """
    Test tính giá vốn theo thực tế đích danh.

    Yêu cầu TT 99: Phải theo dõi theo lô hàng cụ thể.

    Expected:
        - Chọn LOT-B → giá vốn = 1,050,000,000
    """
    cogs = calculate_cogs_specific_identification(
        lot_based_layers, Decimal("1"), ["LOT-B"]
    )
    assert cogs == Decimal("1050000000")


def test_specific_identification_quantity_mismatch(lot_based_layers):
    """
    Test lỗi khi số lượng lô hàng không khớp với số lượng bán.
    """
    with pytest.raises(ValueError, match="Số lượng lô hàng .* không khớp"):
        calculate_cogs_specific_identification(
            lot_based_layers,
            Decimal("2"),  # Muốn bán 2 xe
            ["LOT-B"],  # Nhưng chỉ chọn 1 lô
        )


def test_specific_identification_invalid_lot(lot_based_layers):
    """
    Test lỗi khi lô hàng không tồn tại.
    """
    with pytest.raises(ValueError, match="Không tìm thấy lô hàng"):
        calculate_cogs_specific_identification(
            lot_based_layers, Decimal("1"), ["LOT-X"]
        )


def test_specific_identification_empty_lot_list():
    """
    Test lỗi khi không cung cấp danh sách lô hàng.
    """
    layers = [
        InventoryTransaction(
            "SKU01", Decimal("1"), Decimal("1000000"), date.today(), "IN"
        )
    ]
    with pytest.raises(ValueError, match="Phải cung cấp danh sách lô hàng"):
        calculate_cogs_specific_identification(layers, Decimal("1"), [])


# ──────────────── TEST LÀM TRÒN ────────────────


def test_rounding_behavior():
    """
    Test làm tròn theo chuẩn kế toán Việt Nam (ROUND_HALF_UP).

    Expected:
        - 1000.5 → 1001
        - 1000.4 → 1000
    """
    layers = [
        InventoryTransaction(
            "SKU01", Decimal("1"), Decimal("1000.5"), date.today(), "IN"
        )
    ]
    cogs = calculate_cogs_weighted_average(layers, Decimal("1"))
    assert cogs == Decimal("1001")
