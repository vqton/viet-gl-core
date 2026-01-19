# Path: source/services/accounting.py
"""
MODULE: accounting.py
PURPOSE: Xử lý các nghiệp vụ kế toán cốt lõi và kiểm soát tính toàn vẹn tài chính.
Cung cấp các công cụ để:
    1. Ghi sổ chứng từ (Posting) với nguyên tắc bút toán kép.
    2. Kiểm tra tính cân đối của giao dịch.
    3. Tính toán số dư tài khoản và lập Bảng cân đối phát sinh (Trial Balance).
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from source.database.models.ledger import GeneralLedger
from source.database.models.accounts import Account

class AccountingService:
    """
    Dịch vụ quản lý nghiệp vụ kế toán (Accounting Engine).
    Thực hiện các phép tính toán tài chính dựa trên dữ liệu từ Sổ cái (General Ledger).
    """

    @staticmethod
    def post_voucher(db: Session, v_type: str, v_no: str, v_date: datetime, 
                     description: str, entries: list) -> tuple[bool, str]:
        """
        Ghi một chứng từ kế toán vào Sổ cái (General Ledger).

        Quy trình xử lý:
            - Kiểm tra tổng Nợ có bằng tổng Có hay không.
            - Kiểm tra sự tồn tại của các tài khoản hạch toán.
            - Thực hiện ghi sổ theo cơ chế Transaction (Nếu lỗi sẽ Rollback toàn bộ).

        Args:
            db (Session): Phiên làm việc với cơ sở dữ liệu.
            v_type (str): Loại chứng từ (VD: PT - Phiếu thu, PC - Phiếu chi).
            v_no (str): Số hiệu chứng từ (Dùng để truy vết và kiểm tra tính cân đối).
            v_date (datetime): Ngày ghi sổ.
            description (str): Nội dung diễn giải tổng quát của chứng từ.
            entries (list): Danh sách các dòng định khoản. Mỗi dòng là một dict chứa:
                            {'account_id': str, 'debit': float, 'credit': float, 'partner_id': str}

        Returns:
            tuple[bool, str]: (Trạng thái thành công, Thông báo chi tiết lỗi nếu có).
        """
        # Kiểm tra tính cân đối của chứng từ (TC-01 trong bộ test)
        total_debit = sum(item.get('debit', 0) for item in entries)
        total_credit = sum(item.get('credit', 0) for item in entries)

        if abs(total_debit - total_credit) > 1e-9:
            return False, f"Chứng từ {v_no} không cân (Nợ: {total_debit} != Có: {total_credit})"

        # Kiểm tra danh mục tài khoản (TC-02 trong bộ test)
        valid_accounts = [acc.id for acc in db.query(Account.id).all()]
        
        try:
            for entry in entries:
                acc_id = entry.get('account_id')
                if acc_id not in valid_accounts:
                    return False, f"Tài khoản {acc_id} không tồn tại trong danh mục hệ thống."

                # Tạo bản ghi hạch toán cho từng dòng
                ledger_entry = GeneralLedger(
                    transaction_date=v_date,
                    voucher_no=v_no,
                    description=entry.get('description', description),
                    account_id=acc_id,
                    partner_id=entry.get('partner_id'),
                    partner_type=entry.get('partner_type'),
                    debit=entry.get('debit', 0),
                    credit=entry.get('credit', 0)
                )
                db.add(ledger_entry)

            db.commit()
            return True, f"Đã ghi sổ thành công chứng từ {v_no}."
        
        except Exception as e:
            db.rollback()
            return False, f"Lỗi hệ thống khi thực hiện ghi sổ: {str(e)}"

    @staticmethod
    def get_trial_balance(db: Session) -> dict:
        """
        Tổng hợp Bảng cân đối phát sinh (Trial Balance).
        Đáp ứng yêu cầu kiểm tra tính cân đối toàn hệ thống (TC-A03).

        Returns:
            dict: Chứa thông tin tổng hợp bao gồm:
                - is_balanced (bool): Trạng thái cân đối tổng thể.
                - grand_total_debit (float): Tổng phát sinh Nợ toàn hệ thống.
                - grand_total_credit (float): Tổng phát sinh Có toàn hệ thống.
                - details (list): Danh sách chi tiết số dư từng tài khoản.
        """
        results = db.query(
            GeneralLedger.account_id,
            func.sum(GeneralLedger.debit).label("total_debit"),
            func.sum(GeneralLedger.credit).label("total_credit")
        ).group_by(GeneralLedger.account_id).all()

        details = [
            {"account_id": r.account_id, "debit": r.total_debit, "credit": r.total_credit}
            for r in results
        ]

        grand_debit = sum(r.total_debit for r in results)
        grand_credit = sum(r.total_credit for r in results)

        return {
            "is_balanced": abs(grand_debit - grand_credit) < 1e-9,
            "grand_total_debit": grand_debit,
            "grand_total_credit": grand_credit,
            "details": details
        }

# Khởi tạo instance phục vụ cho việc Import trong Unit Tests
ACC_SERVICE = AccountingService()