# File: seed_coa.py
# Script để chèn dữ liệu tài khoản kế toán mẫu "full" vào DB theo Phụ lục II TT99/2025/TT-BTC
# Bao gồm các tài khoản cấp 1 và cấp 2 theo quy định + một số tài khoản cấp 3 mẫu.
# Thêm đường dẫn gốc của dự án vào sys.path để import module
import os
import sys

# Lấy đường dẫn thư mục hiện tại của script này (seed_coa.py)
script_dir = os.path.dirname(os.path.abspath(__file__))
# Lấy đường dẫn thư mục cha của script (giả định script nằm trong tt99acct/)
project_root = os.path.dirname(script_dir)

# Thêm đường dẫn gốc của dự án vào đầu sys.path
sys.path.insert(0, project_root)

# --- Import sau khi đã thêm path ---
from decimal import Decimal

from app.domain.models.account import LoaiTaiKhoan
from app.infrastructure.database import SessionLocal, engine
from app.infrastructure.models.sql_account import SQLAccount


def seed_data():
    """
    Chèn dữ liệu tài khoản kế toán "full" (cấp 1, 2, và một số 3 mẫu) vào bảng accounts.
    Dữ liệu dựa trên Phụ lục II - Hệ thống tài khoản kế toán cho doanh nghiệp.
    Mục tiêu: Cung cấp bộ COA đầy đủ để kiểm thử các nghiệp vụ chi tiết theo TT99.
    """
    db = SessionLocal()
    try:
        # Kiểm tra xem bảng đã có dữ liệu chưa để tránh chèn trùng (tuỳ chọn)
        # Nếu bạn *muốn* script luôn chèn (và đảm bảo DB trống trước khi chạy), hãy comment 4 dòng dưới
        existing_count = db.query(SQLAccount).count()
        if existing_count > 0:
            print(
                f"Thông báo: Bảng 'accounts' đã có {existing_count} tài khoản. Hủy chèn dữ liệu mẫu 'full'."
            )
            print(
                "Vui lòng xóa dữ liệu cũ trước khi chạy lại script này nếu muốn chèn lại."
            )
            return

        # Danh sách tài khoản mẫu từ Phụ lục II TT99
        # Ghi chú: Bao gồm tài khoản cấp 1, cấp 2 theo quy định và một số tài khoản cấp 3 mẫu.
        # Cấu trúc: (so_tai_khoan, ten_tai_khoan, loai_tai_khoan, cap_tai_khoan, so_tai_khoan_cha, la_tai_khoan_tong_hop)
        accounts_data = [
            # 1. TÀI SẢN (LoaiTaiKhoan.TAI_SAN)
            # 11. Tiền và các khoản tương đương tiền
            ("111", "Tiền Việt Nam", LoaiTaiKhoan.TAI_SAN, 1, None, True),
            ("112", "Ngoại tệ", LoaiTaiKhoan.TAI_SAN, 1, None, True),
            (
                "113",
                "Vàng, bạc, kim khí quý, đá quý",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            # 12. Đầu tư tài chính ngắn hạn
            (
                "121",
                "Chứng khoán kinh doanh",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            (
                "128",
                "Đầu tư nắm giữ đến ngày đáo hạn",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            # 13. Phải thu ngắn hạn
            (
                "131",
                "Phải thu của khách hàng",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            (
                "133",
                "Thuế GTGT được khấu trừ",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            ("136", "Phải thu nội bộ", LoaiTaiKhoan.TAI_SAN, 1, None, True),
            ("138", "Phải thu khác", LoaiTaiKhoan.TAI_SAN, 1, None, True),
            (
                "139",
                "Dự phòng phải thu ngắn hạn",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),  # Contra account
            # 15. Hàng tồn kho
            (
                "151",
                "Hàng mua đang đi đường",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            (
                "152",
                "Nguyên liệu, vật liệu",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            ("153", "Công cụ, dụng cụ", LoaiTaiKhoan.TAI_SAN, 1, None, True),
            (
                "154",
                "Chi phí sản xuất, kinh doanh dở dang",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            ("155", "Thành phẩm", LoaiTaiKhoan.TAI_SAN, 1, None, True),
            ("156", "Hàng hóa", LoaiTaiKhoan.TAI_SAN, 1, None, True),
            ("157", "Hàng gửi đi bán", LoaiTaiKhoan.TAI_SAN, 1, None, True),
            (
                "158",
                "Hàng hóa kho bảo thuế",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            # 21. Tài sản dài hạn
            (
                "211",
                "Tài sản cố định hữu hình",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            (
                "212",
                "Tài sản cố định vô hình",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            (
                "213",
                "Tài sản cố định thuê tài chính",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            (
                "214",
                "Hao mòn tài sản cố định",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),  # Contra account
            # 22. Đầu tư tài chính dài hạn
            (
                "221",
                "Đầu tư vào công ty con",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            (
                "222",
                "Đầu tư vào công ty liên kết, liên doanh",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            ("228", "Đầu tư khác", LoaiTaiKhoan.TAI_SAN, 1, None, True),
            (
                "229",
                "Dự phòng giảm giá đầu tư tài chính",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),  # Contra account
            # 24. Tài sản dở dang, chi phí
            (
                "241",
                "Xây dựng cơ bản dở dang",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            ("242", "Chi phí trả trước", LoaiTaiKhoan.TAI_SAN, 1, None, True),
            (
                "243",
                "Tài sản thuế thu nhập hoãn lại",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            (
                "244",
                "Các khoản đầu tư tài chính không giữ đến ngày đáo hạn",
                LoaiTaiKhoan.TAI_SAN,
                1,
                None,
                True,
            ),
            # 2. NỢ PHẢI TRẢ (LoaiTaiKhoan.NO_PHAI_TRA)
            # 31. Vay và nợ phải trả
            ("311", "Vay ngắn hạn", LoaiTaiKhoan.NO_PHAI_TRA, 1, None, True),
            ("312", "Vay dài hạn", LoaiTaiKhoan.NO_PHAI_TRA, 1, None, True),
            (
                "313",
                "Phải trả người bán",
                LoaiTaiKhoan.NO_PHAI_TRA,
                1,
                None,
                True,
            ),
            # 33. Phải trả, phải nộp
            (
                "331",
                "Phải trả người bán",
                LoaiTaiKhoan.NO_PHAI_TRA,
                1,
                None,
                True,
            ),
            (
                "333",
                "Thuế và các khoản phải nộp nhà nước",
                LoaiTaiKhoan.NO_PHAI_TRA,
                1,
                None,
                True,
            ),
            (
                "334",
                "Phải trả người lao động",
                LoaiTaiKhoan.NO_PHAI_TRA,
                1,
                None,
                True,
            ),
            (
                "335",
                "Chi phí phải trả",
                LoaiTaiKhoan.NO_PHAI_TRA,
                1,
                None,
                True,
            ),
            (
                "336",
                "Phải trả nội bộ",
                LoaiTaiKhoan.NO_PHAI_TRA,
                1,
                None,
                True,
            ),
            ("337", "Phải trả khác", LoaiTaiKhoan.NO_PHAI_TRA, 1, None, True),
            (
                "338",
                "Phải trả, phải nộp khác",
                LoaiTaiKhoan.NO_PHAI_TRA,
                1,
                None,
                True,
            ),
            # 34. Vay và nợ thuê tài chính dài hạn
            (
                "341",
                "Vay và nợ thuê tài chính",
                LoaiTaiKhoan.NO_PHAI_TRA,
                1,
                None,
                True,
            ),
            (
                "343",
                "Phải trả dài hạn khác",
                LoaiTaiKhoan.NO_PHAI_TRA,
                1,
                None,
                True,
            ),
            (
                "347",
                "Thuế thu nhập hoãn lại phải trả",
                LoaiTaiKhoan.NO_PHAI_TRA,
                1,
                None,
                True,
            ),
            # 35. Dự phòng và Quỹ
            (
                "352",
                "Dự phòng phải trả",
                LoaiTaiKhoan.NO_PHAI_TRA,
                1,
                None,
                True,
            ),  # Contra account
            (
                "353",
                "Quỹ tài chính",
                LoaiTaiKhoan.NO_PHAI_TRA,
                1,
                None,
                True,
            ),  # (Có thể là tài khoản vốn nếu coi là của DN)
            # 3. VỐN CHỦ SỞ HỮU (LoaiTaiKhoan.VON_CHU_SO_HUU)
            # 41. Vốn đầu tư của chủ sở hữu
            (
                "411",
                "Vốn đầu tư của chủ sở hữu",
                LoaiTaiKhoan.VON_CHU_SO_HUU,
                1,
                None,
                True,
            ),
            (
                "412",
                "Thặng dư vốn cổ phần",
                LoaiTaiKhoan.VON_CHU_SO_HUU,
                1,
                None,
                True,
            ),
            (
                "413",
                "Chênh lệch tỷ giá hối đoái",
                LoaiTaiKhoan.VON_CHU_SO_HUU,
                1,
                None,
                True,
            ),
            # 42. Quỹ và lợi nhuận chưa phân phối
            (
                "421",
                "Lợi nhuận sau thuế chưa phân phối",
                LoaiTaiKhoan.VON_CHU_SO_HUU,
                1,
                None,
                True,
            ),
            (
                "423",
                "Các quỹ trong vốn chủ sở hữu",
                LoaiTaiKhoan.VON_CHU_SO_HUU,
                1,
                None,
                True,
            ),
            # 4. DOANH THU (LoaiTaiKhoan.DOANH_THU)
            # 51. Doanh thu
            (
                "511",
                "Doanh thu bán hàng và cung cấp dịch vụ",
                LoaiTaiKhoan.DOANH_THU,
                1,
                None,
                True,
            ),
            ("512", "Doanh thu khác", LoaiTaiKhoan.DOANH_THU, 1, None, True),
            (
                "521",
                "Các khoản giảm trừ doanh thu",
                LoaiTaiKhoan.DOANH_THU,
                1,
                None,
                True,
            ),  # Contra account
            ("711", "Thu nhập khác", LoaiTaiKhoan.DOANH_THU, 1, None, True),
            # 5. CHI PHÍ (LoaiTaiKhoan.CHI_PHI)
            # 61. Giá vốn hàng bán (Thương mại)
            ("611", "Mua hàng hóa", LoaiTaiKhoan.CHI_PHI, 1, None, True),
            # 62. Chi phí sản xuất, kinh doanh
            (
                "621",
                "Chi phí nguyên vật liệu trực tiếp",
                LoaiTaiKhoan.CHI_PHI,
                1,
                None,
                True,
            ),
            (
                "622",
                "Chi phí nhân công trực tiếp",
                LoaiTaiKhoan.CHI_PHI,
                1,
                None,
                True,
            ),
            (
                "623",
                "Chi phí sử dụng máy thi công",
                LoaiTaiKhoan.CHI_PHI,
                1,
                None,
                True,
            ),
            (
                "627",
                "Chi phí sản xuất chung",
                LoaiTaiKhoan.CHI_PHI,
                1,
                None,
                True,
            ),
            # 63. Giá vốn hàng bán (Sản xuất)
            (
                "631",
                "Giá vốn hàng bán",
                LoaiTaiKhoan.CHI_PHI,
                1,
                None,
                True,
            ),  # (Thương mại)
            (
                "632",
                "Giá vốn hàng bán",
                LoaiTaiKhoan.CHI_PHI,
                1,
                None,
                True,
            ),  # (Sản xuất)
            # 64. Chi phí bán hàng và QLDN
            ("641", "Chi phí bán hàng", LoaiTaiKhoan.CHI_PHI, 1, None, True),
            (
                "642",
                "Chi phí quản lý doanh nghiệp",
                LoaiTaiKhoan.CHI_PHI,
                1,
                None,
                True,
            ),
            # 8. Chi phí khác và Xác định KQKD
            ("811", "Chi phí khác", LoaiTaiKhoan.CHI_PHI, 1, None, True),
            (
                "821",
                "Chi phí thuế thu nhập doanh nghiệp",
                LoaiTaiKhoan.CHI_PHI,
                1,
                None,
                True,
            ),
            (
                "822",
                "Lợi nhuận khác",
                LoaiTaiKhoan.DOANH_THU,
                1,
                None,
                True,
            ),  # (Có thể coi là doanh thu khác)
            (
                "911",
                "Xác định kết quả kinh doanh",
                LoaiTaiKhoan.KHAC,
                1,
                None,
                True,
            ),  # TK cuối kỳ
            (
                "921",
                "Xác định kết quả hoạt động kinh doanh",
                LoaiTaiKhoan.KHAC,
                1,
                None,
                True,
            ),  # TK cuối kỳ (SX)
            (
                "922",
                "Xác định kết quả hoạt động khác",
                LoaiTaiKhoan.KHAC,
                1,
                None,
                True,
            ),  # TK cuối kỳ (SX)
            # --- Bổ sung các tài khoản cấp 2 & 3 mẫu để hỗ trợ test ---
            # Ví dụ: Chi phí sản xuất chung (627)
            (
                "6271",
                "Chi phí nhân công trực tiếp (phân xưởng)",
                LoaiTaiKhoan.CHI_PHI,
                2,
                "627",
                True,
            ),
            (
                "6272",
                "Chi phí nguyên vật liệu (phân xưởng)",
                LoaiTaiKhoan.CHI_PHI,
                2,
                "627",
                True,
            ),
            (
                "6277",
                "Chi phí khấu hao TSCĐ (phân xưởng)",
                LoaiTaiKhoan.CHI_PHI,
                2,
                "627",
                True,
            ),
            (
                "6278",
                "Chi phí khác bằng tiền (phân xưởng)",
                LoaiTaiKhoan.CHI_PHI,
                2,
                "627",
                True,
            ),
            # Ví dụ: Chi phí QLDN (642)
            (
                "6421",
                "Chi phí lương và phụ cấp",
                LoaiTaiKhoan.CHI_PHI,
                2,
                "642",
                True,
            ),
            (
                "6422",
                "Chi phí khấu hao TSCĐ",
                LoaiTaiKhoan.CHI_PHI,
                2,
                "642",
                True,
            ),
            (
                "6427",
                "Chi phí dịch vụ mua ngoài",
                LoaiTaiKhoan.CHI_PHI,
                2,
                "642",
                True,
            ),
            (
                "6428",
                "Chi phí bằng tiền khác",
                LoaiTaiKhoan.CHI_PHI,
                2,
                "642",
                True,
            ),
            # Ví dụ: Chi phí bán hàng (641)
            (
                "6411",
                "Chi phí lương nhân viên bán hàng",
                LoaiTaiKhoan.CHI_PHI,
                2,
                "641",
                True,
            ),
            (
                "6412",
                "Chi phí khấu hao TSCĐ bán hàng",
                LoaiTaiKhoan.CHI_PHI,
                2,
                "641",
                True,
            ),
            (
                "6417",
                "Chi phí dịch vụ mua ngoài (bán hàng)",
                LoaiTaiKhoan.CHI_PHI,
                2,
                "641",
                True,
            ),
            # Ví dụ: Phải thu khách hàng (131) - tài khoản cấp 3 mẫu
            (
                "1311",
                "Phải thu của khách hàng A",
                LoaiTaiKhoan.TAI_SAN,
                2,
                "131",
                False,
            ),  # Không phải tổng hợp
            (
                "1312",
                "Phải thu của khách hàng B",
                LoaiTaiKhoan.TAI_SAN,
                2,
                "131",
                False,
            ),
            # Ví dụ: Phải trả người bán (331) - tài khoản cấp 3 mẫu
            (
                "3311",
                "Phải trả người bán X",
                LoaiTaiKhoan.NO_PHAI_TRA,
                2,
                "331",
                False,
            ),
            (
                "3312",
                "Phải trả người bán Y",
                LoaiTaiKhoan.NO_PHAI_TRA,
                2,
                "331",
                False,
            ),
            # Ví dụ: Nguyên liệu, vật liệu (152) - tài khoản cấp 3 mẫu
            (
                "1521",
                "Nguyên vật liệu chính",
                LoaiTaiKhoan.TAI_SAN,
                2,
                "152",
                True,
            ),
            ("1522", "Vật liệu phụ", LoaiTaiKhoan.TAI_SAN, 2, "152", True),
            (
                "1523",
                "Công cụ dụng cụ nhỏ",
                LoaiTaiKhoan.TAI_SAN,
                2,
                "152",
                True,
            ),
            # Ví dụ: Hàng hóa (156) - tài khoản cấp 3 mẫu
            ("1561", "Hàng hóa A", LoaiTaiKhoan.TAI_SAN, 2, "156", True),
            ("1562", "Hàng hóa B", LoaiTaiKhoan.TAI_SAN, 2, "156", True),
            # Ví dụ: Tài sản cố định hữu hình (211) - tài khoản cấp 3 mẫu
            ("2111", "Nhà xưởng", LoaiTaiKhoan.TAI_SAN, 2, "211", True),
            ("2112", "Máy móc thiết bị", LoaiTaiKhoan.TAI_SAN, 2, "211", True),
            (
                "2113",
                "Phương tiện vận tải",
                LoaiTaiKhoan.TAI_SAN,
                2,
                "211",
                True,
            ),
            # Ví dụ: Phải trả người lao động (334) - tài khoản cấp 3 mẫu
            (
                "3341",
                "Lương phải trả công nhân",
                LoaiTaiKhoan.NO_PHAI_TRA,
                2,
                "334",
                False,
            ),
            (
                "3342",
                "Lương phải trả nhân viên",
                LoaiTaiKhoan.NO_PHAI_TRA,
                2,
                "334",
                False,
            ),
            # Ví dụ: Phải trả, phải nộp khác (338) - tài khoản cấp 3 mẫu
            (
                "3382",
                "BHXH phải nộp",
                LoaiTaiKhoan.NO_PHAI_TRA,
                2,
                "338",
                False,
            ),
            (
                "3383",
                "BHYT phải nộp",
                LoaiTaiKhoan.NO_PHAI_TRA,
                2,
                "338",
                False,
            ),
            (
                "3384",
                "BHTN phải nộp",
                LoaiTaiKhoan.NO_PHAI_TRA,
                2,
                "338",
                False,
            ),
            (
                "3386",
                "Các khoản khác phải nộp",
                LoaiTaiKhoan.NO_PHAI_TRA,
                2,
                "338",
                False,
            ),
            # Ví dụ: Chi phí trả trước (242) - tài khoản cấp 3 mẫu
            (
                "2421",
                "Chi phí trả trước ngắn hạn",
                LoaiTaiKhoan.TAI_SAN,
                2,
                "242",
                True,
            ),
            (
                "2422",
                "Chi phí trả trước dài hạn",
                LoaiTaiKhoan.TAI_SAN,
                2,
                "242",
                True,
            ),
        ]

        print(
            "Đang chèn dữ liệu tài khoản mẫu 'full' (cấp 1, 2, 3) theo TT99..."
        )
        for acc_data in accounts_data:
            (
                so_tai_khoan,
                ten_tai_khoan,
                loai_tai_khoan,
                cap_tai_khoan,
                so_tai_khoan_cha,
                la_tai_khoan_tong_hop,
            ) = acc_data
            new_account = SQLAccount(
                so_tai_khoan=so_tai_khoan,
                ten_tai_khoan=ten_tai_khoan,
                loai_tai_khoan=loai_tai_khoan,
                cap_tai_khoan=cap_tai_khoan,
                so_tai_khoan_cha=so_tai_khoan_cha,
                la_tai_khoan_tong_hop=la_tai_khoan_tong_hop,
            )
            db.add(new_account)

        db.commit()
        print(
            f"Đã chèn thành công {len(accounts_data)} tài khoản mẫu 'full' vào bảng 'accounts'."
        )
        print(
            "Bây giờ hệ thống đã có các tài khoản cấp 1, cấp 2 theo TT99 và một số tài khoản cấp 3 mẫu để kiểm thử các nghiệp vụ chi tiết."
        )

    except Exception as e:
        db.rollback()  # Nếu có lỗi, hoàn tác giao dịch
        print(f"Lỗi khi chèn dữ liệu: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
