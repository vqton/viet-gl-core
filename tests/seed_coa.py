# tests/seed_coa.py
from gl_core.models import AccountChart, Account, AccountType


def seed_tt133_coa():
    """
    Hàm tạo Chart of Accounts theo TT 133 để test
    """
    accounts = {
        "1111": Account("1111", "Tiền Việt Nam", AccountType.ASSET, "debit"),
        "5111": Account("5111", "Doanh thu bán hàng", AccountType.REVENUE, "credit"),
        "632": Account("632", "Giá vốn hàng bán", AccountType.EXPENSE, "debit"),
        "156": Account("156", "Hàng hóa", AccountType.ASSET, "debit"),
        "421": Account("421", "Lợi nhuận sau thuế chưa phân phối", AccountType.EQUITY, "credit"),
        # Thêm tài khoản 911 để kết chuyển cuối năm
        "911": Account("911", "Xác định kết quả kinh doanh", AccountType.TEMPORARY, "debit"),
        # Thêm các tài khoản khác theo cấu hình YAML nếu cần
        "111": Account("111", "Tiền mặt", AccountType.ASSET, "debit"),
        "112": Account("112", "Tiền gửi ngân hàng", AccountType.ASSET, "debit"),
        "1121": Account("1121", "Tiền gửi ngân hàng", AccountType.ASSET, "debit"),
        "113": Account("113", "Tiền đang chuyển", AccountType.ASSET, "debit"),
        "121": Account("121", "Chứng khoán kinh doanh", AccountType.ASSET, "debit"),
        "128": Account("128", "Tài sản ngắn hạn khác", AccountType.ASSET, "debit"),
        "131": Account("131", "Phải thu khách hàng", AccountType.ASSET, "debit"),
        "1311": Account("1311", "Phải thu khách hàng", AccountType.ASSET, "debit"),
        "1312": Account("1312", "Phải thu nội bộ", AccountType.ASSET, "debit"),
        "1313": Account("1313", "Phải thu khác", AccountType.ASSET, "debit"),
        "141": Account("141", "Tạm ứng", AccountType.ASSET, "debit"),
        "151": Account("151", "Hàng tồn kho", AccountType.ASSET, "debit"),
        "1511": Account("1511", "Nguyên vật liệu", AccountType.ASSET, "debit"),
        "1512": Account("1512", "Thành phẩm", AccountType.ASSET, "debit"),
        "1513": Account("1513", "Hàng hóa", AccountType.ASSET, "debit"),
        "242": Account("242", "Chi phí trả trước", AccountType.ASSET, "debit"),
        "211": Account("211", "Tài sản cố định hữu hình", AccountType.ASSET, "debit"),
        "2111": Account("2111", "Đất", AccountType.ASSET, "debit"),
        "2112": Account("2112", "Nhà xưởng", AccountType.ASSET, "debit"),
        "2113": Account("2113", "Máy móc thiết bị", AccountType.ASSET, "debit"),
        "213": Account("213", "Tài sản cố định vô hình", AccountType.ASSET, "debit"),
        "2131": Account("2131", "Phần mềm", AccountType.ASSET, "debit"),
        "2132": Account("2132", "Quyền sử dụng đất", AccountType.ASSET, "debit"),
        "217": Account("217", "Bất động sản đầu tư", AccountType.ASSET, "debit"),
        "221": Account("221", "Đầu tư tài chính dài hạn", AccountType.ASSET, "debit"),
        "2211": Account("2211", "Cổ phiếu, trái phiếu dài hạn", AccountType.ASSET, "debit"),
        "2212": Account("2212", "Các khoản đầu tư dài hạn khác", AccountType.ASSET, "debit"),
        "228": Account("228", "Tài sản dài hạn khác", AccountType.ASSET, "debit"),
        "311": Account("311", "Vay và nợ ngắn hạn", AccountType.LIABILITY, "credit"),
        "315": Account("315", "Nợ dài hạn", AccountType.LIABILITY, "credit"),
        "331": Account("331", "Phải trả người bán", AccountType.LIABILITY, "credit"),
        "333": Account("333", "Thuế và các khoản phải nộp NN", AccountType.LIABILITY, "credit"),
        "334": Account("334", "Phải trả người lao động", AccountType.LIABILITY, "credit"),
        "338": Account("338", "Phải trả khác", AccountType.LIABILITY, "credit"),
        "411": Account("411", "Vốn đầu tư của chủ sở hữu", AccountType.EQUITY, "credit"),
        "414": Account("414", "Quỹ đầu tư phát triển", AccountType.EQUITY, "credit"),
        "418": Account("418", "Thặng dư vốn cổ phần", AccountType.EQUITY, "credit"),
        "511": Account("511", "Doanh thu bán hàng và cung cấp dịch vụ", AccountType.REVENUE, "credit"),
        "5111": Account("5111", "Doanh thu bán hàng hóa", AccountType.REVENUE, "credit"),
        "5112": Account("5112", "Doanh thu bán thành phẩm", AccountType.REVENUE, "credit"),
        "5113": Account("5113", "Doanh thu dịch vụ", AccountType.REVENUE, "credit"),
        "515": Account("515", "Doanh thu hoạt động tài chính", AccountType.REVENUE, "credit"),
        "5151": Account("5151", "Lãi tiền gửi", AccountType.REVENUE, "credit"),
        "5152": Account("5152", "Lãi chứng khoán kinh doanh", AccountType.REVENUE, "credit"),
        "635": Account("635", "Chi phí tài chính", AccountType.EXPENSE, "debit"),
        "6351": Account("6351", "Lãi vay phải trả", AccountType.EXPENSE, "debit"),
        "6352": Account("6352", "Chi phí tài chính khác", AccountType.EXPENSE, "debit"),
        "641": Account("641", "Chi phí bán hàng", AccountType.EXPENSE, "debit"),
        "642": Account("642", "Chi phí quản lý doanh nghiệp", AccountType.EXPENSE, "debit"),
        "711": Account("711", "Lợi nhuận khác", AccountType.REVENUE, "credit"),
        "8211": Account("8211", "Chi phí thuế TNDN hiện hành", AccountType.EXPENSE, "debit"),
        "8212": Account("8212", "Chi phí thuế TNDN hoãn lại", AccountType.EXPENSE, "debit"),
    }

    return AccountChart(accounts)