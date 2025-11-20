# File: app/domain/models/account.py
from dataclasses import dataclass
from enum import Enum
from typing import Optional

# 1. Định nghĩa Enum LoaiTaiKhoan dựa trên TT99/2025/TT-BTC và Phụ lục II
# Bao gồm các nhóm tài khoản chính và tài khoản đặc biệt như 'Khac' và 'LoaiTru' (nếu cần tách riêng sau)
class LoaiTaiKhoan(Enum):
    """
    Enum đại diện cho các loại tài khoản kế toán theo TT99/2025/TT-BTC Phụ lục II.
    Một số tài khoản như Hao mòn (214), Dự phòng (229, 352), Giảm trừ doanh thu (521)
    là tài khoản loại trừ (contra accounts), ảnh hưởng đến số dư tài khoản đối ứng.
    Loại 'ChiPhi' ở đây bao gồm cả Chi phí khác (811).
    Loại 'Khac' có thể dùng cho các tài khoản đặc biệt khác không thuộc nhóm chính.
    """
    TAI_SAN = "Tai_San"              # Tài sản (1xx, 2xx)
    NO_PHAI_TRA = "No_Phai_Tra"        # Nợ phải trả (3xx)
    VON_CHU_SO_HUU = "Von_Chu_So_Huu"  # Vốn chủ sở hữu (4xx)
    DOANH_THU = "Doanh_Thu"          # Doanh thu (5xx) và Thu nhập khác (711)
    CHI_PHI = "Chi_Phi"              # Chi phí (6xx, 8xx bao gồm 811 - Chi phí khác)
    # KHAC có thể dùng cho các tài khoản đặc biệt như 911 (Xác định KQKD), 821 (Chi phí thuế TNDN),
    # hoặc các tài khoản ngoài bảng CĐKT nếu cần. Có thể tách riêng nếu cần logic riêng.
    KHAC = "Khac"                   # TK xác định KQKD (911), Chi phí thuế TNDN (821), v.v.


