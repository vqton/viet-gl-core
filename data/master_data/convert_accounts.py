import json


def convert_account_master(input_file, output_file):
    # 1. Đọc dữ liệu JSON cũ (Dạng Object)
    with open(input_file, "r", encoding="utf-8") as f:
        old_data = json.load(f)

    # Lấy danh sách tất cả các ID để so sánh cấp bậc
    all_ids = sorted(old_data.keys())
    new_list = []

    for acc_id, info in old_data.items():
        # 2. Logic xác định is_detail:
        # Nếu không có tài khoản nào khác bắt đầu bằng acc_id này và dài hơn nó
        # thì nó là tài khoản chi tiết nhất (Leaf Node)
        is_detail = True
        for potential_child in all_ids:
            if potential_child.startswith(acc_id) and len(potential_child) > len(
                acc_id
            ):
                is_detail = False
                break

        # 3. Ánh xạ sang cấu trúc mới
        new_acc = {
            "account_id": acc_id,
            "name": info.get("name"),
            "nature": info.get("nature"),
            "group": info.get("group"),
            "requires_entity": info.get(
                "require_entity", False
            ),  # Fix lỗi chính tả require -> requires
            "is_cash": info.get("is_cash", False),
            "is_detail": is_detail,
        }
        new_list.append(new_acc)

    # 4. Lưu ra file JSON mới dạng List
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(new_list, f, ensure_ascii=False, indent=4)

    print(f"Thành công! Đã chuyển đổi {len(new_list)} tài khoản sang chuẩn Enterprise.")


if __name__ == "__main__":
    convert_account_master("accounts_old.json", "accounts.json")
