# path: app/domain/validators/tt99_journal_entry_validator.py
from app.application.interfaces.journal_entry_validator import JournalEntryValidatorInterface
from app.application.interfaces.account_repo import AccountRepositoryInterface
from app.domain.models.journal_entry import GhiSoKeToan, ButToanLine, TransactionType

class TT99JournalEntryValidator(JournalEntryValidatorInterface):
    """
    [DOMAIN LAYER - BUSINESS RULE]
    Xác thực các quy tắc nghiệp vụ hạch toán phức tạp theo Thông tư 99/2025/TT-BTC,
    đặc biệt là quy tắc đối ứng Nợ/Có.
    
    Đây là một quy tắc cốt lõi, độc lập với Application Service gọi nó.
    """
    def __init__(self, account_repo: AccountRepositoryInterface):
        """
        Khởi tạo Validator.

        Args:
            account_repo: Repository để truy vấn thông tin chi tiết về tài khoản.
        """
        self._account_repo = account_repo

    def validate(self, entry: GhiSoKeToan):
        """
        Thực hiện xác thực toàn bộ bút toán dựa trên các quy tắc đối ứng TT99.

        Args:
            entry: Domain model GhiSoKeToan cần được xác thực.

        Raises:
            ValueError: Nếu bút toán vi phạm quy tắc đối ứng.
        """
        debit_lines = [line for line in entry.lines if line.transaction_type == TransactionType.DEBIT]
        credit_lines = [line for line in entry.lines if line.transaction_type == TransactionType.CREDIT]
        
        # 1. Kiểm tra từng cặp Nợ/Có
        for debit_line in debit_lines:
            for credit_line in credit_lines:
                self._check_reciprocal_rule(debit_line, credit_line)
                
    def _check_reciprocal_rule(self, debit_line: ButToanLine, credit_line: ButToanLine):
        """
        Kiểm tra tính hợp lệ của cặp đối ứng Nợ và Có.
        
        Args:
            debit_line: Dòng bút toán ghi Nợ.
            credit_line: Dòng bút toán ghi Có.
        
        Raises:
            ValueError: Nếu cặp Nợ/Có vi phạm quy tắc.
        """
        tk_no = self._account_repo.get_by_id(debit_line.account_number)
        tk_co = self._account_repo.get_by_id(credit_line.account_number)

        if not tk_no or not tk_co:
             # Lỗi này đã được bắt trong Service, nhưng cần kiểm tra lại để an toàn
             raise ValueError("Lỗi hệ thống: Không tìm thấy thông tin Tài khoản khi kiểm tra đối ứng.")

        # Lấy nhóm TK cấp 1 (ví dụ: '111' -> '1', '641' -> '6')
        group_no = tk_no.so_tai_khoan[0]
        group_co = tk_co.so_tai_khoan[0]
        
        # Quy tắc 1: Tiền mặt (111) không được đối ứng trực tiếp với Nguồn vốn chủ sở hữu (4xx).
        if group_no == '1' and tk_no.so_tai_khoan.startswith('111') and group_co == '4':
            raise ValueError(
                f"Lỗi Đối ứng: TK Nợ {tk_no.so_tai_khoan} (Tiền mặt) không được đối ứng trực tiếp với TK Có {tk_co.so_tai_khoan} (Nguồn vốn CSH). Cần qua TK trung gian."
            )
        
        # Quy tắc 2: Không hạch toán nợ, có cùng một tài khoản cấp cuối (Leaf Account Rule - Tương tự Vấn đề 1 PM)
        # Chỉ kiểm tra khi hai tài khoản là một
        if debit_line.account_number == credit_line.account_number:
             raise ValueError(
                f"Lỗi Đối ứng: Không được hạch toán Nợ và Có cùng một tài khoản ({debit_line.account_number})."
            )

        # Quy tắc 3: Doanh thu (5xx, 7xx) không được đối ứng trực tiếp với Tiền (11x)
        if (group_no in ['5', '7'] and group_co == '1' and tk_co.so_tai_khoan.startswith('11')) or \
           (group_co in ['5', '7'] and group_no == '1' and tk_no.so_tai_khoan.startswith('11')):
            # Tạm thời chỉ là cảnh báo, vì có thể có thu tiền ngay.
             print(
                f"Cảnh báo Đối ứng: TK Doanh thu ({group_no}xx) đối ứng trực tiếp với TK Tiền ({tk_no.so_tai_khoan}/{tk_co.so_tai_khoan}). Cần kiểm tra chứng từ bán hàng/thu tiền ngay."
            )