# 2. Định nghĩa Entity TaiKhoan sử dụng dataclass
@dataclass
class TaiKhoan:
    """
    Entity đại diện cho Tài khoản Kế toán theo TT99/2025/TT-BTC Phụ lục II.
    """
    # Các thuộc tính của tài khoản
    so_tai_khoan: str          # Ví dụ: "111", "1331", "6421"
    ten_tai_khoan: str          # Ví dụ: "Tiền mặt", "Thuế GTGT được khấu trừ", "Chi phí nhân viên quản lý"
    loai_tai_khoan: LoaiTaiKhoan # Loại tài khoản (TaiSan, NoPhaiTra, ...)
    cap_tai_khoan: int = 1      # Cấp tài khoản (1, 2, 3)
    so_tai_khoan_cha: Optional[str] = None # Tài khoản cha (nếu có, ví dụ: "133" cho "1331")
    la_tai_khoan_tong_hop: bool = True # Có phải là tài khoản tổng hợp không? (Thông thường TK cấp 1 là True)
    # (Có thể thêm các thuộc tính khác nếu cần sau, ví dụ: la_tai_khoan_loai_tru: bool = False)

    def kiem_tra_hop_le(self):
        """
        Hàm được gọi tự động sau khi __init__ để thực hiện kiểm tra hợp lệ
        dựa trên các quy tắc cơ bản từ TT99/2025/TT-BTC.
        """
        # Kiểm tra không trống
        if not self.so_tai_khoan or not self.so_tai_khoan.strip():
            raise ValueError("Số tài khoản không được để trống hoặc chỉ có khoảng trắng.")
        if not self.ten_tai_khoan or not self.ten_tai_khoan.strip():
            raise ValueError("Tên tài khoản không được để trống hoặc chỉ có khoảng trắng.")

        # Kiểm tra định dạng cơ bản cho so_tai_khoan (nếu có quy tắc cụ thể)
        # Ví dụ: Chỉ chứa số và có độ dài hợp lý (thường là 3-4 ký tự theo TT99)
        # Có thể cần linh hoạt hơn nếu doanh nghiệp tự định nghĩa tài khoản con cấp 4, 5...
        if not self.so_tai_khoan.replace('.', '').replace('-', '').isdigit():
             # Cảnh báo hoặc lỗi nếu định dạng không theo quy ước TT99 (111, 1331, 64211, v.v.)
             # Tuy nhiên, để linh hoạt cho tài khoản tự định nghĩa, có thể chỉ kiểm tra cơ bản
             pass # Hoặc raise ValueError nếu muốn bắt buộc format cụ thể

        # Kiểm tra độ dài (tuỳ chọn, theo chuẩn thường dùng hoặc TT99)
        # TT99 không quy định chính xác độ dài tối đa, nhưng 20 char là hợp lý cho số tài khoản.
        if len(self.so_tai_khoan) > 20:
            raise ValueError("Số tài khoản không được vượt quá 20 ký tự.")
        if len(self.ten_tai_khoan) > 256: # Giới hạn hợp lý cho tên tài khoản
            raise ValueError("Tên tài khoản không được vượt quá 256 ký tự.")

        # Kiểm tra cấp tài khoản (theo TT99, cấp 1-3 là phổ biến, có thể có cấp cao hơn tùy doanh nghiệp)
        # Giới hạn ở 1-3 theo Phụ lục II mẫu.
        if self.cap_tai_khoan < 1 or self.cap_tai_khoan > 3:
            raise ValueError("Cấp tài khoản phải từ 1 đến 3 theo TT99/2025/TT-BTC Phụ lục II.")

        # Kiểm tra so_tai_khoan_cha nếu có
        if self.cap_tai_khoan > 1:
            if not self.so_tai_khoan_cha or not self.so_tai_khoan_cha.strip():
                raise ValueError(f"Tài khoản cấp con (Cấp {self.cap_tai_khoan}) phải có số tài khoản cha.")
            # Có thể thêm kiểm tra để đảm bảo so_tai_khoan_cha tồn tại trong hệ thống ở đây
            # hoặc thực hiện kiểm tra ở lớp Application/Infrastructure khi thêm/sửa tài khoản.
            # Ví dụ: kiểm tra cấp độ cha phải nhỏ hơn cấp độ hiện tại
            # (Điều này khó kiểm tra chỉ với thông tin trong Entity này, nên thường xử lý ở Service/Repository)
            # if self.cap_tai_khoan <= get_parent_level(self.so_tai_khoan_cha): # Không khả thi ở đây
            #     raise ValueError(f"Cấp tài khoản ({self.cap_tai_khoan}) phải lớn hơn cấp tài khoản cha.")

        # Kiểm tra logic la_tai_khoan_tong_hop nếu cần (tuỳ yêu cầu nghiệp vụ cụ thể)
        # Ví dụ: tài khoản cấp 1 thường là tài khoản tổng hợp, nhưng có thể có trường hợp đặc biệt.
        # if self.cap_tai_khoan == 1 and not self.la_tai_khoan_tong_hop:
        #     # Có thể cảnh báo hoặc yêu cầu xác nhận
        #     pass # Tùy logic doanh nghiệp

    def __post_init__(self):
        """
        Hàm được gọi tự động sau khi __init__ để thực hiện kiểm tra hợp lệ.
        """
        self.kiem_tra_hop_le()


# 3. (Tuỳ chọn) Constructor factory method nếu cần kiểm tra thêm logic phức tạp hoặc kiểm tra hợp lệ nâng cao
# class TaiKhoanFactory:
#     @staticmethod
#     def tao_tai_khoan(
#         so_tai_khoan: str,
#         ten_tai_khoan: str,
#         loai_tai_khoan: LoaiTaiKhoan,
#         cap_tai_khoan: int = 1,
#         so_tai_khoan_cha: Optional[str] = None,
#         la_tong_hop: bool = True
#     ) -> TaiKhoan:
#         # Có thể thêm logic kiểm tra phức tạp hơn ở đây trước khi tạo instance
#         # Ví dụ: kiểm tra xem so_tai_khoan có bị trùng không (cần Repository)
#         # hoặc kiểm tra xem so_tai_khoan_cha có tồn tại và cấp độ hợp lệ không (cần Repository)
#         # hoặc gọi một service để kiểm tra tên tài khoản có hợp lệ không
#         tai_khoan = TaiKhoan(so_tai_khoan, ten_tai_khoan, loai_tai_khoan, cap_tai_khoan, so_tai_khoan_cha, la_tong_hop)
#         # Có thể gọi một service kiểm tra hợp lệ bổ sung ở đây
#         # KiemTraHopLeService.kiem_tra_tao_tai_khoan(tai_khoan)
#         return tai_khoan