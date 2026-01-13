"""
PATH: D:/TT99ACCT/source/main.py
"""
import time # Thư viện lấy timestamp
from datetime import datetime # Thư viện lấy ngày tháng
from source.services.entity_service import ENTITY_SERVICE
from source.services.accounting_service import ACC_SERVICE

def main():
    print("\n=== TT99 ACCT: HỆ THỐNG VẬN HÀNH CHÍNH THỨC ===")
    
    # 1. Chuẩn bị dữ liệu demo (Luôn sinh mã mới để tránh UNIQUE error)
    v_no_demo = f"HD_{int(time.time())}"
    
    entries = [
        {"account_id": "131", "debit": 1000, "credit": 0, "entity_id": "KH_001", "description": "Bán hàng"},
        {"account_id": "511", "debit": 0, "credit": 1000, "description": "Doanh thu"}
    ]
    
    # 2. Ghi sổ (Được bảo vệ bởi Try-Except để không chết chương trình)
    try:
        status, msg = ACC_SERVICE.post_voucher(
            "HĐ", v_no_demo, datetime.now(), "Bán hàng tự động", entries
        )
        print(f"Trạng thái vận hành: {msg}")
    except Exception as e:
        print(f"Lỗi ghi sổ: {e}")

    # 3. [EDGE] In Bảng cân đối phát sinh (Luôn chạy được)
    print("\n" + "="*30 + " BẢNG CÂN ĐỐI PHÁT SINH " + "="*30)
    try:
        tb = ACC_SERVICE.get_formatted_trial_balance()
        
        print(f"{'Mã TK':<10} | {'Tên Tài Khoản':<35} | {'Phát sinh Nợ':>15} | {'Phát sinh Có':>15}")
        print("-" * 85)
        
        # QA Check: Đảm bảo tb["rows"] tồn tại trước khi loop
        for row in tb.get("rows", []):
            print(f"{row['id']:<10} | {row['name']:<35} | {row['debit']:>15,.0f} | {row['credit']:>15,.0f}")
            
        print("-" * 85)
        print(f"{'TỔNG CỘNG:':<48} | {tb.get('grand_total_debit', 0):>15,.0f} | {tb.get('grand_total_credit', 0):>15,.0f}")
        print("="*85)
    except Exception as e:
        print(f"Không thể truy xuất báo cáo: {e}")

if __name__ == "__main__":
    main()