# path: app/application/services/journal_entries/create_service.py
from decimal import Decimal
from typing import Tuple

from app.application.interfaces.account_repo import AccountRepositoryInterface
from app.application.interfaces.journal_entry_repo import (
    JournalEntryRepositoryInterface,
)
from app.application.interfaces.period_repo import (
    AccountingPeriodRepositoryInterface,
)
from app.domain.models.journal_entry import DetailObjectType, GhiSoKeToan


class JournalEntryCreateService:
    """
    Service tạo mới một bút toán (Journal Entry).

    Chịu trách nhiệm thực thi các quy tắc nghiệp vụ quan trọng theo TT99:
    1. Kiểm tra tính cân bằng (Nợ = Có).
    2. Kiểm tra kỳ kế toán đang mở.
    3. Kiểm tra chỉ hạch toán vào tài khoản cấp cuối cùng (Leaf Account - Vấn đề 1 PM).
    4. Kiểm tra Chi tiết Bắt buộc (Mandatory Detail Linkage - Vấn đề 2 PM).
    """

    def __init__(
        self,
        journal_entry_repo: JournalEntryRepositoryInterface,
        account_repo: AccountRepositoryInterface,
        period_repo: AccountingPeriodRepositoryInterface,
    ):
        """
        Khởi tạo JournalEntryCreateService.

        Args:
            journal_entry_repo: Repository để lưu trữ bút toán.
            account_repo: Repository để truy vấn thông tin tài khoản.
            period_repo: Repository để kiểm tra kỳ kế toán.
        """
        self._journal_entry_repo = journal_entry_repo
        self._account_repo = account_repo
        self._period_repo = period_repo

    def execute(self, entry: GhiSoKeToan) -> GhiSoKeToan:
        """
        Thực thi việc tạo bút toán, kiểm tra tính cân bằng và tuân thủ các quy tắc TT99.

        Args:
            entry: Domain model GhiSoKeToan cần được ghi sổ.

        Returns:
            GhiSoKeToan: Bút toán đã được lưu thành công.

        Raises:
            ValueError: Nếu bút toán không hợp lệ (không cân bằng, sai kỳ, hoặc thiếu chi tiết).
            Exception: Lỗi hệ thống khi lưu trữ.
        """

        # 1. Kiểm tra tính cân bằng (Tổng Nợ = Tổng Có)
        total_debit, total_credit = self._calculate_totals(entry)

        if total_debit != total_credit:
            raise ValueError(
                f"Bút toán không cân bằng. Tổng Nợ: {total_debit.quantize(Decimal('0.00'))} | Tổng Có: {total_credit.quantize(Decimal('0.00'))}"
            )

        # 2. Kiểm tra Kỳ Kế toán có đang Mở không
        is_open = self._period_repo.is_date_in_open_period(entry.entry_date)
        if not is_open:
            raise ValueError(
                f"Ngày ghi sổ ({entry.entry_date}) không nằm trong kỳ kế toán đang Mở. Không thể ghi sổ."
            )

        # 3. Kiểm tra các tài khoản và quy tắc chi tiết hóa TT99
        for line in entry.lines:
            account = self._account_repo.get_by_id(line.account_number)

            if not account:
                raise ValueError(
                    f"Tài khoản '{line.account_number}' trong bút toán không tồn tại."
                )

            # Vấn đề 1 PM: Kiểm tra Leaf Account (Tài khoản cấp cuối cùng)
            if self._account_repo.has_children(line.account_number):
                raise ValueError(
                    f"Tài khoản '{line.account_number}' là tài khoản tổng hợp. Vui lòng hạch toán vào tài khoản chi tiết (Leaf Account)."
                )

            # Vấn đề 2 PM: Kiểm tra Chi tiết Bắt buộc (Mandatory Detail Linkage)
            required_types = account.required_detail_type
            if required_types:
                # Nếu Tài khoản yêu cầu chi tiết (required_types không rỗng)
                if line.detail_object_id is None:
                    # Bắt buộc phải có ID đối tượng
                    required_names = [t.value for t in required_types]
                    raise ValueError(
                        f"Tài khoản '{line.account_number}' bắt buộc phải theo dõi chi tiết theo: {', '.join(required_names)}. Vui lòng cung cấp Mã đối tượng."
                    )

                # Bổ sung logic kiểm tra loại đối tượng (detail_object_type)
                if line.detail_object_type not in required_types:
                    # Bắt buộc loại đối tượng phải nằm trong danh sách yêu cầu
                    raise ValueError(
                        f"Tài khoản '{line.account_number}' yêu cầu loại chi tiết {required_types}, nhưng dòng bút toán cung cấp loại {line.detail_object_type.value}."
                    )

            # 3c. Kiểm tra số tiền
            if line.amount <= Decimal(0):
                raise ValueError("Số tiền trong dòng bút toán phải lớn hơn 0.")

            if not line.so_chung_tu_goc or not line.ngay_chung_tu_goc:
                raise ValueError(
                    "Mọi bút toán phải có số và ngày chứng từ gốc theo TT99 Điều 10."
                )
        # 4. Lưu bút toán vào Repository (Database)
        try:
            saved_entry = self._journal_entry_repo.add(entry)
            return saved_entry
        except Exception as e:
            # Xử lý lỗi lưu trữ
            raise Exception(f"Không thể lưu bút toán do lỗi hệ thống: {e}")

    def _calculate_totals(self, entry: GhiSoKeToan) -> Tuple[Decimal, Decimal]:
        """
        Tính tổng Nợ và tổng Có của bút toán để đảm bảo tính cân bằng.

        Args:
            entry: Domain model GhiSoKeToan.

        Returns:
            Tuple[Decimal, Decimal]: Tổng Nợ và Tổng Có.
        """
        total_debit = Decimal(0)
        total_credit = Decimal(0)
        for line in entry.lines:
            if line.transaction_type.value == "Nợ":
                total_debit += line.amount
            elif line.transaction_type.value == "Có":
                total_credit += line.amount
        return total_debit, total_credit
