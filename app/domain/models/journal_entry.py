# app/domain/models/journal_entry.py
"""
Domain models cho Bút toán kế toán (Journal Entry) theo TT99/2025/TT-BTC.
[TT99-Đ10] Mọi dòng bút toán phải có chứng từ gốc (số và ngày).
"""

import uuid
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List, Optional


class DetailObjectType(Enum):
    """
    Các loại đối tượng chi tiết theo yêu cầu TT99 (sub-ledger tracking).
    """

    NONE = "NONE"
    CUSTOMER = "KHACH_HANG"
    SUPPLIER = "NHA_CUNG_CAP"
    INVENTORY = "HANG_HOA"
    COST_OBJECT = "DOI_TUONG_CHI_PHI"
    FIXED_ASSET = "TAI_SAN_CO_DINH"


class TransactionType(Enum):
    """Loại giao dịch Nợ/Có."""

    DEBIT = "Nợ"
    CREDIT = "Có"


@dataclass(frozen=True)
class ButToanLine:
    """
    [TT99-Đ10] Dòng bút toán phải có chứng từ gốc.
    Đây là Value Object — không có identity, chỉ xác định bởi giá trị.
    """

    # —— CÁC TRƯỜNG BẮT BUỘC (KHÔNG CÓ DEFAULT) ——
    account_number: str
    amount: Decimal
    transaction_type: TransactionType
    so_chung_tu_goc: str  # ← SỐ CHỨNG TỪ GỐC (BẮT BUỘC)
    ngay_chung_tu_goc: date  # ← NGÀY CHỨNG TỪ GỐC (BẮT BUỘC)

    # —— CÁC TRƯỜNG TÙY CHỌN (CÓ DEFAULT) ——
    detail_object_type: DetailObjectType = field(default=DetailObjectType.NONE)
    detail_object_id: Optional[str] = field(default=None)


@dataclass(frozen=True)
class GhiSoKeToan:
    """
    Entity đại diện cho một Bút toán (Journal Entry).
    Đây là Aggregate Root — chịu trách nhiệm toàn vẹn nghiệp vụ ghi sổ kép.
    """

    # —— CÁC TRƯỜNG BẮT BUỘC ——
    entry_date: date
    document_type: str  # Loại chứng từ (PT, PC, BC...)
    document_number: str  # Số chứng từ (duy nhất)
    description: str
    lines: List[ButToanLine]

    # —— CÁC TRƯỜNG TÙY CHỌN ——
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: date = field(default_factory=date.today)
