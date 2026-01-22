"""
Module: RecordSalesUseCase

Use case ghi nhận bán hàng theo Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Ghi nhận doanh thu tại thời điểm giao hàng (Điều 19 TT 99)
- Giá vốn phải là giá thực tế (Hướng dẫn TK 156)
- Hàng khuyến mãi phải phân bổ doanh thu (Hướng dẫn TK 511)
- Bút toán phải có người lập, người duyệt (Điều 10, 27 TT 99)
"""

from datetime import datetime, date
from typing import List
from domain.value_objects.sales_invoice import SalesInvoice
from domain.entities.journal_entry import JournalEntry
from domain.services.inventory_valuation_service import InventoryValuationService
from domain.services.journal_entry_service import JournalEntryService
from domain.rules.sales_accounting_rule import apply_sales_rule
from application.dto.sales_dto import SalesDTO


class RecordSalesUseCase:
    """
    Use case xử lý nghiệp vụ bán hàng.

    Attributes:
        inventory_repo: Repository cung cấp dữ liệu tồn kho.
        period_service: Dịch vụ quản lý kỳ kế toán.
    """

    def __init__(self, inventory_repo, period_service):
        self.inventory_repo = inventory_repo
        self.period_service = period_service

    def execute(
        self, sales_dto: SalesDTO, current_user_id: str, approver_id: str = "KT_TRUONG"
    ) -> List[JournalEntry]:
        """
        Thực thi nghiệp vụ bán hàng.

        Args:
            sales_dto (SalesDTO): Dữ liệu đầu vào từ giao diện.
            current_user_id (str): ID người lập chứng từ.
            approver_id (str): ID người duyệt (mặc định: kế toán trưởng).

        Returns:
            List[JournalEntry]: Danh sách bút toán đã được duyệt.

        Raises:
            ValueError: Nếu tồn kho không đủ hoặc dữ liệu không hợp lệ.
        """
        # 1. Chuyển DTO thành entity hợp lệ
        invoice = self._map_to_sales_invoice(sales_dto)

        # 2. Xác định kỳ kế toán
        accounting_period = self.period_service.get_period_by_date(invoice.invoice_date)
        if not accounting_period:
            raise ValueError(
                f"Không tìm thấy kỳ kế toán cho ngày {invoice.invoice_date}"
            )
        if accounting_period.is_closed:
            raise ValueError("Không thể ghi nhận nghiệp vụ trong kỳ đã khóa sổ")

        # 3. Lấy dữ liệu tồn kho thực tế
        inventory_transactions = self.inventory_repo.get_transactions_by_skus(
            [item.sku for item in invoice.line_items]
        )

        # 4. Tính giá vốn thực tế (kiểm tra tồn kho)
        total_quantity = sum(item.quantity for item in invoice.line_items)
        try:
            cogs = InventoryValuationService.calculate_cogs_fifo(
                inventory_transactions, total_quantity
            )
        except ValueError as e:
            raise ValueError(f"Lỗi tính giá vốn: {str(e)}")

        # 5. Áp dụng luật hạch toán
        now = datetime.now()
        entries = apply_sales_rule(
            invoice=invoice,
            inventory_transactions=inventory_transactions,
            document_id=sales_dto.document_id,
            accounting_date=invoice.invoice_date,
            accounting_period_code=accounting_period.code,
            created_by=current_user_id,
            created_at=now,
            approved_by=approver_id,
            approved_at=now,
        )

        # 6. (Tùy chọn) Lưu bút toán vào repository
        # self.journal_entry_repo.save_all(entries)

        return entries

    def _map_to_sales_invoice(self, dto: SalesDTO) -> SalesInvoice:
        """
        Chuyển đổi SalesDTO thành SalesInvoice hợp lệ.

        Kiểm tra tính hợp lệ của MST, ngày hóa đơn, v.v.
        """
        if not dto.seller_tax_code or len(dto.seller_tax_code) not in (10, 14):
            raise ValueError("Mã số thuế người bán không hợp lệ")
        if dto.invoice_date > date.today():
            raise ValueError("Ngày hóa đơn không được lớn hơn ngày hiện tại")

        return SalesInvoice(
            invoice_number=dto.invoice_number,
            invoice_date=dto.invoice_date,
            seller_tax_code=dto.seller_tax_code,
            buyer_name=dto.buyer_name,
            buyer_tax_code=dto.buyer_tax_code or "",
            line_items=dto.line_items,
            vat_rate=dto.vat_rate,
        )
