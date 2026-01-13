"""
PROJECT: TT99ACCT - Hệ thống Kế toán chuẩn Thông tư 99/2025/TT-BTC
MODULE: REPORTS - LEDGER
DESCRIPTION: Trích xuất dữ liệu từ Storage để lập Sổ Nhật Ký Chung và Sổ Cái.
PATH: D:/TT99ACCT/source/reports/ledger.py
"""

import sqlite3
import pandas as pd  # Sử dụng pandas để định dạng bảng báo cáo chuyên nghiệp
from database.storage import DB_STORAGE
from security.logger_config import logger


class AccountingReports:
    def __init__(self, db_path: str = None):
        # Lấy đường dẫn DB từ storage đã cấu hình
        self.db_path = db_path or DB_STORAGE.db_path

    def get_general_journal(self, start_date: str, end_date: str):
        """
        Lập Sổ Nhật Ký Chung (General Journal).
        Hiển thị toàn bộ giao dịch phát sinh trong kỳ.
        """
        query = """
            SELECT 
                h.date_at as "Ngày hạch toán",
                h.v_no as "Số chứng từ",
                j.description as "Diễn giải",
                j.account_id as "TK Đối ứng",
                j.debit as "Nợ",
                j.credit as "Có"
            FROM voucher_header h
            JOIN journal_entries j ON h.v_id = j.v_id
            WHERE h.date_at BETWEEN ? AND ? AND h.status = 'POSTED'
            ORDER BY h.date_at ASC, h.v_no ASC, j.line_id ASC
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(query, conn, params=(start_date, end_date))

                # Thêm dòng tổng cộng
                total_debit = df["Nợ"].sum()
                total_credit = df["Có"].sum()

                logger.info(f"Đã xuất Sổ Nhật Ký Chung từ {start_date} đến {end_date}")
                return df, total_debit, total_credit
        except Exception as e:
            logger.error(f"Lỗi khi lập Nhật ký chung: {e}")
            return None, 0, 0

    def get_general_ledger(self, account_id: str, start_date: str, end_date: str):
        """
        Lập Sổ Cái (General Ledger) cho một tài khoản cụ thể.
        Có tính toán số dư đầu kỳ và lũy kế phát sinh.
        """
        # 1. Tính số dư đầu kỳ (Trước start_date)
        # (Giả định: Debit - Credit = Balance)
        open_bal_query = """
            SELECT SUM(debit) - SUM(credit) as balance
            FROM journal_entries j
            JOIN voucher_header h ON j.v_id = h.v_id
            WHERE j.account_id LIKE ? AND h.date_at < ? AND h.status = 'POSTED'
        """

        # 2. Lấy phát sinh trong kỳ
        detail_query = """
            SELECT 
                h.date_at as "Ngày",
                h.v_no as "Số hiệu",
                j.description as "Diễn giải",
                j.debit as "Nợ",
                j.credit as "Có"
            FROM journal_entries j
            JOIN voucher_header h ON j.v_id = h.v_id
            WHERE j.account_id = ? AND h.date_at BETWEEN ? AND ? AND h.status = 'POSTED'
            ORDER BY h.date_at ASC
        """

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Tính số dư đầu kỳ
                cursor = conn.cursor()
                cursor.execute(open_bal_query, (f"{account_id}%", start_date))
                row = cursor.fetchone()
                opening_balance = row[0] if row[0] else 0.0

                # Lấy chi tiết
                df = pd.read_sql_query(
                    detail_query, conn, params=(account_id, start_date, end_date)
                )

                # Tính số dư lũy kế (Running Balance)
                df["Số dư"] = opening_balance + df["Nợ"].cumsum() - df["Có"].cumsum()

                return df, opening_balance
        except Exception as e:
            logger.error(f"Lỗi khi lập Sổ cái tài khoản {account_id}: {e}")
            return None, 0


# Instance báo cáo
REPORT_SERVICE = AccountingReports()
