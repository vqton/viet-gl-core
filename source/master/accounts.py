"""
PROJECT: TT99ACCT - Hệ thống Kế toán chuẩn Thông tư 99/2025/TT-BTC
MODULE: MASTER - ACCOUNTS
DESCRIPTION: Quản lý danh mục hệ thống tài khoản, hỗ trợ nạp dữ liệu từ JSON và kiểm tra tính phân cấp.
PATH: D:/TT99ACCT/source/master/accounts.py
"""

import json
import os
from dataclasses import dataclass
from typing import Dict, Optional
from security.logger_config import logger


@dataclass
class Account:
    id: str
    name: str
    nature: str  # DEBIT, CREDIT, hoặc BOTH
    group: str  # Loại tài khoản (1-9)
    require_entity: bool = False
    is_cash: bool = False


class ChartOfAccounts:
    def __init__(
        self, json_relative_path: str = "../../data/master_data/accounts_tt99.json"
    ):
        self.accounts: Dict[str, Account] = {}

        # Xác định đường dẫn tuyệt đối để tránh lỗi môi trường
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.full_path = os.path.normpath(os.path.join(base_path, json_relative_path))

        self.load_from_json()

    def load_from_json(self):
        """Nạp toàn bộ danh mục tài khoản từ file JSON đã chiết xuất từ TT99."""
        if not os.path.exists(self.full_path):
            logger.error(
                f"CRITICAL: Không tìm thấy file JSON danh mục tại {self.full_path}"
            )
            return

        try:
            with open(self.full_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for acc_id, attrs in data.items():
                    # Khởi tạo object Account từ dữ liệu JSON
                    self.accounts[acc_id] = Account(**attrs)

            logger.info(
                f"Hệ thống đã nạp thành công {len(self.accounts)} tài khoản từ danh mục TT99/2025."
            )
        except Exception as e:
            logger.error(f"Lỗi khi xử lý file JSON danh mục: {str(e)}")

    def get_account(self, acc_id: str) -> Optional[Account]:
        """Truy xuất thông tin chi tiết của một tài khoản."""
        return self.accounts.get(acc_id)

    def is_leaf(self, acc_id: str) -> bool:
        """
        NGUYÊN TẮC CFO: Chỉ cho phép hạch toán vào tài khoản lá.
        Nếu một mã tài khoản là tiền tố của mã khác dài hơn, nó là tài khoản mẹ.
        Ví dụ: '111' không phải lá vì có '1111'.
        """
        if acc_id not in self.accounts:
            return False

        # Kiểm tra xem có tài khoản nào bắt đầu bằng acc_id này mà dài hơn không
        has_child = any(
            other_id.startswith(acc_id) and len(other_id) > len(acc_id)
            for other_id in self.accounts.keys()
        )
        return not has_child

    def validate_account_for_posting(self, acc_id: str) -> tuple[bool, str]:
        """Kiểm tra tổng thể điều kiện để tài khoản được phép xuất hiện trên chứng từ."""
        acc = self.get_account(acc_id)
        if not acc:
            return False, f"Tài khoản {acc_id} không tồn tại trong hệ thống."

        if not self.is_leaf(acc_id):
            return (
                False,
                f"Tài khoản {acc_id} là tài khoản tổng hợp, vui lòng chọn tài khoản chi tiết (cấp con).",
            )

        return True, "Hợp lệ"


# Khởi tạo Singleton để dùng chung cho toàn bộ Engine và Report
COA = ChartOfAccounts()
