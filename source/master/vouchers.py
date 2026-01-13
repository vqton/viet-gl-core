"""
PROJECT: TT99ACCT - Hệ thống Kế toán chuẩn Thông tư 99/2025/TT-BTC
MODULE: MASTER - VOUCHERS
DESCRIPTION: Định nghĩa các loại chứng từ và quy tắc đánh số (Auto-numbering).
AUTHORS: PM & CFO
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict


@dataclass
class VoucherType:
    """Định nghĩa quy tắc cho từng loại chứng từ (Ví dụ: Phiếu Thu, Phiếu Chi)."""

    code: str  # Mã loại chứng từ (PT, PC, PN, PX, PK)
    name: str  # Tên loại chứng từ
    prefix: str  # Tiền tố đánh số (Ví dụ: 'PT')
    default_desc: str  # Diễn giải mặc định
    auto_number: bool = True


@dataclass
class JournalEntry:
    """Chi tiết một dòng bút toán (Accounting Line)."""

    account_id: str  # Tài khoản hạch toán
    description: str  # Diễn giải chi tiết cho từng dòng
    debit: float = 0.0  # Số tiền bên Nợ
    credit: float = 0.0  # Số tiền bên Có
    entity_id: Optional[str] = None  # Đối tượng (nếu tài khoản yêu cầu)
    inventory_id: Optional[str] = None  # Mã kho/vật tư (nếu có)


class VoucherManager:
    """Bộ máy quản lý và kiểm soát các loại chứng từ trong hệ thống."""

    def __init__(self):
        # KHỞI TẠO CÁC LOẠI CHỨNG TỪ CHUẨN (CFO Approved)
        self._voucher_types = {
            "PT": VoucherType("PT", "Phiếu Thu", "PT", "Thu tiền từ..."),
            "PC": VoucherType("PC", "Phiếu Chi", "PC", "Chi tiền cho..."),
            "PN": VoucherType("PN", "Phiếu Nhập Kho", "PN", "Nhập kho vật tư..."),
            "PX": VoucherType("PX", "Phiếu Xuất Kho", "PX", "Xuất kho bán hàng..."),
            "PK": VoucherType("PK", "Phiếu Kế Toán", "PK", "Kết chuyển/Điều chỉnh..."),
        }

        # Bộ đếm số thứ tự để đánh số tự động (Production logic)
        self._counters: Dict[str, int] = {code: 0 for code in self._voucher_types}

    def generate_number(self, code: str, date: datetime) -> str:
        """
        Tạo số chứng từ tự động theo định dạng: PREFIX/MM-YYYY/SERIAL
        Ví dụ: PT/01-2026/0001
        """
        if code not in self._voucher_types:
            return "UNKNOWN"

        self._counters[code] += 1
        v_type = self._voucher_types[code]
        serial = str(self._counters[code]).zfill(4)  # Đánh số 4 chữ số
        return f"{v_type.prefix}/{date.strftime('%m-%Y')}/{serial}"

    def get_type(self, code: str) -> Optional[VoucherType]:
        return self._voucher_types.get(code)


# Khởi tạo instance quản lý chứng từ
VOUCHER_SERVICE = VoucherManager()

# --- DEMO TEST (Chạy thử nghiệm cho dev) ---
if __name__ == "__main__":
    current_date = datetime.now()

    # Giả lập tạo số phiếu thu
    num1 = VOUCHER_SERVICE.generate_number("PT", current_date)
    num2 = VOUCHER_SERVICE.generate_number("PT", current_date)

    print(f"Số phiếu thu 1: {num1}")  # Kết quả: PT/01-2026/0001
    print(f"Số phiếu thu 2: {num2}")  # Kết quả: PT/01-2026/0002
