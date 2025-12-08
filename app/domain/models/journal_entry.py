# path: app/domain/models/journal_entry.py
import uuid
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import List, Optional


class DetailObjectType(Enum):
    """
    Định nghĩa các loại đối tượng cần theo dõi chi tiết (sub-ledger tracking) theo yêu cầu TT99.

    Các loại chi tiết này được liên kết với TaiKhoan để đảm bảo tính minh bạch và chi tiết
    trong báo cáo tài chính.
    """

    NONE = "NONE"  # Không yêu cầu chi tiết
    CUSTOMER = "KHACH_HANG"  # Khách hàng (Dùng cho TK 131, 138,...)
    SUPPLIER = "NHA_CUNG_CAP"  # Nhà cung cấp (Dùng cho TK 331, 338,...)
    INVENTORY = "HANG_HOA"  # Hàng hóa/Vật tư (Dùng cho TK 152, 156,...)
    COST_OBJECT = "DOI_TUONG_CHI_PHI"  # Đối tượng tập hợp chi phí (Dùng cho TK 621, 627,...)
    FIXED_ASSET = (
        "TAI_SAN_CO_DINH"  # Tài sản cố định (Dùng cho TK 211, 214,...)
    )


class TransactionType(Enum):
    """
    Loại giao dịch trong dòng bút toán (Nợ/Có).
    """

    DEBIT = "Nợ"
    CREDIT = "Có"


@dataclass(frozen=True)
class ButToanLine:
    """
    Mô hình một dòng (line) chi tiết trong bút toán.
    """

    account_number: str
    amount: Decimal
    transaction_type: TransactionType

    # === Thuộc tính Chi tiết Bắt buộc (Vấn đề 2 PM) ===
    detail_object_type: DetailObjectType = field(default=DetailObjectType.NONE)
    detail_object_id: Optional[str] = field(
        default=None
    )  # Mã của đối tượng chi tiết (VD: 'KH001', 'NCC005')

@dataclass(frozen=True)
class GhiSoKeToan:
    """
    Mô hình Domain cho Bút Toán Kế Toán (Journal Entry).
    Đây là đơn vị giao dịch cơ bản trong hệ thống kế toán.
    """

    # —— CÁC TRƯỜNG BẮT BUỘC (KHÔNG CÓ DEFAULT) ——
    entry_date: date
    document_type: str  # Loại chứng từ (VD: PC - Phiếu chi, PT - Phiếu thu, BC - Báo có)
    document_number: str  # Số chứng từ (VD: PC0001, PT2025/001)
    description: str  # Diễn giải nghiệp vụ kế toán
    lines: List[ButToanLine]

    # —— CÁC TRƯỜNG TÙY CHỌN (CÓ DEFAULT) ——
    entry_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: date = field(default_factory=date.today)