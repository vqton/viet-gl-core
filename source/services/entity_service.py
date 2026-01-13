"""
PATH: D:/TT99ACCT/source/services/entity_service.py
ROLE: Quản lý logic nghiệp vụ cho Đối tượng
"""

from source.database.storage import DB_STORAGE


class EntityService:
    def create_entity(self, entity_id, name, tax_code=None, e_type="KH", **kwargs):

        # 1. Validation Nghiệp vụ
        if not entity_id or len(entity_id) < 2:
            return False, "Mã đối tượng quá ngắn hoặc không hợp lệ."

        # Lớp chặn nghiệp vụ (Business Logic Validation)
        if entity_id is None or len(str(entity_id).strip()) < 3:
            return (
                False,
                "Error: entity_id is required and must be at least 3 characters.",
            )

        if e_type == "KH" and not tax_code:
            # CFO yêu cầu: Khách hàng tổ chức bắt buộc phải có MST
            print("Cảnh báo: Khách hàng không có MST sẽ bị đưa vào danh sách rà soát.")

        # 2. Logic xử lý dữ liệu trước khi lưu
        name = name.strip().upper()  # Chuẩn hóa tên viết hoa toàn bộ

        # 3. Gọi Storage để thực thi
        return DB_STORAGE.add_entity(entity_id, name, tax_code, e_type, **kwargs)

    def get_entity_info(self, entity_id):
        # Logic lấy thông tin đối tượng (có thể mở rộng thêm check công nợ tại đây)
        pass


ENTITY_SERVICE = EntityService()
