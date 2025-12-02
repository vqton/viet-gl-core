# app/application/validators/tt99_account_validator.py
from app.application.interfaces.account_validator import TaiKhoanValidator
from app.domain.models.account import TaiKhoan as TaiKhoanDomain


class TT99TaiKhoanValidator(TaiKhoanValidator):
    """
    Validator đảm bảo tài khoản tuân thủ TT99/2025/TT-BTC và Phụ lục II.
    """

    def validate(self, tai_khoan: TaiKhoanDomain):
        # 1. Kiểm tra nhóm tài khoản 9xx (TT99 không có)
        if tai_khoan.so_tai_khoan.startswith("9"):
            raise ValueError("TT99/2025/TT-BTC không có tài khoản nhóm 9xx.")

        # 2. Kiểm tra định dạng số tài khoản (vd: chỉ gồm số, dài tối đa 10 ký tự)
        if not tai_khoan.so_tai_khoan.isdigit():
            raise ValueError("Số tài khoản chỉ được chứa ký tự số.")

        if len(tai_khoan.so_tai_khoan) > 10:
            raise ValueError("Số tài khoản không được vượt quá 10 ký tự.")

        # 3. (Tùy chọn) Kiểm tra tên tài khoản theo danh sách chuẩn (có thể load từ file)
        # self._kiem_tra_ten_tai_khoan_theo_pl2(tai_khoan)
