# Path: source/main.py
"""
MODULE: main.py
ROLE: Điểm khởi chạy ứng dụng chính (Production Entry Point).
PURPOSE: 
    1. Thực hiện các giao dịch nghiệp vụ thực tế (Hạch toán chứng từ).
    2. Xuất báo cáo quản trị nhanh (Bảng cân đối phát sinh).
    3. Đảm bảo luồng vận hành không bị gián đoạn bởi lỗi dữ liệu.
"""

import time
from datetime import datetime
from sqlalchemy.orm import Session
from source.database.foundation import engine
from source.services.accounting import ACC_SERVICE

def main():
    """
    Hàm vận hành chính của hệ thống kế toán TT99.
    Thực hiện luồng: Ghi sổ -> Truy vấn báo cáo -> Hiển thị kết quả.
    """
    print("\n" + "="*20 + " TT99 ACCT: HỆ THỐNG VẬN HÀNH CHÍNH THỨC " + "="*20)

    # Sử dụng context manager để quản lý session an toàn
    with Session(engine) as db:
        # 1. Chuẩn bị dữ liệu demo (Luôn sinh mã mới dựa trên timestamp để tránh UNIQUE error)
        v_no_demo = f"HD_{int(time.time())}"

        # Cấu trúc entries khớp với tham số của AccountingService.post_voucher
        entries = [
            {
                "account_id": "131",
                "debit": 1000,
                "credit": 0,
                "partner_id": "KH_001",
                "partner_type": "CUSTOMER",
                "description": "Bán hàng cho khách KH_001",
            },
            {
                "account_id": "511", 
                "debit": 0, 
                "credit": 1000, 
                "description": "Ghi nhận doanh thu bán hàng"
            },
        ]

        # 2. Ghi sổ (Posting)
        print(f"[*] Đang thực hiện ghi sổ chứng từ: {v_no_demo}...")
        try:
            status, msg = ACC_SERVICE.post_voucher(
                db, "HĐ", v_no_demo, datetime.now(), "Nghiệp vụ bán hàng tự động", entries
            )
            print(f"    👉 Trạng thái vận hành: {msg}")
        except Exception as e:
            print(f"    ❌ Lỗi thực thi ghi sổ: {e}")

        # 3. Truy xuất báo cáo Bảng cân đối phát sinh (Trial Balance)
        print("\n" + "=" * 25 + " BẢNG CÂN ĐỐI PHÁT SINH " + "=" * 25)
        try:
            # Gọi hàm get_trial_balance đã được chuẩn hóa trong accounting.py
            tb = ACC_SERVICE.get_trial_balance(db)

            # Header báo cáo
            print(f"{'Mã TK':<10} | {'Phát sinh Nợ':>15} | {'Phát sinh Có':>15}")
            print("-" * 46)

            # Duyệt dữ liệu từ key 'details' (theo đúng cấu trúc dict trong accounting.py)
            for row in tb.get("details", []):
                print(
                    f"{row['account_id']:<10} | {row['debit']:>15,.0f} | {row['credit']:>15,.0f}"
                )

            print("-" * 46)
            
            # Kiểm tra tính cân đối tổng thể
            balance_status = "CÂN ĐỐI" if tb.get("is_balanced") else "KHÔNG CÂN"
            print(f"TÌNH TRẠNG: {balance_status}")
            print(f"{'TỔNG CỘNG:':<10} | {tb.get('grand_total_debit', 0):>15,.0f} | {tb.get('grand_total_credit', 0):>15,.0f}")
            print("=" * 74)
            
        except Exception as e:
            print(f"❌ Không thể truy xuất báo cáo: {e}")

if __name__ == "__main__":
    main()