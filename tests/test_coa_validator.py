"""
Test cases for COA validator.

Yêu cầu pháp lý:
- Thông tư 99/2025/TT-BTC: Điều 11 (sử dụng đúng hệ thống tài khoản)

Mục tiêu test:
- Xác minh kiểm tra tính hợp lệ của tài khoản kế toán
- Kiểm tra kết cấu Nợ/Có theo loại tài khoản
"""

import pytest
from unittest.mock import patch
from datetime import datetime, date
from decimal import Decimal
from src.domain.entities.journal_entry import JournalEntry
from src.domain.validators.coa_validator import validate_journal_entry
from src.domain.value_objects.purchase_invoice import PurchaseInvoice, PurchaseLineItem
from src.domain.rules.purchase_accounting_rule import apply_purchase_rule


def test_valid_asset_account():
    """
    Test tài khoản tài sản hợp lệ.

    Yêu cầu TT 99:
    - Tài khoản tài sản (1xx) chỉ được ghi Nợ

    Expected:
        - TK 131 (phải thu) ghi Nợ → hợp lệ
    """
    entry = JournalEntry(
        account="131",
        debit=Decimal("10000000"),
        credit=Decimal("0"),
        description="Phải thu KH",
        source_document_id="INV-001",
        accounting_date=date.today(),
        accounting_period_code="2026-Q2",
        created_by="TEST",
        created_at=datetime.now(),
        approved_by="TEST",
        approved_at=datetime.now(),
    )
    assert validate_journal_entry(entry) == True


def test_invalid_revenue_debit():
    """
    Test lỗi khi ghi Nợ vào tài khoản doanh thu.

    Yêu cầu TT 99:
    - TK doanh thu (511, 515...) chỉ được ghi Có

    Expected:
        - validate_journal_entry trả về False
    """
    entry = JournalEntry(
        account="5111",
        debit=Decimal("1000000"),
        credit=Decimal("0"),
        description="Lỗi ghi Nợ doanh thu",
        source_document_id="ERR-001",
        accounting_date=date.today(),
        accounting_period_code="2026-Q2",
        created_by="TEST",
        created_at=datetime.now(),
        approved_by="TEST",
        approved_at=datetime.now(),
    )
    assert validate_journal_entry(entry) == False


def test_purchase_invalid_account():
    """
    Test lỗi khi tài khoản không hợp lệ.

    Yêu cầu TT 99:
    - Điều 11: Phải sử dụng đúng hệ thống tài khoản

    Expected:
        - Ném ValueError khi có tài khoản không tồn tại trong COA
    """
    invoice = PurchaseInvoice(
        invoice_number="PO-003",
        invoice_date=date(2026, 4, 17),
        supplier_tax_code="9876543210",
        supplier_name="NCC DEF",
        line_items=[
            PurchaseLineItem("SKU03", "Phụ kiện", Decimal("100"), Decimal("100000"))
        ],
    )
    with patch(
        "src.domain.rules.purchase_accounting_rule.is_valid_account"
    ) as mock_func:
        mock_func.return_value = False
        with pytest.raises(ValueError, match="Tài khoản không hợp lệ"):
            apply_purchase_rule(
                invoice=invoice,
                document_id="PO-003",
                accounting_date=date(2026, 4, 17),
                accounting_period_code="2026-Q2",
                created_by="NV001",
                created_at=datetime.now(),
                approved_by="KT_TRUONG",
                approved_at=datetime.now(),
            )
