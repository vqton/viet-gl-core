namespace AIErp.Infrastructure.SeedData;

using AIErp.Domain.Entities;
using AIErp.Domain.Enums;

public static class IdentitySeed
{
    public static List<Account> GetChartOfAccounts()
    {
        var accounts = new List<(string Code, string Name, AccountType Type, NormalBalance NormalBalance, bool IsDetail, string? ParentCode, bool IsSystem)>
        {
            // ============== TÀI SẢN NGẮN HẠN (1xx) ==============
            ("1", "TÀI SẢN NGẮN HẠN", AccountType.Asset, NormalBalance.Debit, false, null, true),

            // 111 - Tiền
            ("111", "Tiền", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1111", "Tiền Việt Nam", AccountType.Asset, NormalBalance.Debit, true, "111", true),
            ("1112", "Ngoại tệ", AccountType.Asset, NormalBalance.Debit, true, "111", true),
            ("1113", "Vàng kim loại, đá quý", AccountType.Asset, NormalBalance.Debit, true, "111", false),

            // 112 - Tiền gửi không kỳ hạn (TT99)
            ("112", "Tiền gửi không kỳ hạn", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1121", "Tiền Việt Nam", AccountType.Asset, NormalBalance.Debit, true, "112", true),
            ("1122", "Ngoại tệ", AccountType.Asset, NormalBalance.Debit, true, "112", true),

            // 121 - Chứng khoán kinh doanh
            ("121", "Chứng khoán kinh doanh", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1211", "Cổ phiếu", AccountType.Asset, NormalBalance.Debit, true, "121", false),
            ("1212", "Trái phiếu", AccountType.Asset, NormalBalance.Debit, true, "121", false),
            ("1213", "Chứng chỉ tiền gửi", AccountType.Asset, NormalBalance.Debit, true, "121", false),
            ("1218", "Chứng khoán kinh doanh khác", AccountType.Asset, NormalBalance.Debit, true, "121", false),

            // 128 - Tiền gửi có kỳ hạn
            ("128", "Tiền gửi có kỳ hạn", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1281", "Tiền gửi có kỳ hạn", AccountType.Asset, NormalBalance.Debit, true, "128", false),
            ("1282", "Ký quỹ có kỳ hạn", AccountType.Asset, NormalBalance.Debit, true, "128", false),
            ("1288", "Đầu tư khác có kỳ hạn", AccountType.Asset, NormalBalance.Debit, true, "128", false),

            // 131 - Phải thu của khách hàng
            ("131", "Phải thu của khách hàng", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1311", "Phải thu khách hàng", AccountType.Asset, NormalBalance.Debit, true, "131", true),
            ("1312", "Phải thu khách hàng là các bên liên quan", AccountType.Asset, NormalBalance.Debit, true, "131", false),

            // 133 - Thuế GTGT được khấu trừ
            ("133", "Thuế GTGT được khấu trừ", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1331", "Thuế GTGT được khấu trừ của hàng hóa, dịch vụ", AccountType.Asset, NormalBalance.Debit, true, "133", true),
            ("1332", "Thuế GTGT được khấu trừ của TSCĐ", AccountType.Asset, NormalBalance.Debit, true, "133", true),

            // 136 - Phải thu nội bộ
            ("136", "Phải thu nội bộ", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1361", "Phải thu nội bộ", AccountType.Asset, NormalBalance.Debit, true, "136", false),
            ("1362", "Phải thu nội bộ về chênh lệch giá", AccountType.Asset, NormalBalance.Debit, true, "136", false),
            ("1363", "Phải thu nội bộ là các bên liên quan", AccountType.Asset, NormalBalance.Debit, true, "136", false),

            // 138 - Phải thu khác
            ("138", "Phải thu khác", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1381", "Tạm ứng", AccountType.Asset, NormalBalance.Debit, true, "138", false),
            ("1385", "Phải thu về cổ phần hoàn lại", AccountType.Asset, NormalBalance.Debit, true, "138", false),
            ("1386", "Cổ tức và lợi nhuận phải thu", AccountType.Asset, NormalBalance.Debit, true, "138", false),
            ("1388", "Phải thu khác", AccountType.Asset, NormalBalance.Debit, true, "138", false),

            // 141 - Tạm ứng
            ("141", "Tạm ứng", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1411", "Tạm ứng", AccountType.Asset, NormalBalance.Debit, true, "141", false),
            ("1412", "Ký cược, ký quỹ", AccountType.Asset, NormalBalance.Debit, true, "141", false),
            ("1413", "Tạm ứng cho công nhân viên", AccountType.Asset, NormalBalance.Debit, true, "141", false),

            // 151 - Hàng mua đang đi đường
            ("151", "Hàng mua đang đi đường", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1511", "Nguyên liệu, vật liệu đang đi đường", AccountType.Asset, NormalBalance.Debit, true, "151", false),
            ("1512", "Hàng hóa đang đi đường", AccountType.Asset, NormalBalance.Debit, true, "151", false),

            // 152 - Nguyên liệu, vật liệu
            ("152", "Nguyên liệu, vật liệu", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1521", "Nguyên liệu, vật liệu", AccountType.Asset, NormalBalance.Debit, true, "152", false),
            ("1522", "Vật liệu phụ", AccountType.Asset, NormalBalance.Debit, true, "152", false),
            ("1523", "Nhiên liệu", AccountType.Asset, NormalBalance.Debit, true, "152", false),
            ("1524", "Phụ tùng, phụ kiện", AccountType.Asset, NormalBalance.Debit, true, "152", false),
            ("1528", "Vật liệu khác", AccountType.Asset, NormalBalance.Debit, true, "152", false),

            // 153 - Công cụ, dụng cụ
            ("153", "Công cụ, dụng cụ", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1531", "Công cụ, dụng cụ", AccountType.Asset, NormalBalance.Debit, true, "153", false),
            ("1532", "Vật rẻ tiền, mau hỏng", AccountType.Asset, NormalBalance.Debit, true, "153", false),
            ("1533", "Bao bì luân chuyển", AccountType.Asset, NormalBalance.Debit, true, "153", false),

            // 154 - Chi phí sản xuất kinh doanh dở dang
            ("154", "Chi phí sản xuất kinh doanh dở dang", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1541", "Chi phí sản xuất dở dang", AccountType.Asset, NormalBalance.Debit, true, "154", false),
            ("1542", "Chi phí sản xuất dở dang dịch vụ", AccountType.Asset, NormalBalance.Debit, true, "154", false),

            // 155 - Sản phẩm (TT99)
            ("155", "Sản phẩm", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1551", "Sản phẩm", AccountType.Asset, NormalBalance.Debit, true, "155", false),
            ("1552", "Sản phẩm đang gửi bán", AccountType.Asset, NormalBalance.Debit, true, "155", false),
            ("1553", "Sản phẩm bất động sản", AccountType.Asset, NormalBalance.Debit, true, "155", false),

            // 156 - Hàng hóa
            ("156", "Hàng hóa", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1561", "Hàng hóa", AccountType.Asset, NormalBalance.Debit, true, "156", false),
            ("1562", "Hàng hóa đang gửi bán", AccountType.Asset, NormalBalance.Debit, true, "156", false),
            ("1567", "Hàng hóa bất động sản", AccountType.Asset, NormalBalance.Debit, true, "156", false),

            // 157 - Hàng gửi bán
            ("157", "Hàng gửi bán", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1571", "Hàng gửi bán", AccountType.Asset, NormalBalance.Debit, true, "157", false),
            ("1572", "Hàng gửi đại lý", AccountType.Asset, NormalBalance.Debit, true, "157", false),
            ("1573", "Hàng gửi gia công chế biến", AccountType.Asset, NormalBalance.Debit, true, "157", false),

            // 158 - Hàng hóa kho bảo thuế
            ("158", "Hàng hóa kho bảo thuế", AccountType.Asset, NormalBalance.Debit, false, "1", true),
            ("1581", "Hàng hóa kho bảo thuế nội địa", AccountType.Asset, NormalBalance.Debit, true, "158", false),
            ("1588", "Hàng hóa kho bảo thuế khác", AccountType.Asset, NormalBalance.Debit, true, "158", false),

            // ============== TÀI SẢN DÀI HẠN (2xx) ==============
            ("2", "TÀI SẢN DÀI HẠN", AccountType.Asset, NormalBalance.Debit, false, null, true),

            // 211 - Tài sản cố định hữu hình
            ("211", "Tài sản cố định hữu hình", AccountType.Asset, NormalBalance.Debit, false, "2", true),
            ("2111", "TSCĐ hữu hình", AccountType.Asset, NormalBalance.Debit, true, "211", false),
            ("2112", "TSCĐ thuê tài chính", AccountType.Asset, NormalBalance.Debit, true, "211", false),
            ("2113", "TSCĐ vô hình", AccountType.Asset, NormalBalance.Debit, true, "211", false),
            ("2118", "TSCĐ khác", AccountType.Asset, NormalBalance.Debit, true, "211", false),

            // 213 - Tài sản cố định vô hình
            ("213", "Tài sản cố định vô hình", AccountType.Asset, NormalBalance.Debit, false, "2", true),
            ("2131", "Quyền sử dụng đất", AccountType.Asset, NormalBalance.Debit, true, "213", false),
            ("2132", "Quyền phát minh, sáng chế", AccountType.Asset, NormalBalance.Debit, true, "213", false),
            ("2133", "Bản quyền, kiểu dáng công nghiệp, nhãn hiệu hàng hóa", AccountType.Asset, NormalBalance.Debit, true, "213", false),
            ("2134", "Phần mềm máy tính", AccountType.Asset, NormalBalance.Debit, true, "213", false),
            ("2135", "TSCĐ vô hình khác", AccountType.Asset, NormalBalance.Debit, true, "213", false),
            ("2138", "Chi phí tài sản cố định vô hình", AccountType.Asset, NormalBalance.Debit, true, "213", false),

            // 214 - Hao mòn và khấu hao TSCĐ
            ("214", "Hao mòn và khấu hao TSCĐ", AccountType.Asset, NormalBalance.Credit, false, "2", true),
            ("2141", "Hao mòn TSCĐ hữu hình", AccountType.Asset, NormalBalance.Credit, true, "214", false),
            ("2142", "Hao mòn TSCĐ thuê tài chính", AccountType.Asset, NormalBalance.Credit, true, "214", false),
            ("2143", "Hao mòn TSCĐ vô hình", AccountType.Asset, NormalBalance.Credit, true, "214", false),
            ("2147", "Hao mòn bất động sản đầu tư", AccountType.Asset, NormalBalance.Credit, true, "214", false),

            // 217 - Bất động sản đầu tư
            ("217", "Bất động sản đầu tư", AccountType.Asset, NormalBalance.Debit, false, "2", true),
            ("2171", "Nhà cửa, vật kiến trúc", AccountType.Asset, NormalBalance.Debit, true, "217", false),
            ("2172", "Quyền sử dụng đất", AccountType.Asset, NormalBalance.Debit, true, "217", false),
            ("2173", "Cây cấy, súc vật làm việc và cho sản phẩm", AccountType.Asset, NormalBalance.Debit, true, "217", false),
            ("2178", "Bất động sản đầu tư khác", AccountType.Asset, NormalBalance.Debit, true, "217", false),

            // 221 - Đầu tư vào công ty con
            ("221", "Đầu tư vào công ty con", AccountType.Asset, NormalBalance.Debit, false, "2", true),
            ("2211", "Đầu tư vào công ty con", AccountType.Asset, NormalBalance.Debit, true, "221", false),

            // 222 - Đầu tư vào công ty liên kết
            ("222", "Đầu tư vào công ty liên kết", AccountType.Asset, NormalBalance.Debit, false, "2", true),
            ("2221", "Đầu tư vào công ty liên kết", AccountType.Asset, NormalBalance.Debit, true, "222", false),

            // 228 - Đầu tư khác
            ("228", "Đầu tư khác", AccountType.Asset, NormalBalance.Debit, false, "2", true),
            ("2281", "Đầu tư cổ phiếu", AccountType.Asset, NormalBalance.Debit, true, "228", false),
            ("2282", "Đầu tư trái phiếu", AccountType.Asset, NormalBalance.Debit, true, "228", false),
            ("2288", "Đầu tư khác", AccountType.Asset, NormalBalance.Debit, true, "228", false),

            // 241 - Xây dựng cơ bản dở dang
            ("241", "Xây dựng cơ bản dở dang", AccountType.Asset, NormalBalance.Debit, false, "2", true),
            ("2411", "Mua sắm TSCĐ", AccountType.Asset, NormalBalance.Debit, true, "241", false),
            ("2412", "Xây dựng cơ bản", AccountType.Asset, NormalBalance.Debit, true, "241", false),
            ("2413", "Sửa chữa TSCĐ", AccountType.Asset, NormalBalance.Debit, true, "241", false),

            // 242 - Chi phí trả trước dài hạn
            ("242", "Chi phí trả trước dài hạn", AccountType.Asset, NormalBalance.Debit, false, "2", true),
            ("2421", "Chi phí trả trước", AccountType.Asset, NormalBalance.Debit, true, "242", false),
            ("2422", "Ký quỹ dài hạn", AccountType.Asset, NormalBalance.Debit, true, "242", false),

            // 244 - Chênh lệch tỷ giá hối đoái
            ("244", "Chênh lệch tỷ giá hối đoái", AccountType.Asset, NormalBalance.Debit, false, "2", true),
            ("2441", "Chênh lệch tỷ giá hối đoái", AccountType.Asset, NormalBalance.Debit, true, "244", false),

            // 251 - Tài sản thuế thu nhập hoãn lại
            ("251", "Tài sản thuế thu nhập hoãn lại", AccountType.Asset, NormalBalance.Debit, false, "2", true),
            ("2511", "Tài sản thuế thu nhập hoãn lại", AccountType.Asset, NormalBalance.Debit, true, "251", false),

            // ============== NGUỒN VỐN (3xx) ==============
            ("3", "NGUỒN VỐN", AccountType.Liability, NormalBalance.Credit, false, null, true),

            // 311 - Phải trả người bán
            ("311", "Phải trả người bán", AccountType.Liability, NormalBalance.Credit, false, "3", true),
            ("3111", "Phải trả người bán", AccountType.Liability, NormalBalance.Credit, true, "311", false),
            ("3112", "Phải trả người bán là các bên liên quan", AccountType.Liability, NormalBalance.Credit, true, "311", false),

            // 312 - Người mua trả tiền trước
            ("312", "Người mua trả tiền trước", AccountType.Liability, NormalBalance.Credit, false, "3", true),
            ("3121", "Người mua trả tiền trước", AccountType.Liability, NormalBalance.Credit, true, "312", false),
            ("3122", "Người mua trả tiền trước là các bên liên quan", AccountType.Liability, NormalBalance.Credit, true, "312", false),

            // 313 - Thuế và các khoản phải nộp Nhà nước (TT99)
            ("313", "Thuế và các khoản phải nộp Nhà nước", AccountType.Liability, NormalBalance.Credit, false, "3", true),
            ("3131", "Thuế GTGT đầu ra", AccountType.Liability, NormalBalance.Credit, true, "313", true),
            ("3132", "Thuế tiêu thụ đặc biệt", AccountType.Liability, NormalBalance.Credit, true, "313", true),
            ("3133", "Thuế xuất, nhập khẩu", AccountType.Liability, NormalBalance.Credit, true, "313", true),
            ("3134", "Thuế thu nhập doanh nghiệp", AccountType.Liability, NormalBalance.Credit, true, "313", true),
            ("3135", "Thuế thu nhập cá nhân", AccountType.Liability, NormalBalance.Credit, true, "313", true),
            ("3136", "Thuế tài nguyên", AccountType.Liability, NormalBalance.Credit, true, "313", true),
            ("3137", "Thuế nhà đất, tiền thuê đất", AccountType.Liability, NormalBalance.Credit, true, "313", true),
            ("3138", "Thuế, phí, lệ phí khác", AccountType.Liability, NormalBalance.Credit, true, "313", true),
            ("3139", "Thuế giá trị gia tăng được khấu trừ", AccountType.Liability, NormalBalance.Credit, true, "313", true),

            // 314 - Phải trả người lao động
            ("314", "Phải trả người lao động", AccountType.Liability, NormalBalance.Credit, false, "3", true),
            ("3141", "Phải trả người lao động", AccountType.Liability, NormalBalance.Credit, true, "314", false),
            ("3142", "Phải trả thu nhập người lao động", AccountType.Liability, NormalBalance.Credit, true, "314", false),
            ("3143", "Phải trả bảo hiểm xã hội", AccountType.Liability, NormalBalance.Credit, true, "314", false),
            ("3144", "Phải trả bảo hiểm y tế", AccountType.Liability, NormalBalance.Credit, true, "314", false),
            ("3145", "Phải trả kinh phí công đoàn", AccountType.Liability, NormalBalance.Credit, true, "314", false),

            // 315 - Chi phí phải trả
            ("315", "Chi phí phải trả", AccountType.Liability, NormalBalance.Credit, false, "3", true),
            ("3151", "Chi phí lãi vay phải trả", AccountType.Liability, NormalBalance.Credit, true, "315", false),
            ("3158", "Chi phí phải trả khác", AccountType.Liability, NormalBalance.Credit, true, "315", false),

            // 316 - Phải trả nội bộ
            ("316", "Phải trả nội bộ", AccountType.Liability, NormalBalance.Credit, false, "3", true),
            ("3161", "Phải trả nội bộ", AccountType.Liability, NormalBalance.Credit, true, "316", false),
            ("3162", "Phải trả nội bộ về chênh lệch giá", AccountType.Liability, NormalBalance.Credit, true, "316", false),
            ("3163", "Phải trả nội bộ là các bên liên quan", AccountType.Liability, NormalBalance.Credit, true, "316", false),

            // 317 - Phải trả khác
            ("317", "Phải trả khác", AccountType.Liability, NormalBalance.Credit, false, "3", true),
            ("3171", "Ký cược, ký quỹ", AccountType.Liability, NormalBalance.Credit, true, "317", false),
            ("3172", "Nhận ký quỹ, ký cược ngắn hạn", AccountType.Liability, NormalBalance.Credit, true, "317", false),
            ("3173", "Nhận ký quỹ, ký cược dài hạn", AccountType.Liability, NormalBalance.Credit, true, "317", false),
            ("3178", "Phải trả khác", AccountType.Liability, NormalBalance.Credit, true, "317", false),

            // 318 - Vay và nợ thuê tài chính
            ("318", "Vay và nợ thuê tài chính", AccountType.Liability, NormalBalance.Credit, false, "3", true),
            ("3181", "Vay ngắn hạn", AccountType.Liability, NormalBalance.Credit, true, "318", false),
            ("3182", "Vay dài hạn", AccountType.Liability, NormalBalance.Credit, true, "318", false),
            ("3183", "Nợ thuê tài chính", AccountType.Liability, NormalBalance.Credit, true, "318", false),

            // 319 - Dự phòng phải trả
            ("319", "Dự phòng phải trả", AccountType.Liability, NormalBalance.Credit, false, "3", true),
            ("3191", "Dự phòng bảo hành sản phẩm, hàng hóa", AccountType.Liability, NormalBalance.Credit, true, "319", false),
            ("3192", "Dự phòng tái cơ cấu", AccountType.Liability, NormalBalance.Credit, true, "319", false),
            ("3193", "Dự phòng phải trả khác", AccountType.Liability, NormalBalance.Credit, true, "319", false),

            // 320 - Doanh thu chưa thực hiện
            ("320", "Doanh thu chưa thực hiện", AccountType.Liability, NormalBalance.Credit, false, "3", true),
            ("3201", "Doanh thu chưa thực hiện", AccountType.Liability, NormalBalance.Credit, true, "320", false),
            ("3202", "Doanh thu nhận trước ngắn hạn", AccountType.Liability, NormalBalance.Credit, true, "320", false),
            ("3203", "Doanh thu nhận trước dài hạn", AccountType.Liability, NormalBalance.Credit, true, "320", false),

            // 321 - Chênh lệch tỷ giá hối đoái
            ("321", "Chênh lệch tỷ giá hối đoái", AccountType.Liability, NormalBalance.Credit, false, "3", true),
            ("3211", "Chênh lệch tỷ giá hối đoái", AccountType.Liability, NormalBalance.Credit, true, "321", false),

            // 322 - Thuế thu nhập hoãn lại phải trả
            ("322", "Thuế thu nhập hoãn lại phải trả", AccountType.Liability, NormalBalance.Credit, false, "3", true),
            ("3221", "Thuế thu nhập hoãn lại phải trả", AccountType.Liability, NormalBalance.Credit, true, "322", false),

            // 331 - Quỹ của doanh nghiệp
            ("331", "Quỹ của doanh nghiệp", AccountType.Equity, NormalBalance.Credit, false, "3", true),
            ("3311", "Quỹ đầu tư phát triển", AccountType.Equity, NormalBalance.Credit, true, "331", false),
            ("3312", "Quỹ hỗ trợ sắp xếp doanh nghiệp", AccountType.Equity, NormalBalance.Credit, true, "331", false),
            ("3313", "Quỹ khác thuộc vốn chủ sở hữu", AccountType.Equity, NormalBalance.Credit, true, "331", false),

            // 333 - Phải trả cổ tức, lợi nhuận (TT99)
            ("333", "Phải trả cổ tức, lợi nhuận", AccountType.Liability, NormalBalance.Credit, false, "3", true),
            ("3331", "Phải trả cổ tức", AccountType.Liability, NormalBalance.Credit, true, "333", true),
            ("3332", "Phải trả lợi nhuận", AccountType.Liability, NormalBalance.Credit, true, "333", true),
            ("3333", "Phải trả cổ tức, lợi nhuận cho các bên liên quan", AccountType.Liability, NormalBalance.Credit, true, "333", false),

            // 411 - Vốn đầu tư của chủ sở hữu (TT99)
            ("411", "Vốn đầu tư của chủ sở hữu", AccountType.Equity, NormalBalance.Credit, false, "3", true),
            ("4111", "Vốn đầu tư của chủ sở hữu", AccountType.Equity, NormalBalance.Credit, true, "411", true),
            ("4112", "Thặng dư vốn cổ phần", AccountType.Equity, NormalBalance.Credit, true, "411", true),
            ("4113", "Vốn khác của chủ sở hữu", AccountType.Equity, NormalBalance.Credit, true, "411", false),
            ("4115", "Cổ phiếu quỹ", AccountType.Equity, NormalBalance.Debit, true, "411", true),
            ("4118", "Chênh lệch đánh giá tài sản", AccountType.Equity, NormalBalance.Credit, true, "411", true),

            // 412 - Chênh lệch tỷ giá hối đoái
            ("412", "Chênh lệch tỷ giá hối đoái", AccountType.Equity, NormalBalance.Credit, false, "3", true),
            ("4121", "Chênh lệch tỷ giá hối đoái", AccountType.Equity, NormalBalance.Credit, true, "412", false),

            // 413 - Chênh lệch đánh giá lại tài sản
            ("413", "Chênh lệch đánh giá lại tài sản", AccountType.Equity, NormalBalance.Credit, false, "3", true),
            ("4131", "Chênh lệch đánh giá lại tài sản", AccountType.Equity, NormalBalance.Credit, true, "413", false),
            ("4132", "Chênh lệch đánh giá lại các khoản đầu tư", AccountType.Equity, NormalBalance.Credit, true, "413", false),

            // 421 - Lợi nhuận sau thuế chưa phân phối (TT99)
            ("421", "Lợi nhuận sau thuế chưa phân phối", AccountType.Equity, NormalBalance.Credit, false, "3", true),
            ("4211", "Lợi nhuận sau thuế chưa phân phối", AccountType.Equity, NormalBalance.Credit, true, "421", true),
            ("4212", "Lợi nhuận các năm trước", AccountType.Equity, NormalBalance.Credit, true, "421", true),

            // ============== DOANH THU (5xx) ==============
            ("5", "DOANH THU", AccountType.Revenue, NormalBalance.Credit, false, null, true),

            // 511 - Doanh thu bán hàng (TT99)
            ("511", "Doanh thu bán hàng", AccountType.Revenue, NormalBalance.Credit, false, "5", true),
            ("5111", "Doanh thu bán hàng hóa", AccountType.Revenue, NormalBalance.Credit, true, "511", true),
            ("5112", "Doanh thu bán sản phẩm", AccountType.Revenue, NormalBalance.Credit, true, "511", true),
            ("5113", "Doanh thu cung cấp dịch vụ", AccountType.Revenue, NormalBalance.Credit, true, "511", true),
            ("5114", "Doanh thu trợ cấp, tài trợ", AccountType.Revenue, NormalBalance.Credit, true, "511", false),
            ("5117", "Doanh thu khác", AccountType.Revenue, NormalBalance.Credit, true, "511", false),
            ("5118", "Hàng bán bị trả lại", AccountType.Revenue, NormalBalance.Debit, true, "511", true),
            ("5119", "Chiết khấu thương mại", AccountType.Revenue, NormalBalance.Debit, true, "511", true),

            // 515 - Doanh thu tài chính
            ("515", "Doanh thu tài chính", AccountType.Revenue, NormalBalance.Credit, false, "5", true),
            ("5151", "Lãi tiền gửi, lãi cho vay", AccountType.Revenue, NormalBalance.Credit, true, "515", false),
            ("5152", "Lãi chênh lệch tỷ giá", AccountType.Revenue, NormalBalance.Credit, true, "515", false),
            ("5153", "Lãi từ bán các khoản đầu tư", AccountType.Revenue, NormalBalance.Credit, true, "515", false),
            ("5154", "Doanh thu từ hoạt động đầu tư khác", AccountType.Revenue, NormalBalance.Credit, true, "515", false),

            // 516 - Doanh thu hoạt động khác
            ("516", "Doanh thu hoạt động khác", AccountType.Revenue, NormalBalance.Credit, false, "5", true),
            ("5161", "Thanh lý, nhượng bán tài sản cố định", AccountType.Revenue, NormalBalance.Credit, true, "516", false),
            ("5162", "Thu nhập từ hoạt động khác", AccountType.Revenue, NormalBalance.Credit, true, "516", false),

            // ============== CHI PHÍ (6xx) ==============
            ("6", "CHI PHÍ", AccountType.Expense, NormalBalance.Debit, false, null, true),

            // 611 - Mua hàng
            ("611", "Mua hàng", AccountType.Expense, NormalBalance.Debit, false, "6", true),
            ("6111", "Mua nguyên liệu, vật liệu", AccountType.Expense, NormalBalance.Debit, true, "611", false),
            ("6112", "Mua hàng hóa", AccountType.Expense, NormalBalance.Debit, true, "611", false),

            // 621 - Chi phí nguyên liệu, vật liệu trực tiếp
            ("621", "Chi phí nguyên liệu, vật liệu trực tiếp", AccountType.Expense, NormalBalance.Debit, false, "6", true),
            ("6211", "Chi phí nguyên liệu, vật liệu trực tiếp", AccountType.Expense, NormalBalance.Debit, true, "621", false),

            // 622 - Chi phí nhân công trực tiếp
            ("622", "Chi phí nhân công trực tiếp", AccountType.Expense, NormalBalance.Debit, false, "6", true),
            ("6221", "Chi phí nhân công trực tiếp", AccountType.Expense, NormalBalance.Debit, true, "622", false),

            // 623 - Chi phí sử dụng máy thi công
            ("623", "Chi phí sử dụng máy thi công", AccountType.Expense, NormalBalance.Debit, false, "6", true),
            ("6231", "Chi phí nhân viên điều khiển máy", AccountType.Expense, NormalBalance.Debit, true, "623", false),
            ("6232", "Chi phí nhiên liệu, vật liệu", AccountType.Expense, NormalBalance.Debit, true, "623", false),
            ("6233", "Chi phí khấu hao máy thi công", AccountType.Expense, NormalBalance.Debit, true, "623", false),
            ("6234", "Chi phí sửa chữa máy thi công", AccountType.Expense, NormalBalance.Debit, true, "623", false),
            ("6238", "Chi phí khác bằng tiền", AccountType.Expense, NormalBalance.Debit, true, "623", false),

            // 627 - Chi phí sản xuất chung
            ("627", "Chi phí sản xuất chung", AccountType.Expense, NormalBalance.Debit, false, "6", true),
            ("6271", "Chi phí nhân viên phân xưởng", AccountType.Expense, NormalBalance.Debit, true, "627", false),
            ("6272", "Chi phí vật liệu", AccountType.Expense, NormalBalance.Debit, true, "627", false),
            ("6273", "Chi phí công cụ, dụng cụ", AccountType.Expense, NormalBalance.Debit, true, "627", false),
            ("6274", "Chi phí khấu hao TSCĐ", AccountType.Expense, NormalBalance.Debit, true, "627", false),
            ("6275", "Chi phí bảo hành sản phẩm", AccountType.Expense, NormalBalance.Debit, true, "627", false),
            ("6276", "Chi phí dịch vụ mua ngoài", AccountType.Expense, NormalBalance.Debit, true, "627", false),
            ("6277", "Chi phí bằng tiền khác", AccountType.Expense, NormalBalance.Debit, true, "627", false),

            // 632 - Giá vốn hàng bán
            ("632", "Giá vốn hàng bán", AccountType.Expense, NormalBalance.Debit, false, "6", true),
            ("6321", "Giá vốn hàng hóa đã bán", AccountType.Expense, NormalBalance.Debit, true, "632", false),
            ("6322", "Giá vốn sản phẩm đã bán", AccountType.Expense, NormalBalance.Debit, true, "632", false),
            ("6323", "Giá vốn dịch vụ đã cung cấp", AccountType.Expense, NormalBalance.Debit, true, "632", false),
            ("6324", "Hàng bán bị trả lại giá vốn", AccountType.Expense, NormalBalance.Debit, true, "632", false),
            ("6325", "Chiết khấu thương mại giá vốn", AccountType.Expense, NormalBalance.Debit, true, "632", false),

            // 635 - Chi phí tài chính
            ("635", "Chi phí tài chính", AccountType.Expense, NormalBalance.Debit, false, "6", true),
            ("6351", "Lãi tiền vay", AccountType.Expense, NormalBalance.Debit, true, "635", false),
            ("6352", "Lỗ chênh lệch tỷ giá", AccountType.Expense, NormalBalance.Debit, true, "635", false),
            ("6353", "Chi phí giao dịch chứng khoán", AccountType.Expense, NormalBalance.Debit, true, "635", false),
            ("6354", "Lỗ từ bán các khoản đầu tư", AccountType.Expense, NormalBalance.Debit, true, "635", false),
            ("6358", "Chi phí tài chính khác", AccountType.Expense, NormalBalance.Debit, true, "635", false),

            // 641 - Chi phí bán hàng
            ("641", "Chi phí bán hàng", AccountType.Expense, NormalBalance.Debit, false, "6", true),
            ("6411", "Chi phí nhân viên", AccountType.Expense, NormalBalance.Debit, true, "641", false),
            ("6412", "Chi phí vật liệu, bao bì", AccountType.Expense, NormalBalance.Debit, true, "641", false),
            ("6413", "Chi phí công cụ, dụng cụ", AccountType.Expense, NormalBalance.Debit, true, "641", false),
            ("6414", "Chi phí khấu hao TSCĐ", AccountType.Expense, NormalBalance.Debit, true, "641", false),
            ("6415", "Chi phí bảo hành", AccountType.Expense, NormalBalance.Debit, true, "641", false),
            ("6416", "Chi phí quảng cáo, giới thiệu, tiếp thị", AccountType.Expense, NormalBalance.Debit, true, "641", false),
            ("6417", "Chi phí dịch vụ mua ngoài", AccountType.Expense, NormalBalance.Debit, true, "641", false),
            ("6418", "Chi phí khác", AccountType.Expense, NormalBalance.Debit, true, "641", false),

            // 642 - Chi phí quản lý doanh nghiệp
            ("642", "Chi phí quản lý doanh nghiệp", AccountType.Expense, NormalBalance.Debit, false, "6", true),
            ("6421", "Chi phí nhân viên quản lý", AccountType.Expense, NormalBalance.Debit, true, "642", false),
            ("6422", "Chi phí vật liệu quản lý", AccountType.Expense, NormalBalance.Debit, true, "642", false),
            ("6423", "Chi phí công cụ, dụng cụ", AccountType.Expense, NormalBalance.Debit, true, "642", false),
            ("6424", "Chi phí khấu hao TSCĐ", AccountType.Expense, NormalBalance.Debit, true, "642", false),
            ("6425", "Thuế, phí và lệ phí", AccountType.Expense, NormalBalance.Debit, true, "642", false),
            ("6426", "Chi phí dự phòng", AccountType.Expense, NormalBalance.Debit, true, "642", false),
            ("6427", "Chi phí dịch vụ mua ngoài", AccountType.Expense, NormalBalance.Debit, true, "642", false),
            ("6428", "Chi phí khác", AccountType.Expense, NormalBalance.Debit, true, "642", false),

            // 643 - Chi phí hoạt động khác
            ("643", "Chi phí hoạt động khác", AccountType.Expense, NormalBalance.Debit, false, "6", true),
            ("6431", "Thanh lý, nhượng bán TSCĐ", AccountType.Expense, NormalBalance.Debit, true, "643", false),
            ("6432", "Chi phí hoạt động khác", AccountType.Expense, NormalBalance.Debit, true, "643", false),

            // 644 - Chi phí thuế thu nhập doanh nghiệp
            ("644", "Chi phí thuế thu nhập doanh nghiệp", AccountType.Expense, NormalBalance.Debit, false, "6", true),
            ("6441", "Chi phí thuế TNDN hiện hành", AccountType.Expense, NormalBalance.Debit, true, "644", false),
            ("6442", "Chi phí thuế TNDN hoãn lại", AccountType.Expense, NormalBalance.Debit, true, "644", false),

            // ============== TÀI KHOẢN XÁC ĐỊNH KẾT QUẢ (9xx) ==============
            ("9", "XÁC ĐỊNH KẾT QUẢ", AccountType.Expense, NormalBalance.Debit, false, null, true),
            ("911", "Xác định kết quả kinh doanh", AccountType.Expense, NormalBalance.Debit, false, "9", true),
        };

        var system = "SYSTEM";
        var codeToAccount = new Dictionary<string, Account>();

        foreach (var (code, name, type, normalBalance, isDetail, parentCode, isSystem) in accounts)
        {
            var parentId = parentCode != null && codeToAccount.TryGetValue(parentCode, out var parent) ? parent.Id : (Guid?)null;

            var account = Account.Create(
                code: code,
                name: name,
                type: type,
                normalBalance: normalBalance,
                isDetail: isDetail,
                parentId: parentId,
                createdBy: system,
                isSystem: isSystem
            );

            codeToAccount[code] = account;
        }

        return codeToAccount.Values.ToList();
    }

    public static List<FiscalPeriod> GetFiscalPeriods()
    {
        var periods = new List<FiscalPeriod>();
        var now = DateTime.UtcNow;
        var system = "SYSTEM";

        var year = now.Year;
        for (int period = 1; period <= 12; period++)
        {
            var startDate = new DateOnly(year, period, 1);
            var endDate = startDate.AddMonths(1).AddDays(-1);

            var isOpen = period <= now.Month && year == now.Year;

            var fiscalPeriod = FiscalPeriod.Create(
                year: year,
                period: period,
                startDate: startDate,
                endDate: endDate,
                createdBy: system,
                isAdjustmentPeriod: false
            );

            if (isOpen)
            {
                fiscalPeriod.Open(system);
            }

            periods.Add(fiscalPeriod);
        }

        return periods;
    }
}
