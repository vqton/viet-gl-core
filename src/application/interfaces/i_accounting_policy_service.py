"""
Module: Accounting Policy Service Interface

Định nghĩa hợp đồng truy xuất chính sách kế toán hiện tại.

Yêu cầu pháp lý:
- Thông tư 99: Doanh nghiệp phải đăng ký phương pháp tính giá vốn
- Chính sách phải được áp dụng nhất quán trong kỳ kế toán

Lưu ý:
- Đây là service interface — không phải repository
- Có thể lấy từ DB, config file, hoặc API
"""

from src.application.dtos.accounting_policy_dto import AccountingPolicyDTO


class IAccountingPolicyService:
    """
    Interface truy xuất chính sách kế toán.

    Methods:
        get_current_policy() -> AccountingPolicyDTO:
            Lấy chính sách kế toán hiện tại của doanh nghiệp.
    """

    def get_current_policy(self) -> AccountingPolicyDTO:
        """
        Lấy chính sách kế toán hiện tại.

        Returns:
            AccountingPolicyDTO: Chính sách đang áp dụng.

        Raises:
            NotImplementedError: Vì đây là interface.
        """
        raise NotImplementedError("Phải được triển khai trong adapter layer")
