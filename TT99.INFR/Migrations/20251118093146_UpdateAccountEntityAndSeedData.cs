using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

#pragma warning disable CA1814 // Prefer jagged arrays over multidimensional

namespace TT99.INFR.Migrations
{
    /// <inheritdoc />
    public partial class UpdateAccountEntityAndSeedData : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "001");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "002");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "003");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "004");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "005");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "006");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "007");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "008");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "009");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "142");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "271");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "272");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "311");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "315");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "335");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "415");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "417");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "531");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "532");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "611");

            migrationBuilder.AddColumn<int>(
                name: "Level",
                table: "Accounts",
                type: "integer",
                nullable: false,
                defaultValue: 0);

            migrationBuilder.AddColumn<string>(
                name: "ParentAccountNumber",
                table: "Accounts",
                type: "character varying(20)",
                maxLength: 20,
                nullable: true);

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "111",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "112",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Tiền gửi không kỳ hạn", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "113",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "121",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "128",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "131",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "133",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "136",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "138",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "141",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "151",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "152",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "153",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "154",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "155",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Sản phẩm", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "156",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "157",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "171",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Giao dịch mua, bán lại trái phiếu chính phủ", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "211",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "213",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "214",
                columns: new[] { "Level", "ParentAccountNumber", "Type" },
                values: new object[] { 1, null, "Expense" });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "221",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Đầu tư vào công ty con", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "222",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Đầu tư vào công ty liên doanh, liên kết", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "241",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "242",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Chi phí chờ phân bổ", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "331",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Phải trả cho người bán", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "333",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Thuế và các khoản phải nộp Nhà nước", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "334",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Phải trả người lao động", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "336",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "337",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Thanh toán tiền theo hợp đồng xây dựng", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "338",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Phải trả, phải nộp khác", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "341",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Vay và nợ thuê tài chính", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "343",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "344",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Nhận ký quỹ, ký cược", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "411",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Vốn chủ sở hữu", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "412",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Chênh lệch đánh giá lại tài sản", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "413",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "414",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "418",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Các quỹ khác thuộc vốn chủ sở hữu", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "419",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Cổ phiếu mua lại của chính mình", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "421",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "511",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "515",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "521",
                columns: new[] { "Level", "ParentAccountNumber", "Type" },
                values: new object[] { 1, null, "Revenue" });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "621",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Chi phí nguyên liệu, vật liệu trực tiếp", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "622",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "623",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Chi phí sử dụng máy thi công", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "627",
                columns: new[] { "AccountName", "Level", "ParentAccountNumber" },
                values: new object[] { "Chi phí sản xuất chung", 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "632",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "635",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "641",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "642",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6421",
                columns: new[] { "AccountName", "IsSummaryAccount", "Level", "ParentAccountNumber" },
                values: new object[] { "Chi phí nhân viên quản lý", false, 2, "642" });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6422",
                columns: new[] { "AccountName", "IsSummaryAccount", "Level", "ParentAccountNumber" },
                values: new object[] { "Chi phí vật liệu văn phòng", false, 2, "642" });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "811",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "911",
                columns: new[] { "Level", "ParentAccountNumber" },
                values: new object[] { 1, null });

            migrationBuilder.InsertData(
                table: "Accounts",
                columns: new[] { "AccountNumber", "AccountName", "IsSummaryAccount", "Level", "ParentAccountNumber", "Type" },
                values: new object[,]
                {
                    { "1281", "Tiền gửi có kỳ hạn", false, 2, "128", "Asset" },
                    { "1282", "Trái phiếu", false, 2, "128", "Asset" },
                    { "1283", "Cho vay", false, 2, "128", "Asset" },
                    { "1288", "Các khoản đầu tư khác nắm giữ đến ngày đáo hạn", false, 2, "128", "Asset" },
                    { "1331", "Thuế GTGT được khấu trừ của hàng hóa, dịch vụ", false, 2, "133", "Asset" },
                    { "1332", "Thuế GTGT được khấu trừ của TSCĐ", false, 2, "133", "Asset" },
                    { "1361", "Vốn kinh doanh ở đơn vị trực thuộc", false, 2, "136", "Asset" },
                    { "1362", "Phải thu nội bộ về chênh lệch tỷ giá", false, 2, "136", "Asset" },
                    { "1363", "Phải thu nội bộ về chi phí đi vay đủ điều kiện được vốn hóa", false, 2, "136", "Asset" },
                    { "1368", "Phải thu nội bộ khác", false, 2, "136", "Asset" },
                    { "1381", "Tài sản thiếu chờ xử lý", false, 2, "138", "Asset" },
                    { "1388", "Phải thu khác", false, 2, "138", "Asset" },
                    { "158", "Nguyên liệu, vật tư tại kho bảo thuế", true, 1, null, "Asset" },
                    { "212", "Tài sản cố định thuê tài chính", true, 1, null, "Asset" },
                    { "2141", "Hao mòn TSCĐ hữu hình", false, 2, "214", "Expense" },
                    { "2142", "Hao mòn TSCĐ thuê tài chính", false, 2, "214", "Expense" },
                    { "2143", "Hao mòn TSCĐ vô hình", false, 2, "214", "Expense" },
                    { "2147", "Hao mòn BĐSĐT", false, 2, "214", "Expense" },
                    { "215", "Tài sản sinh học", true, 1, null, "Asset" },
                    { "2151", "Súc vật nuôi cho sản phẩm định kỳ", false, 2, "215", "Asset" },
                    { "21511", "Súc vật nuôi cho sản phẩm định kỳ chưa đạt đến giai đoạn trưởng thành", false, 3, "2151", "Asset" },
                    { "21512", "Súc vật nuôi cho sản phẩm định kỳ đạt đến giai đoạn trưởng thành", false, 3, "2151", "Asset" },
                    { "2152", "Súc vật nuôi lấy sản phẩm một lần", false, 2, "215", "Asset" },
                    { "21521", "Súc vật nuôi lấy sản phẩm một lần", false, 3, "2152", "Asset" },
                    { "2153", "Cây trồng theo mùa vụ hoặc lấy sản phẩm một lần", false, 2, "215", "Asset" },
                    { "217", "Bất động sản đầu tư", true, 1, null, "Asset" },
                    { "228", "Đầu tư khác", true, 1, null, "Asset" },
                    { "2281", "Đầu tư góp vốn vào đơn vị khác", false, 2, "228", "Asset" },
                    { "2282", "Đầu tư khác", false, 2, "228", "Asset" },
                    { "229", "Dự phòng tổn thất tài sản", true, 1, null, "Asset" },
                    { "2291", "Dự phòng giảm giá chứng khoán kinh doanh", false, 2, "229", "Asset" },
                    { "2292", "Dự phòng tổn thất đầu tư vào đơn vị khác", false, 2, "229", "Asset" },
                    { "2293", "Dự phòng tổn thất các khoản đầu tư tài chính khác", false, 2, "229", "Asset" },
                    { "2294", "Dự phòng giảm giá hàng tồn kho", false, 2, "229", "Asset" },
                    { "2295", "Dự phòng tổn thất tài sản sinh học", false, 2, "229", "Asset" },
                    { "2411", "Mua sắm TSCĐ", false, 2, "241", "Asset" },
                    { "2412", "Xây dựng cơ bản", false, 2, "241", "Asset" },
                    { "2413", "Sửa chữa, bảo dưỡng định kỳ TSCĐ", false, 2, "241", "Asset" },
                    { "2414", "Nâng cấp, cải tạo TSCĐ", false, 2, "241", "Asset" },
                    { "243", "Tài sản thuế thu nhập hoãn lại", true, 1, null, "Asset" },
                    { "244", "Ký quỹ, ký cược", true, 1, null, "Asset" },
                    { "332", "Phải trả cổ tức, lợi nhuận", true, 1, null, "Liability" },
                    { "3331", "Thuế GTGT phải nộp", false, 2, "333", "Liability" },
                    { "3332", "Thuế tiêu thụ đặc biệt", false, 2, "333", "Liability" },
                    { "3333", "Thuế xuất, nhập khẩu", false, 2, "333", "Liability" },
                    { "3334", "Thuế thu nhập doanh nghiệp", false, 2, "333", "Liability" },
                    { "3335", "Thuế thu nhập cá nhân", false, 2, "333", "Liability" },
                    { "3336", "Thuế tài nguyên", false, 2, "333", "Liability" },
                    { "3337", "Thuế đất, tiền thuê đất", false, 2, "333", "Liability" },
                    { "3338", "Thuế bảo vệ môi trường", false, 2, "333", "Liability" },
                    { "3339", "Phí, lệ phí và các khoản phải nộp khác", false, 2, "333", "Liability" },
                    { "3361", "Phải trả nội bộ về vốn kinh doanh", false, 2, "336", "Liability" },
                    { "3362", "Phải trả nội bộ về chênh lệch tỷ giá", false, 2, "336", "Liability" },
                    { "3363", "Phải trả nội bộ về chi phí đi vay đủ điều kiện được vốn hóa", false, 2, "336", "Liability" },
                    { "3368", "Phải trả nội bộ khác", false, 2, "336", "Liability" },
                    { "3381", "Tài sản thừa chờ giải quyết", false, 2, "338", "Liability" },
                    { "3382", "Kinh phí công đoàn", false, 2, "338", "Liability" },
                    { "3383", "Bảo hiểm xã hội", false, 2, "338", "Liability" },
                    { "3384", "Bảo hiểm y tế", false, 2, "338", "Liability" },
                    { "3385", "Bảo hiểm thất nghiệp", false, 2, "338", "Liability" },
                    { "3387", "Doanh thu chờ phân bổ", false, 2, "338", "Liability" },
                    { "3388", "Phải trả, phải nộp khác", false, 2, "338", "Liability" },
                    { "3411", "Các khoản vay", false, 2, "341", "Liability" },
                    { "3412", "Nợ thuê tài chính", false, 2, "341", "Liability" },
                    { "3431", "Trái phiếu thường", false, 2, "343", "Liability" },
                    { "3432", "Trái phiếu chuyển đổi", false, 2, "343", "Liability" },
                    { "347", "Thuế thu nhập hoãn lại phải trả", true, 1, null, "Liability" },
                    { "352", "Dự phòng phải trả", true, 1, null, "Liability" },
                    { "3521", "Dự phòng bảo hành sản phẩm, hàng hóa", false, 2, "352", "Liability" },
                    { "3522", "Dự phòng bảo hành công trình xây dựng", false, 2, "352", "Liability" },
                    { "3523", "Dự phòng tái cơ cấu doanh nghiệp", false, 2, "352", "Liability" },
                    { "3525", "Dự phòng phải trả khác", false, 2, "352", "Liability" },
                    { "353", "Quỹ khen thưởng, phúc lợi", true, 1, null, "Liability" },
                    { "3531", "Quỹ khen thưởng", false, 2, "353", "Liability" },
                    { "3532", "Quỹ phúc lợi", false, 2, "353", "Liability" },
                    { "3533", "Quỹ phúc lợi đã hình thành TSCĐ", false, 2, "353", "Liability" },
                    { "3534", "Quỹ phúc lợi quản lý điều hành công ty", false, 2, "353", "Liability" },
                    { "356", "Quỹ phát triển khoa học và công nghệ", true, 1, null, "Liability" },
                    { "3561", "Quỹ phát triển khoa học và công nghệ", false, 2, "356", "Liability" },
                    { "3562", "Quỹ phát triển khoa học và công nghệ đã hình thành tài sản", false, 2, "356", "Liability" },
                    { "357", "Quỹ bình ổn giá", true, 1, null, "Liability" },
                    { "4111", "Vốn góp của chủ sở hữu", false, 2, "411", "Equity" },
                    { "41111", "Vốn góp của chủ sở hữu phổ thông có quyền biểu quyết", false, 3, "4111", "Equity" },
                    { "41112", "Vốn góp khác", false, 3, "4111", "Equity" },
                    { "4112", "Thặng dư vốn", false, 2, "411", "Equity" },
                    { "4118", "Vốn khác", false, 2, "411", "Equity" },
                    { "4211", "Lợi nhuận sau thuế chưa phân phối lũy kế đến cuối năm trước", false, 2, "421", "Equity" },
                    { "4212", "Lợi nhuận sau thuế chưa phân phối năm nay", false, 2, "421", "Equity" },
                    { "6231", "Chi phí nhân công", false, 2, "623", "Expense" },
                    { "6232", "Chi phí vật liệu", false, 2, "623", "Expense" },
                    { "6233", "Chi phí dụng cụ sản xuất", false, 2, "623", "Expense" },
                    { "6234", "Chi phí dịch vụ mua ngoài", false, 2, "623", "Expense" },
                    { "6238", "Chi phí bằng tiền khác", false, 2, "623", "Expense" },
                    { "6271", "Chi phí nhân viên phân xưởng", false, 2, "627", "Expense" },
                    { "6272", "Chi phí vật liệu sản xuất", false, 2, "627", "Expense" },
                    { "6273", "Chi phí dụng cụ sản xuất", false, 2, "627", "Expense" },
                    { "6274", "Chi phí khấu hao TSCĐ", false, 2, "627", "Expense" },
                    { "6275", "Thuế, phí, lệ phí", false, 2, "627", "Expense" },
                    { "6277", "Chi phí dịch vụ mua ngoài", false, 2, "627", "Expense" },
                    { "6278", "Chi phí bằng tiền khác", false, 2, "627", "Expense" },
                    { "6411", "Chi phí nhân viên bán hàng", false, 2, "641", "Expense" },
                    { "6412", "Chi phí vật liệu, bao bì", false, 2, "641", "Expense" },
                    { "6413", "Chi phí dụng cụ, vật tư", false, 2, "641", "Expense" },
                    { "6414", "Chi phí khấu hao TSCĐ", false, 2, "641", "Expense" },
                    { "6415", "Thuế, phí, lệ phí", false, 2, "641", "Expense" },
                    { "6417", "Chi phí dịch vụ mua ngoài", false, 2, "641", "Expense" },
                    { "6418", "Chi phí bằng tiền khác", false, 2, "641", "Expense" },
                    { "6423", "Chi phí đồ dùng văn phòng", false, 2, "642", "Expense" },
                    { "6424", "Chi phí khấu hao TSCĐ", false, 2, "642", "Expense" },
                    { "6425", "Thuế, phí, lệ phí", false, 2, "642", "Expense" },
                    { "6426", "Chi phí dự phòng", false, 2, "642", "Expense" },
                    { "6427", "Chi phí dịch vụ mua ngoài", false, 2, "642", "Expense" },
                    { "6428", "Chi phí bằng tiền khác", false, 2, "642", "Expense" },
                    { "711", "Thu nhập khác", true, 1, null, "Revenue" },
                    { "821", "Chi phí thuế thu nhập doanh nghiệp", true, 1, null, "Expense" },
                    { "8211", "Chi phí thuế TNDN hiện hành", false, 2, "821", "Expense" },
                    { "8212", "Chi phí thuế TNDN hoãn lại", false, 2, "821", "Expense" }
                });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "1281");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "1282");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "1283");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "1288");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "1331");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "1332");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "1361");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "1362");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "1363");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "1368");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "1381");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "1388");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "158");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "212");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2141");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2142");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2143");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2147");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "215");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2151");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "21511");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "21512");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2152");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "21521");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2153");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "217");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "228");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2281");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2282");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "229");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2291");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2292");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2293");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2294");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2295");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2411");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2412");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2413");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "2414");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "243");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "244");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "332");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3331");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3332");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3333");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3334");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3335");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3336");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3337");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3338");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3339");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3361");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3362");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3363");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3368");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3381");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3382");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3383");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3384");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3385");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3387");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3388");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3411");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3412");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3431");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3432");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "347");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "352");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3521");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3522");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3523");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3525");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "353");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3531");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3532");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3533");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3534");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "356");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3561");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "3562");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "357");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "4111");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "41111");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "41112");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "4112");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "4118");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "4211");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "4212");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6231");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6232");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6233");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6234");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6238");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6271");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6272");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6273");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6274");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6275");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6277");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6278");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6411");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6412");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6413");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6414");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6415");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6417");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6418");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6423");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6424");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6425");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6426");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6427");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6428");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "711");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "821");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "8211");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "8212");

            migrationBuilder.DropColumn(
                name: "Level",
                table: "Accounts");

            migrationBuilder.DropColumn(
                name: "ParentAccountNumber",
                table: "Accounts");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "112",
                column: "AccountName",
                value: "Tiền gửi ngân hàng");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "155",
                column: "AccountName",
                value: "Thành phẩm");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "171",
                column: "AccountName",
                value: "Gửi giữ kinh doanh chứng khoán");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "214",
                column: "Type",
                value: "Asset");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "221",
                column: "AccountName",
                value: "Đầu tư vào công ty liên kết, liên doanh");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "222",
                column: "AccountName",
                value: "Đầu tư góp vốn vào đơn vị khác");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "242",
                column: "AccountName",
                value: "Bất động sản đầu tư dở dang");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "331",
                column: "AccountName",
                value: "Phải trả người lao động");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "333",
                column: "AccountName",
                value: "Thuế và các khoản phải nộp nhà nước");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "334",
                column: "AccountName",
                value: "Phải trả người mua");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "337",
                column: "AccountName",
                value: "Phải trả khách hàng");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "338",
                column: "AccountName",
                value: "Phải trả khác");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "341",
                column: "AccountName",
                value: "Vay dài hạn");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "344",
                column: "AccountName",
                value: "Nhận ký quỹ dài hạn");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "411",
                column: "AccountName",
                value: "Vốn đầu tư của chủ sở hữu");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "412",
                column: "AccountName",
                value: "Thặng dư vốn cổ phần");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "418",
                column: "AccountName",
                value: "Quỹ bình ổn giá");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "419",
                column: "AccountName",
                value: "Vốn góp của thành viên");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "521",
                column: "Type",
                value: "Expense");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "621",
                column: "AccountName",
                value: "Chi phí nguyên vật liệu trực tiếp");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "623",
                column: "AccountName",
                value: "Chi phí sản xuất chung");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "627",
                column: "AccountName",
                value: "Chi phí quản lý doanh nghiệp");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6421",
                columns: new[] { "AccountName", "IsSummaryAccount" },
                values: new object[] { "Chi phí tiền lương", true });

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6422",
                columns: new[] { "AccountName", "IsSummaryAccount" },
                values: new object[] { "Chi phí bảo hiểm, bảo hộ lao động", true });

            migrationBuilder.InsertData(
                table: "Accounts",
                columns: new[] { "AccountNumber", "AccountName", "IsSummaryAccount", "Type" },
                values: new object[,]
                {
                    { "001", "Tài sản thuê", true, "Other" },
                    { "002", "Vật tư, hàng hóa nhận giữ hộ", true, "Other" },
                    { "003", "Ký quỹ, ký cược", true, "Other" },
                    { "004", "Chứng từ, sổ sách kế toán đã xử lý", true, "Other" },
                    { "005", "Công cụ, dụng cụ không đủ tiêu chuẩn tài sản cố định", true, "Other" },
                    { "006", "Tài sản thiếu chờ xử lý", true, "Other" },
                    { "007", "Tài sản thừa chờ xử lý", true, "Other" },
                    { "008", "Nợ khó đòi đã xử lý", true, "Other" },
                    { "009", "Tài sản của đơn vị cấp trên giao", true, "Other" },
                    { "142", "Chi phí trả trước", true, "Asset" },
                    { "271", "Gửi giữ kinh doanh chứng khoán (dài hạn)", true, "Asset" },
                    { "272", "Ký quỹ, ký cược dài hạn", true, "Asset" },
                    { "311", "Phải trả cho người bán", true, "Liability" },
                    { "315", "Vay ngắn hạn", true, "Liability" },
                    { "335", "Chi phí phải trả", true, "Liability" },
                    { "415", "Quỹ hỗ trợ sắp xếp doanh nghiệp", true, "Equity" },
                    { "417", "Quỹ khen thưởng, phúc lợi", true, "Equity" },
                    { "531", "Hàng bán bị trả lại", true, "Expense" },
                    { "532", "Chiết khấu thương mại", true, "Expense" },
                    { "611", "Mua hàng (hàng hóa, nguyên vật liệu)", true, "Expense" }
                });
        }
    }
}
