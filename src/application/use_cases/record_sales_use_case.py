"""
Module: Record Sales Use Case

Ghi nhận nghiệp vụ bán hàng theo Thông tư 99/2025/TT-BTC.

Yêu cầu pháp lý:
- Điều 19 TT 99: Ghi nhận doanh thu tại thời điểm giao hàng
- Hướng dẫn TK 156: Giá vốn phải là giá thực tế theo phương pháp đã chọn
- Điều 27 TT 99: Tạo công nợ chi tiết cho từng khách hàng
- Điều 10, 27 TT 99: Bút toán phải có audit trail đầy đủ

Trách nhiệm:
- Phối hợp giữa hóa đơn, tồn kho, chính sách kế toán và rule hạch toán
- Tạo công nợ chi tiết khi phát sinh phải thu
- Đảm bảo toàn vẹn nghiệp vụ trước khi lưu bút toán
"""

from datetime import datetime, timedelta
from typing import List
from decimal import Decimal
from src.domain.value_objects.sales_invoice import SalesInvoice
from src.domain.entities.journal_entry import JournalEntry
from src.domain.rules.sales_accounting_rule import apply_sales_rule
from src.application.interfaces.i_inventory_repository import IInventoryRepository
from src.application.interfaces.i_journal_entry_repository import IJournalEntryRepository
from src.application.interfaces.i_accounting_policy_service import IAccountingPolicyService
from src.application.interfaces.i_debt_repository import IDebtRepository
from src.application.dtos.sales_invoice_dto import SalesInvoiceDTO
from src.application.use_cases.create_debt_use_case import CreateDebtUseCase

class RecordSalesUseCase:
    """
    Use case ghi nhận bán hàng.
    
    Attributes:
        inventory_repo (IInventoryRepository): Truy xuất tồn kho
        journal_entry_repo (IJournalEntryRepository): Lưu bút toán
        policy_service (IAccountingPolicyService): Lấy chính sách kế toán
        debt_repo (IDebtRepository): Quản lý công nợ
    """
    
    def __init__(
        self,
        inventory_repo: IInventoryRepository,
        journal_entry_repo: IJournalEntryRepository,
        policy_service: IAccountingPolicyService,
        debt_repo: IDebtRepository
    ):
        self.inventory_repo = inventory_repo
        self.journal_entry_repo = journal_entry_repo
        self.policy_service = policy_service
        self.debt_repo = debt_repo

    def execute(self, dto: SalesInvoiceDTO, created_by: str) -> List[JournalEntry]:
        """
        Thực thi ghi nhận bán hàng.
        
        Args:
            dto (SalesInvoiceDTO): Dữ liệu hóa đơn từ UI/API
            created_by (str): ID người lập bút toán
            
        Returns:
            List[JournalEntry]: Danh sách bút toán đã tạo
            
        Raises:
            ValueError: Nếu hóa đơn không hợp lệ hoặc tồn kho không đủ
        """
        # 1. Chuyển DTO → Domain Entity
        invoice = SalesInvoice(
            invoice_number=dto.invoice_number,
            invoice_date=dto.invoice_date,
            seller_tax_code=dto.seller_tax_code,
            buyer_name=dto.buyer_name,
            buyer_tax_code=dto.buyer_tax_code,
            line_items=dto.line_items,
            vat_rate=dto.vat_rate
        )
        
        # 2. Lấy chính sách kế toán hiện tại (để biết phương pháp tính giá vốn)
        policy = self.policy_service.get_current_policy()
        
        # 3. Lấy toàn bộ giao dịch tồn kho cho các SKU trong hóa đơn
        all_inventory_transactions = []
        for item in invoice.line_items:
            transactions = self.inventory_repo.get_transactions_by_sku(item.sku)
            all_inventory_transactions.extend(transactions)
        
        # 4. Tính tổng tiền phải thu (gồm cả thuế GTGT)
        total_amount = sum(item.quantity * item.unit_price for item in invoice.line_items)
        vat_amount = total_amount * dto.vat_rate
        total_with_vat = total_amount + vat_amount
        
        # 5. Tạo công nợ chi tiết (nếu có giá trị)
        if total_with_vat > Decimal('0'):
            from src.application.dtos.debt_creation_dto import DebtCreationDTO
            debt_dto = DebtCreationDTO(
                party_id=f"CUST-{invoice.buyer_tax_code}",
                party_name=invoice.buyer_name,
                party_tax_code=invoice.buyer_tax_code,
                document_id=invoice.invoice_number,
                document_type="SALES",
                amount=total_with_vat,
                due_date=invoice.invoice_date + timedelta(days=30),  # Hạn 30 ngày
                currency="VND"
            )
            CreateDebtUseCase(self.debt_repo).execute(debt_dto)
        
        # 6. Áp dụng rule hạch toán từ core logic
        entries = apply_sales_rule(
            invoice=invoice,
            inventory_transactions=all_inventory_transactions,
            document_id=invoice.invoice_number,
            accounting_date=invoice.invoice_date,
            accounting_period_code=self._get_period_code(invoice.invoice_date),
            created_by=created_by,
            created_at=datetime.now(),
            approved_by="KT_TRUONG",  # Có thể thay bằng user thực tế
            approved_at=datetime.now()
        )
        
        # 7. Lưu bút toán vào hệ thống
        for entry in entries:
            self.journal_entry_repo.save(entry)
            
        return entries

    def _get_period_code(self, date) -> str:
        """Chuyển đổi ngày thành mã kỳ kế toán (ví dụ: 2026-Q2)."""
        year = date.year
        quarter = (date.month - 1) // 3 + 1
        return f"{year}-Q{quarter}"