"""
PATH: D:/TT99ACCT/source/services/accounting_service.py
ROLE: Kiểm soát bút toán và tính cân đối tài chính
"""

import json

from sqlalchemy import func
from sqlalchemy.orm import joinedload
from source.database.models.accounting import JournalEntryModel, VoucherHeaderModel
from ..database.storage import DB_STORAGE


import json


class AccountingEngine:
    def __init__(self, coa_path):
        with open(coa_path, "r", encoding="utf-8") as f:
            self.accounts = json.load(f)
        self.leaf_accounts = self._identify_leaf_accounts()

    def _identify_leaf_accounts(self):
        """Tự động xác định tài khoản nào là 'Lá' dựa trên ID"""
        ids = sorted([a["id"] for a in self.accounts])
        leaves = []
        for i, current_id in enumerate(ids):
            # Nếu ID tiếp theo không bắt đầu bằng ID hiện tại -> ID hiện tại là Lá
            if i + 1 < len(ids) and ids[i + 1].startswith(current_id):
                continue
            leaves.append(current_id)
        return leaves

    def validate_transaction(self, voucher):
        """
        Quy tắc kiểm soát:
        1. Tài khoản phải tồn tại.
        2. Phải là tài khoản Lá (Leaf).
        3. Tổng Nợ phải bằng Tổng Có.
        """
        total_debit = 0
        total_credit = 0

        for entry in voucher["entries"]:
            acc_id = entry["account_id"]

            # Kiểm tra tài khoản Lá
            if acc_id not in self.leaf_accounts:
                raise ValueError(
                    f"LỖI NGHIỆP VỤ: Tài khoản {acc_id} là tài khoản tổng hợp. Vui lòng chọn tài khoản chi tiết hơn!"
                )

            total_debit += entry.get("debit", 0)
            total_credit += entry.get("credit", 0)

        # Kiểm tra tính cân bằng kế toán
        if total_debit != total_credit:
            raise ValueError(
                f"LỖI CÂN BẰNG: Tổng Nợ ({total_debit}) khác Tổng Có ({total_credit})!"
            )

        return True


class AccountingService:
    def __init__(self):
        self.master_path = "data/master_data/accounts.json"

    def _get_accounts_map(self):
        """Load danh mục tài khoản từ master JSON"""
        try:
            with open(self.master_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {acc["account_id"]: acc for acc in data}
        except FileNotFoundError:
            return {}

    def post_voucher(self, v_type, v_no, date_at, description, entries):
        """
        Ghi sổ chứng từ sau khi đã qua các lớp kiểm soát
        """
        acc_map = self._get_accounts_map()
        if not acc_map:
            return False, "Hệ thống lỗi: Không tìm thấy danh mục tài khoản Master."

        dr_total = 0
        cr_total = 0

        # Kiểm tra từng dòng định khoản
        for entry in entries:
            acc_id = entry.get("account_id")

            # 1. Check tồn tại
            if acc_id not in acc_map:
                return False, f"Tài khoản {acc_id} không tồn tại."

            # 2. Check tài khoản chi tiết (Enterprise Rule)
            if not acc_map[acc_id].get("is_detail"):
                return False, f"Không được hạch toán vào TK tổng hợp {acc_id}."

            # 3. Check bắt buộc Đối tượng (Phải thu/Phải trả)
            if acc_map[acc_id].get("requires_entity") and not entry.get("entity_id"):
                return (
                    False,
                    f"Tài khoản {acc_id} yêu cầu phải có mã đối tượng kèm theo.",
                )

            dr_total += entry.get("debit", 0)
            cr_total += entry.get("credit", 0)

        # 4. Check nguyên tắc cân đối (Accounting Rule)
        if round(dr_total, 4) != round(cr_total, 4):
            return False, f"Chứng từ không cân! (Nợ: {dr_total} | Có: {cr_total})"

        # 5. Lưu vào Database
        return DB_STORAGE.save_transaction(v_type, v_no, date_at, description, entries)

    def get_gl_report(self, account_id):
        """Truy vấn chi tiết Sổ Cái với kỹ thuật Eager Loading"""
        session = DB_STORAGE.Session()
        try:
            results = (
                session.query(JournalEntryModel)
                .options(joinedload(JournalEntryModel.header))
                .filter(JournalEntryModel.account_id == account_id)
                .order_by(JournalEntryModel.created_at)
                .all()
            )
            return results
        finally:
            session.close()  # Bây giờ đóng session thoải mái vì header đã được tải rồi

    def get_account_balance(self, account_id):
        """Tính số dư hiện tại của tài khoản (Nợ - Có)"""
        session = DB_STORAGE.Session()
        try:
            # Dùng Database để tính tổng thay vì loop trong Python
            totals = (
                session.query(
                    func.sum(JournalEntryModel.debit).label("total_debit"),
                    func.sum(JournalEntryModel.credit).label("total_credit"),
                )
                .filter(JournalEntryModel.account_id == account_id)
                .first()
            )

            debit = totals.total_debit or 0
            credit = totals.total_credit or 0

            # Theo chuẩn kế toán: Số dư = Nợ - Có
            return debit - credit
        finally:
            session.close()

    def get_trial_balance(self, start_date=None, end_date=None):
        """
        CORE LOGIC: Tính bảng cân đối phát sinh cho toàn bộ hệ thống
        Theo nguyên tắc từ lõi: Tính toán trực tiếp từ Journal Entries
        """
        session = DB_STORAGE.Session()
        try:
            # Truy vấn tổng hợp Nợ/Có theo từng Tài khoản
            query = session.query(
                JournalEntryModel.account_id,
                func.sum(JournalEntryModel.debit).label("total_debit"),
                func.sum(JournalEntryModel.credit).label("total_credit"),
            )

            # Lọc theo thời gian nếu có (Edge requirement nhưng Core support)
            if start_date and end_date:
                query = query.join(JournalEntryModel.header).filter(
                    VoucherHeaderModel.date_at.between(start_date, end_date)
                )

            results = query.group_by(JournalEntryModel.account_id).all()

            # CFO Phản biện: Cần format dữ liệu để dễ dàng kiểm soát Nợ = Có
            tb_data = []
            grand_total_debit = 0
            grand_total_credit = 0

            for row in results:
                tb_data.append(
                    {
                        "account_id": row.account_id,
                        "debit": row.total_debit or 0,
                        "credit": row.total_credit or 0,
                    }
                )
                grand_total_debit += row.total_debit or 0
                grand_total_credit += row.total_credit or 0

            return {
                "details": tb_data,
                "grand_total_debit": grand_total_debit,
                "grand_total_credit": grand_total_credit,
                "is_balanced": grand_total_debit == grand_total_credit,
            }
        finally:
            session.close()

    def get_formatted_trial_balance(self):
        core_tb = self.get_trial_balance()
        acc_map = self._get_accounts_map()

        formatted_rows = []
        for item in core_tb["details"]:
            acc_info = acc_map.get(item["account_id"], {})
            formatted_rows.append(
                {
                    "id": item["account_id"],
                    "name": acc_info.get("name", "Unknown"),
                    "debit": item["debit"],
                    "credit": item["credit"],
                }
            )

        formatted_rows.sort(key=lambda x: x["id"])

        # Trả về Dictionary tường minh để main.py truy cập tb["rows"]
        return {
            "rows": formatted_rows,
            "grand_total_debit": core_tb["grand_total_debit"],
            "grand_total_credit": core_tb["grand_total_credit"],
        }


ACC_SERVICE = AccountingService()
