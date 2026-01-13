"""
PROJECT: TT99ACCT - Hệ thống Kế toán chuẩn Thông tư 99/2025/TT-BTC
MODULE: CORE - ENGINE (Validation & Processing)
DESCRIPTION: Kiểm soát tính cân đối, ràng buộc pháp lý và tính nhất quán dữ liệu.
"""

from typing import List, Tuple, Dict
from master.accounts import COA
from master.entities import ENTITIES
from master.vouchers import JournalEntry


class AccountingEngine:
    """Bộ máy kiểm soát giao dịch theo tiêu chuẩn kiểm toán quốc tế."""

    @staticmethod
    def validate_voucher(
        voucher_type: str, entries: List[JournalEntry]
    ) -> Tuple[bool, List[str]]:
        """
        Kiểm tra toàn diện chứng từ trước khi vào sổ cái.
        Trả về: (Hợp lệ: bool, Danh sách lỗi: List[str])
        """
        errors = []
        if not entries:
            return False, ["Chứng từ trống, không có dữ liệu hạch toán."]

        total_debit = 0.0
        total_credit = 0.0
        has_type_0 = False
        has_normal_type = False

        for idx, entry in enumerate(entries):
            line_no = idx + 1
            acc = COA.get_account(entry.account_id)

            # 1. Kiểm tra tồn tại & Tài khoản lá (Thông tư 99)
            if not acc:
                errors.append(
                    f"Dòng {line_no}: Tài khoản {entry.account_id} không có trong danh mục."
                )
                continue

            if not COA.is_leaf(entry.account_id):
                errors.append(
                    f"Dòng {line_no}: Không được hạch toán vào TK tổng hợp {entry.account_id}."
                )

            # 2. Phân loại tài khoản (Chặn trộn lẫn loại 0 và loại 1-9)
            if acc.group == "0":
                has_type_0 = True
            else:
                has_normal_type = True

            # 3. Kiểm tra ràng buộc Đối tượng (CFO's Rule)
            if acc.require_entity and not entry.entity_id:
                errors.append(
                    f"Dòng {line_no}: Tài khoản {entry.account_id} bắt buộc phải có Đối tượng."
                )

            if entry.entity_id and not ENTITIES.get_by_id(entry.entity_id):
                errors.append(
                    f"Dòng {line_no}: Mã đối tượng {entry.entity_id} không tồn tại."
                )

            # 4. Cộng dồn để kiểm tra cân đối
            total_debit += round(entry.debit, 2)
            total_credit += round(entry.credit, 2)

        # 5. Kiểm tra nguyên tắc hạch toán đơn/kép
        if has_type_0 and has_normal_type:
            errors.append(
                "Lỗi: Không được hạch toán tài khoản ngoài bảng (Loại 0) chung với tài khoản trong bảng."
            )

        if not has_type_0:  # Đối với tài khoản 1-9, bắt buộc phải cân đối
            if round(total_debit, 2) != round(total_credit, 2):
                errors.append(
                    f"Chứng từ không cân. Chênh lệch: {abs(total_debit - total_credit):,.2f}"
                )

        return (len(errors) == 0, errors)

    @staticmethod
    def check_correspondence(debit_acc: str, credit_acc: str) -> bool:
        """
        Kiểm tra tính hợp lý của cặp tài khoản đối ứng.
        Ví dụ: Không cho phép Nợ 111 / Có 111.
        """
        if debit_acc == credit_acc:
            return False
        return True


# Singleton Engine
ENGINE = AccountingEngine()
