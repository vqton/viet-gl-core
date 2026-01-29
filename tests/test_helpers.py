"""
Test helpers for creating domain entities.

Cung cấp factory functions để tạo test data chuẩn hóa,
giúp test case ngắn gọn, dễ đọc, và tránh lỗi thiếu tham số.
"""

from datetime import date, datetime
from decimal import Decimal
from src.domain.entities.journal_entry import JournalEntry


def create_journal_entry(
    account: str = "111",
    debit: Decimal = Decimal("0"),
    credit: Decimal = Decimal("0"),
    description: str = "Test journal entry",
    source_document_id: str = "TEST-DOC-001",
    accounting_date: date = None,
    accounting_period_code: str = "2026-Q2",
    created_by: str = "TEST_USER",
    created_at: datetime = None,
    approved_by: str = "KT_TRUONG",
    approved_at: datetime = None,
    status: str = "approved",
    original_entry_id: str = "",
    is_reversal: bool = False,
    adjustment_reason: str = "",
) -> JournalEntry:
    """
    Tạo JournalEntry với các giá trị mặc định hợp lý.

    Args:
        account (str): Mã tài khoản (mặc định: "111")
        debit (Decimal): Số tiền Nợ (mặc định: 0)
        credit (Decimal): Số tiền Có (mặc định: 0)
        description (str): Diễn giải (mặc định: "Test journal entry")
        source_document_id (str): ID chứng từ gốc (bắt buộc theo TT 99)
        accounting_date (date): Ngày kế toán (mặc định: hôm nay)
        accounting_period_code (str): Kỳ kế toán (mặc định: "2026-Q2")
        created_by (str): Người tạo (mặc định: "TEST_USER")
        created_at (datetime): Thời gian tạo (mặc định: hiện tại)
        approved_by (str): Người duyệt (mặc định: "KT_TRUONG")
        approved_at (datetime): Thời gian duyệt (mặc định: hiện tại)
        status (str): Trạng thái (mặc định: "approved")
        original_entry_id (str): ID bút toán gốc (cho điều chỉnh)
        is_reversal (bool): Là bút toán điều chỉnh?
        adjustment_reason (str): Lý do điều chỉnh

    Returns:
        JournalEntry: Đối tượng bút toán đã tạo
    """
    # Thiết lập ngày mặc định
    if accounting_date is None:
        accounting_date = date(2026, 4, 15)  # Ngày cố định cho test reproducible

    if created_at is None:
        created_at = datetime(2026, 4, 15, 10, 30, 0)

    if approved_at is None:
        approved_at = datetime(2026, 4, 15, 11, 0, 0)

    return JournalEntry(
        account=account,
        debit=debit,
        credit=credit,
        description=description,
        source_document_id=source_document_id,
        accounting_date=accounting_date,
        accounting_period_code=accounting_period_code,
        created_by=created_by,
        created_at=created_at,
        approved_by=approved_by,
        approved_at=approved_at,
        status=status,
        original_entry_id=original_entry_id,
        is_reversal=is_reversal,
        adjustment_reason=adjustment_reason,
    )


def create_sales_journal_entries(
    invoice_number: str = "INV-001",
    revenue_amount: Decimal = Decimal("10000000"),
    cogs_amount: Decimal = Decimal("7000000"),
    vat_rate: Decimal = Decimal("0.1"),
) -> list[JournalEntry]:
    """
    Tạo bộ bút toán bán hàng chuẩn theo Thông tư 99.

    Bao gồm:
    - Nợ 131 (Phải thu KH)
    - Có 5111 (Doanh thu)
    - Có 33311 (Thuế GTGT)
    - Nợ 632 (Giá vốn)
    - Có 156 (Xuất kho)

    Args:
        invoice_number (str): Số hóa đơn
        revenue_amount (Decimal): Doanh thu
        cogs_amount (Decimal): Giá vốn
        vat_rate (Decimal): Thuế suất GTGT

    Returns:
        List[JournalEntry]: Danh sách 5 bút toán
    """
    total_with_vat = revenue_amount * (1 + vat_rate)
    vat_amount = revenue_amount * vat_rate

    return [
        create_journal_entry(
            account="131",
            debit=total_with_vat,
            credit=Decimal("0"),
            description=f"Phải thu KH hóa đơn {invoice_number}",
            source_document_id=invoice_number,
        ),
        create_journal_entry(
            account="5111",
            debit=Decimal("0"),
            credit=revenue_amount,
            description=f"Doanh thu hóa đơn {invoice_number}",
            source_document_id=invoice_number,
        ),
        create_journal_entry(
            account="33311",
            debit=Decimal("0"),
            credit=vat_amount,
            description=f"Thuế GTGT hóa đơn {invoice_number}",
            source_document_id=invoice_number,
        ),
        create_journal_entry(
            account="632",
            debit=cogs_amount,
            credit=Decimal("0"),
            description=f"Giá vốn hóa đơn {invoice_number}",
            source_document_id=invoice_number,
        ),
        create_journal_entry(
            account="156",
            debit=Decimal("0"),
            credit=cogs_amount,
            description=f"Xuất kho hóa đơn {invoice_number}",
            source_document_id=invoice_number,
        ),
    ]


def create_purchase_journal_entries(
    invoice_number: str = "PO-001",
    goods_amount: Decimal = Decimal("8000000"),
    freight_cost: Decimal = Decimal("0"),
    vat_rate: Decimal = Decimal("0.1"),
) -> list[JournalEntry]:
    """
    Tạo bộ bút toán mua hàng chuẩn theo Thông tư 99.

    Args:
        invoice_number (str): Số hóa đơn mua
        goods_amount (Decimal): Giá trị hàng hóa
        freight_cost (Decimal): Chi phí vận chuyển
        vat_rate (Decimal): Thuế suất GTGT

    Returns:
        List[JournalEntry]: Danh sách bút toán mua hàng
    """
    total_before_vat = goods_amount + freight_cost
    vat_amount = total_before_vat * vat_rate
    total_with_vat = total_before_vat + vat_amount

    entries = []

    # Hàng hóa (1561)
    if goods_amount > 0:
        entries.append(
            create_journal_entry(
                account="1561",
                debit=goods_amount,
                credit=Decimal("0"),
                description=f"Hàng hóa hóa đơn {invoice_number}",
                source_document_id=invoice_number,
            )
        )

    # Chi phí vận chuyển (1562)
    if freight_cost > 0:
        entries.append(
            create_journal_entry(
                account="1562",
                debit=freight_cost,
                credit=Decimal("0"),
                description=f"Chi phí vận chuyển hóa đơn {invoice_number}",
                source_document_id=invoice_number,
            )
        )

    # Thuế GTGT được khấu trừ (13311)
    if vat_amount > 0:
        entries.append(
            create_journal_entry(
                account="13311",
                debit=vat_amount,
                credit=Decimal("0"),
                description=f"Thuế GTGT được khấu trừ hóa đơn {invoice_number}",
                source_document_id=invoice_number,
            )
        )

    # Phải trả người bán (331)
    entries.append(
        create_journal_entry(
            account="331",
            debit=Decimal("0"),
            credit=total_with_vat,
            description=f"Phải trả NCC hóa đơn {invoice_number}",
            source_document_id=invoice_number,
        )
    )

    return entries
