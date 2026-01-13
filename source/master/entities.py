"""
PROJECT: TT99ACCT - Hệ thống Kế toán chuẩn Thông tư 99/2025/TT-BTC
MODULE: MASTER - ENTITIES (Phân hệ Đối tượng)
DESCRIPTION: Quản lý Khách hàng, Nhà cung cấp, Nhân viên và Đối tượng khác.
             Hỗ trợ kiểm soát hạn mức nợ, MST và vết kiểm toán (Audit Trail).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
import re


@dataclass
class Entity:
    """Cấu trúc dữ liệu đối tượng đạt chuẩn Production."""

    id: str  # Khóa chính (Primary Key) - Định danh duy nhất
    name: str  # Tên pháp nhân/cá nhân (Ghi trên hóa đơn)
    tax_id: Optional[str]  # Khóa phụ (Unique) - Mã số thuế chuẩn VN
    type: str  # CUSTOMER, SUPPLIER, EMPLOYEE, INTERNAL

    # --- Thông tin quản trị & Thuế ---
    address: str = ""  # Địa chỉ đăng ký kinh doanh
    email_invoice: str = ""  # Email tự động gửi hóa đơn điện tử
    default_account: str = ""  # TK công nợ mặc định (131, 331, 141)

    # --- Kiểm soát rủi ro tài chính (CFO's Fields) ---
    debt_limit: float = 0.0  # Hạn mức nợ tối đa (0 = Không giới hạn)
    payment_term_days: int = 0  # Số ngày được phép nợ

    # --- Thông tin thanh toán (Bank Transfer) ---
    bank_account: str = ""
    bank_name: str = ""

    # --- Audit Trail & System State ---
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    note: str = ""


class EntityRegistry:
    """Bộ máy quản lý danh mục đối tượng tập trung."""

    def __init__(self):
        # Khởi tạo dữ liệu mẫu chuẩn (Dữ liệu Mock cho Production)
        self._entities: List[Entity] = [
            Entity(
                id="KH_VINAMILK",
                name="CP Sữa Việt Nam",
                tax_id="0300588569",
                type="CUSTOMER",
                debt_limit=1000000000,
                default_account="131",
            ),
            Entity(
                id="NCC_DELL",
                name="Dell Vietnam Technology",
                tax_id="0101234567",
                type="SUPPLIER",
                default_account="331",
            ),
            Entity(
                id="NV_ADMIN",
                name="Lê Văn Quản Trị",
                tax_id="8012345678",
                type="EMPLOYEE",
                default_account="141",
            ),
        ]
        # Map để truy xuất siêu tốc (O(1))
        self.entity_map: Dict[str, Entity] = {e.id: e for e in self._entities}

    def validate_mst(self, tax_id: str) -> bool:
        """Kiểm tra MST Việt Nam: 10 số hoặc 13 số (nhánh)."""
        if not tax_id:
            return True
        return bool(re.match(r"^[0-9]{10}(-[0-9]{3})?$", tax_id))

    def add_entity(self, entity: Entity) -> tuple:
        """Thêm mới đối tượng với các bước kiểm tra logic chặt chẽ."""
        if entity.id in self.entity_map:
            return False, f"ID {entity.id} đã tồn tại."
        if not self.validate_mst(entity.tax_id):
            return False, "Định dạng Mã số thuế không hợp lệ."

        self.entity_map[entity.id] = entity
        self._entities.append(entity)
        return True, "Thành công"

    def search(self, query: str) -> List[Entity]:
        """Tìm kiếm thông minh: Theo ID, Tên hoặc MST."""
        query = query.lower()
        return [
            e
            for e in self._entities
            if query in e.id.lower()
            or query in e.name.lower()
            or (e.tax_id and query in e.tax_id)
        ]

    def get_by_id(self, eid: str) -> Optional[Entity]:
        """Lấy đối tượng, trả về None nếu không thấy."""
        return self.entity_map.get(eid)


# Khởi tạo instance toàn cục (Singleton)
ENTITIES = EntityRegistry()

# --- VÍ DỤ KIỂM TRA (Sử dụng cho lập trình viên thế hệ sau) ---
if __name__ == "__main__":
    found = ENTITIES.search("Vina")
    for e in found:
        print(
            f"Tìm thấy: {e.name} - MST: {e.tax_id} - Hạn mức: {e.debt_limit:,.0f} VND"
        )
