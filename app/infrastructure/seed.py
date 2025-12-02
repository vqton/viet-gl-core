import logging
from typing import List

from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

# Import các thành phần cần thiết
from sqlalchemy.orm import Session

from app.domain.models.account import LoaiTaiKhoan

# Import các thành phần đã được định nghĩa ở các file khác
# 1. Import Base từ base.py
from app.infrastructure.base import Base

# 2. Import engine từ database.py
from app.infrastructure.database import engine
from app.infrastructure.models.sql_account import SQLAccount

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- DỮ LIỆU SƠ ĐỒ TÀI KHOẢN (COA) MỞ RỘNG TOÀN DIỆN (~75 TÀI KHOẢN) ---
COA_DATA: List[dict] = [
    # ========================================================
    # I. TÀI SẢN NGẮN HẠN (ASSET - TAI_SAN) - Loại 1xx
    # ========================================================
    {
        "so_tai_khoan": "111",
        "ten_tai_khoan": "Tiền mặt",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "1111",
        "ten_tai_khoan": "Tiền Việt Nam",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "111",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "1112",
        "ten_tai_khoan": "Ngoại tệ",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "111",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "112",
        "ten_tai_khoan": "Tiền gửi Ngân hàng",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "1121",
        "ten_tai_khoan": "Tiền Việt Nam",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "112",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "1122",
        "ten_tai_khoan": "Ngoại tệ",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "112",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "113",
        "ten_tai_khoan": "Tiền đang chuyển",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "121",
        "ten_tai_khoan": "Đầu tư tài chính ngắn hạn",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "131",
        "ten_tai_khoan": "Phải thu của khách hàng",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "1311",
        "ten_tai_khoan": "Phải thu khách hàng trong nước",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "131",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "133",
        "ten_tai_khoan": "Thuế GTGT được khấu trừ",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "1331",
        "ten_tai_khoan": "Thuế GTGT được khấu trừ của HHDV",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "133",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "1332",
        "ten_tai_khoan": "Thuế GTGT được khấu trừ của TSCĐ",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "133",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "138",
        "ten_tai_khoan": "Phải thu khác",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "141",
        "ten_tai_khoan": "Tạm ứng",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "152",
        "ten_tai_khoan": "Nguyên liệu, vật liệu",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "153",
        "ten_tai_khoan": "Công cụ, dụng cụ",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "154",
        "ten_tai_khoan": "Chi phí SXKD dở dang",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "155",
        "ten_tai_khoan": "Thành phẩm",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "156",
        "ten_tai_khoan": "Hàng hóa",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "1561",
        "ten_tai_khoan": "Giá mua hàng hóa",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "156",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "1567",
        "ten_tai_khoan": "Hàng hóa bất động sản",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "156",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "157",
        "ten_tai_khoan": "Hàng gửi đi bán",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "161",
        "ten_tai_khoan": "Chi phí chờ kết chuyển",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    # ========================================================
    # II. TÀI SẢN DÀI HẠN (ASSET - TAI_SAN) - Loại 2xx
    # ========================================================
    {
        "so_tai_khoan": "211",
        "ten_tai_khoan": "TSCĐ hữu hình",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "2111",
        "ten_tai_khoan": "Nhà cửa, vật kiến trúc",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "211",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "2113",
        "ten_tai_khoan": "Máy móc, thiết bị",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "211",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "213",
        "ten_tai_khoan": "TSCĐ vô hình",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "214",
        "ten_tai_khoan": "Hao mòn TSCĐ (Contra)",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "2141",
        "ten_tai_khoan": "Hao mòn TSCĐ hữu hình",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "214",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "2143",
        "ten_tai_khoan": "Hao mòn TSCĐ vô hình",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "214",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "228",
        "ten_tai_khoan": "Đầu tư dài hạn khác",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "229",
        "ten_tai_khoan": "Dự phòng tổn thất tài sản",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "241",
        "ten_tai_khoan": "Xây dựng cơ bản dở dang",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "242",
        "ten_tai_khoan": "Chi phí trả trước dài hạn",
        "loai_tai_khoan": LoaiTaiKhoan.TAI_SAN,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    # ========================================================
    # III. NỢ PHẢI TRẢ (LIABILITY - NO_PHAI_TRA) - Loại 3xx
    # ========================================================
    {
        "so_tai_khoan": "331",
        "ten_tai_khoan": "Phải trả cho người bán",
        "loai_tai_khoan": LoaiTaiKhoan.NO_PHAI_TRA,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "333",
        "ten_tai_khoan": "Thuế và các khoản PT Nhà nước",
        "loai_tai_khoan": LoaiTaiKhoan.NO_PHAI_TRA,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "3331",
        "ten_tai_khoan": "Thuế GTGT phải nộp",
        "loai_tai_khoan": LoaiTaiKhoan.NO_PHAI_TRA,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "333",
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "33311",
        "ten_tai_khoan": "Thuế GTGT đầu ra",
        "loai_tai_khoan": LoaiTaiKhoan.NO_PHAI_TRA,
        "cap_tai_khoan": 3,
        "so_tai_khoan_cha": "3331",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "3334",
        "ten_tai_khoan": "Thuế thu nhập doanh nghiệp",
        "loai_tai_khoan": LoaiTaiKhoan.NO_PHAI_TRA,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "333",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "3335",
        "ten_tai_khoan": "Thuế thu nhập cá nhân",
        "loai_tai_khoan": LoaiTaiKhoan.NO_PHAI_TRA,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "333",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "3336",
        "ten_tai_khoan": "Thuế tài nguyên",
        "loai_tai_khoan": LoaiTaiKhoan.NO_PHAI_TRA,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "333",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "334",
        "ten_tai_khoan": "Phải trả người lao động",
        "loai_tai_khoan": LoaiTaiKhoan.NO_PHAI_TRA,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "338",
        "ten_tai_khoan": "Phải trả, phải nộp khác",
        "loai_tai_khoan": LoaiTaiKhoan.NO_PHAI_TRA,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "3382",
        "ten_tai_khoan": "Kinh phí công đoàn",
        "loai_tai_khoan": LoaiTaiKhoan.NO_PHAI_TRA,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "338",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "3383",
        "ten_tai_khoan": "Bảo hiểm xã hội",
        "loai_tai_khoan": LoaiTaiKhoan.NO_PHAI_TRA,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "338",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "3387",
        "ten_tai_khoan": "Doanh thu chưa thực hiện",
        "loai_tai_khoan": LoaiTaiKhoan.NO_PHAI_TRA,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "338",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "341",
        "ten_tai_khoan": "Vay và nợ thuê tài chính",
        "loai_tai_khoan": LoaiTaiKhoan.NO_PHAI_TRA,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "352",
        "ten_tai_khoan": "Dự phòng phải trả",
        "loai_tai_khoan": LoaiTaiKhoan.NO_PHAI_TRA,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "353",
        "ten_tai_khoan": "Quỹ khen thưởng, phúc lợi",
        "loai_tai_khoan": LoaiTaiKhoan.NO_PHAI_TRA,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    # ========================================================
    # IV. VỐN CHỦ SỞ HỮU (EQUITY - VON_CHU_SO_HUU) - Loại 4xx
    # ========================================================
    {
        "so_tai_khoan": "411",
        "ten_tai_khoan": "Vốn đầu tư của chủ sở hữu",
        "loai_tai_khoan": LoaiTaiKhoan.VON_CHU_SO_HUU,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "4111",
        "ten_tai_khoan": "Vốn góp của CSH",
        "loai_tai_khoan": LoaiTaiKhoan.VON_CHU_SO_HUU,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "411",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "414",
        "ten_tai_khoan": "Quỹ đầu tư phát triển",
        "loai_tai_khoan": LoaiTaiKhoan.VON_CHU_SO_HUU,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "418",
        "ten_tai_khoan": "Các quỹ khác thuộc Vốn CSH",
        "loai_tai_khoan": LoaiTaiKhoan.VON_CHU_SO_HUU,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "421",
        "ten_tai_khoan": "Lợi nhuận sau thuế chưa phân phối",
        "loai_tai_khoan": LoaiTaiKhoan.VON_CHU_SO_HUU,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "4211",
        "ten_tai_khoan": "LNST chưa PP năm trước",
        "loai_tai_khoan": LoaiTaiKhoan.VON_CHU_SO_HUU,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "421",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "4212",
        "ten_tai_khoan": "LNST chưa PP năm nay",
        "loai_tai_khoan": LoaiTaiKhoan.VON_CHU_SO_HUU,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "421",
        "la_tai_khoan_tong_hop": False,
    },
    # ========================================================
    # V. DOANH THU (INCOME - DOANH_THU) - Loại 5xx, 7xx
    # ========================================================
    {
        "so_tai_khoan": "511",
        "ten_tai_khoan": "Doanh thu bán hàng và cung cấp DV",
        "loai_tai_khoan": LoaiTaiKhoan.DOANH_THU,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "5111",
        "ten_tai_khoan": "Doanh thu bán hàng hóa",
        "loai_tai_khoan": LoaiTaiKhoan.DOANH_THU,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "511",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "5112",
        "ten_tai_khoan": "Doanh thu bán thành phẩm",
        "loai_tai_khoan": LoaiTaiKhoan.DOANH_THU,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "511",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "5113",
        "ten_tai_khoan": "Doanh thu cung cấp dịch vụ",
        "loai_tai_khoan": LoaiTaiKhoan.DOANH_THU,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "511",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "515",
        "ten_tai_khoan": "Doanh thu hoạt động tài chính",
        "loai_tai_khoan": LoaiTaiKhoan.DOANH_THU,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "521",
        "ten_tai_khoan": "Các khoản giảm trừ doanh thu (Contra)",
        "loai_tai_khoan": LoaiTaiKhoan.DOANH_THU,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "5211",
        "ten_tai_khoan": "Chiết khấu thương mại",
        "loai_tai_khoan": LoaiTaiKhoan.DOANH_THU,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "521",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "5212",
        "ten_tai_khoan": "Giảm giá hàng bán",
        "loai_tai_khoan": LoaiTaiKhoan.DOANH_THU,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "521",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "5213",
        "ten_tai_khoan": "Hàng bán bị trả lại",
        "loai_tai_khoan": LoaiTaiKhoan.DOANH_THU,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "521",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "711",
        "ten_tai_khoan": "Thu nhập khác",
        "loai_tai_khoan": LoaiTaiKhoan.DOANH_THU,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    # ========================================================
    # VI. CHI PHÍ (EXPENSE - CHI_PHI) - Loại 6xx, 8xx
    # ========================================================
    {
        "so_tai_khoan": "611",
        "ten_tai_khoan": "Mua hàng",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "621",
        "ten_tai_khoan": "Chi phí nguyên liệu, vật liệu trực tiếp",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "622",
        "ten_tai_khoan": "Chi phí nhân công trực tiếp",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "623",
        "ten_tai_khoan": "Chi phí sử dụng máy thi công",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "627",
        "ten_tai_khoan": "Chi phí sản xuất chung",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "6271",
        "ten_tai_khoan": "Chi phí nhân viên phân xưởng",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "627",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "6274",
        "ten_tai_khoan": "Chi phí khấu hao TSCĐ",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "627",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "632",
        "ten_tai_khoan": "Giá vốn hàng bán",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "635",
        "ten_tai_khoan": "Chi phí tài chính",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "641",
        "ten_tai_khoan": "Chi phí bán hàng",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "6417",
        "ten_tai_khoan": "Chi phí dịch vụ mua ngoài",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "641",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "6418",
        "ten_tai_khoan": "Chi phí khác bằng tiền",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "641",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "642",
        "ten_tai_khoan": "Chi phí quản lý doanh nghiệp",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": True,
    },
    {
        "so_tai_khoan": "6421",
        "ten_tai_khoan": "Chi phí nhân viên QLDN",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "642",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "6422",
        "ten_tai_khoan": "Chi phí vật liệu QLDN",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "642",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "6423",
        "ten_tai_khoan": "Chi phí CCDC QLDN",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "642",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "6427",
        "ten_tai_khoan": "Chi phí dịch vụ mua ngoài QLDN",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 2,
        "so_tai_khoan_cha": "642",
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "811",
        "ten_tai_khoan": "Chi phí khác",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "821",
        "ten_tai_khoan": "Chi phí thuế TNDN hiện hành",
        "loai_tai_khoan": LoaiTaiKhoan.CHI_PHI,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    # ========================================================
    # VII. XÁC ĐỊNH KẾT QUẢ KINH DOANH (OTHER - KHAC) - Loại 9xx
    # ========================================================
    {
        "so_tai_khoan": "911",
        "ten_tai_khoan": "Xác định kết quả kinh doanh",
        "loai_tai_khoan": LoaiTaiKhoan.KHAC,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    # ========================================================
    # VIII. TÀI KHOẢN NGOÀI BẢNG CÂN ĐỐI (OFF-BALANCE - KHAC) - Loại 0xx
    # ========================================================
    {
        "so_tai_khoan": "001",
        "ten_tai_khoan": "Tài sản thuê ngoài",
        "loai_tai_khoan": LoaiTaiKhoan.KHAC,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
    {
        "so_tai_khoan": "004",
        "ten_tai_khoan": "Nợ khó đòi đã xử lý",
        "loai_tai_khoan": LoaiTaiKhoan.KHAC,
        "cap_tai_khoan": 1,
        "so_tai_khoan_cha": None,
        "la_tai_khoan_tong_hop": False,
    },
]


# Hàm seed_coa vẫn giữ nguyên chức năng và sử dụng engine được truyền vào
def seed_coa(engine: Engine):
    """
    Chèn dữ liệu Sơ đồ Tài khoản (COA) mẫu dựa trên TT99/2025/TT-BTC vào cơ sở dữ liệu.
    """
    logging.info("--- BẮT ĐẦU SEED DỮ LIỆU TÀI KHOẢN KẾ TOÁN (COA) ---")

    try:
        # Sử dụng Session context manager
        with Session(engine) as session:
            # 1. Kiểm tra dữ liệu đã tồn tại chưa
            if session.query(SQLAccount).count() > 0:
                logging.warning(
                    "Bảng 'accounts' đã có dữ liệu. Bỏ qua seeding COA."
                )
                return

            # 2. Chuyển đổi dữ liệu từ List[dict] sang List[SQLAccount]
            accounts_to_add: List[SQLAccount] = []
            for item in COA_DATA:
                try:
                    account = SQLAccount(**item)
                    accounts_to_add.append(account)
                except Exception as e:
                    logging.error(
                        f"Lỗi khi tạo đối tượng SQLAccount cho TK {item.get('so_tai_khoan')}: {e}"
                    )

            if not accounts_to_add:
                logging.error("Không có tài khoản nào hợp lệ để thêm.")
                return

            # 3. Thực hiện thêm dữ liệu vào session
            session.add_all(accounts_to_add)

            # 4. Commit giao dịch
            session.commit()
            logging.info(
                f"Seeding COA hoàn tất. Đã thêm {len(accounts_to_add)} tài khoản."
            )

    except SQLAlchemyError as e:
        logging.error(f"Lỗi SQLAlchemy trong quá trình seeding COA: {e}")
        # Rollback giao dịch nếu có lỗi
        try:
            session.rollback()
        except:
            pass
    except Exception as e:
        logging.error(
            f"Một lỗi không xác định xảy ra trong quá trình seeding COA: {e}"
        )


# --- PHẦN CHẠY SCRIPT TRỰC TIẾP (DEMO) ---
if __name__ == "__main__":
    # Sử dụng engine đã được import từ app/infrastructure/database.py
    try:
        # Đảm bảo bảng đã được tạo trước khi seed.
        logging.info("Kiểm tra và tạo bảng nếu chưa tồn tại...")
        Base.metadata.create_all(bind=engine)

        seed_coa(engine)

    except Exception as e:
        logging.error(f"Không thể chạy script seeding demo: {e}")
