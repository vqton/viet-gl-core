using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

#pragma warning disable CA1814 // Prefer jagged arrays over multidimensional

namespace TT99.INFR.Migrations
{
    /// <inheritdoc />
    public partial class SeedInitialChartOfAccountsTT99 : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "112",
                column: "AccountName",
                value: "Tiền gửi ngân hàng");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "211",
                column: "AccountName",
                value: "Tài sản cố định hữu hình");

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
                keyValue: "511",
                column: "AccountName",
                value: "Doanh thu bán hàng và cung cấp dịch vụ");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "621",
                column: "AccountName",
                value: "Chi phí nguyên vật liệu trực tiếp");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "642",
                column: "AccountName",
                value: "Chi phí quản lý doanh nghiệp");

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
                    { "113", "Tiền đang chuyển", true, "Asset" },
                    { "121", "Chứng khoán kinh doanh", true, "Asset" },
                    { "128", "Đầu tư nắm giữ đến ngày đáo hạn", true, "Asset" },
                    { "133", "Thuế GTGT được khấu trừ", true, "Asset" },
                    { "136", "Phải thu nội bộ", true, "Asset" },
                    { "138", "Phải thu khác", true, "Asset" },
                    { "141", "Tạm ứng", true, "Asset" },
                    { "142", "Chi phí trả trước", true, "Asset" },
                    { "151", "Hàng mua đang đi đường", true, "Asset" },
                    { "153", "Công cụ, dụng cụ", true, "Asset" },
                    { "154", "Chi phí sản xuất, kinh doanh dở dang", true, "Asset" },
                    { "155", "Thành phẩm", true, "Asset" },
                    { "156", "Hàng hóa", true, "Asset" },
                    { "157", "Hàng gửi đi bán", true, "Asset" },
                    { "171", "Gửi giữ kinh doanh chứng khoán", true, "Asset" },
                    { "213", "Tài sản cố định vô hình", true, "Asset" },
                    { "214", "Hao mòn tài sản cố định", true, "Asset" },
                    { "221", "Đầu tư vào công ty liên kết, liên doanh", true, "Asset" },
                    { "222", "Đầu tư góp vốn vào đơn vị khác", true, "Asset" },
                    { "241", "Xây dựng cơ bản dở dang", true, "Asset" },
                    { "242", "Bất động sản đầu tư dở dang", true, "Asset" },
                    { "271", "Gửi giữ kinh doanh chứng khoán (dài hạn)", true, "Asset" },
                    { "272", "Ký quỹ, ký cược dài hạn", true, "Asset" },
                    { "311", "Phải trả cho người bán", true, "Liability" },
                    { "315", "Vay ngắn hạn", true, "Liability" },
                    { "335", "Chi phí phải trả", true, "Liability" },
                    { "336", "Phải trả nội bộ", true, "Liability" },
                    { "337", "Phải trả khách hàng", true, "Liability" },
                    { "338", "Phải trả khác", true, "Liability" },
                    { "341", "Vay dài hạn", true, "Liability" },
                    { "343", "Trái phiếu phát hành", true, "Liability" },
                    { "344", "Nhận ký quỹ dài hạn", true, "Liability" },
                    { "412", "Thặng dư vốn cổ phần", true, "Equity" },
                    { "413", "Chênh lệch tỷ giá hối đoái", true, "Equity" },
                    { "414", "Quỹ đầu tư phát triển", true, "Equity" },
                    { "415", "Quỹ hỗ trợ sắp xếp doanh nghiệp", true, "Equity" },
                    { "417", "Quỹ khen thưởng, phúc lợi", true, "Equity" },
                    { "418", "Quỹ bình ổn giá", true, "Equity" },
                    { "419", "Vốn góp của thành viên", true, "Equity" },
                    { "421", "Lợi nhuận sau thuế chưa phân phối", true, "Equity" },
                    { "515", "Doanh thu hoạt động tài chính", true, "Revenue" },
                    { "521", "Các khoản giảm trừ doanh thu", true, "Expense" },
                    { "531", "Hàng bán bị trả lại", true, "Expense" },
                    { "532", "Chiết khấu thương mại", true, "Expense" },
                    { "611", "Mua hàng (hàng hóa, nguyên vật liệu)", true, "Expense" },
                    { "622", "Chi phí nhân công trực tiếp", true, "Expense" },
                    { "623", "Chi phí sản xuất chung", true, "Expense" },
                    { "627", "Chi phí quản lý doanh nghiệp", true, "Expense" },
                    { "632", "Giá vốn hàng bán", true, "Expense" },
                    { "635", "Chi phí tài chính", true, "Expense" },
                    { "6421", "Chi phí tiền lương", true, "Expense" },
                    { "6422", "Chi phí bảo hiểm, bảo hộ lao động", true, "Expense" },
                    { "811", "Chi phí khác", true, "Expense" }
                });
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
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
                keyValue: "113");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "121");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "128");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "133");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "136");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "138");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "141");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "142");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "151");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "153");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "154");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "155");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "156");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "157");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "171");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "213");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "214");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "221");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "222");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "241");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "242");

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
                keyValue: "336");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "337");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "338");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "341");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "343");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "344");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "412");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "413");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "414");

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
                keyValue: "418");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "419");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "421");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "515");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "521");

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

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "622");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "623");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "627");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "632");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "635");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6421");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "6422");

            migrationBuilder.DeleteData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "811");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "112",
                column: "AccountName",
                value: "Tiền gửi Ngân hàng");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "211",
                column: "AccountName",
                value: "Tài sản cố định");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "331",
                column: "AccountName",
                value: "Phải trả cho người bán");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "333",
                column: "AccountName",
                value: "Thuế và các khoản phải nộp NN");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "334",
                column: "AccountName",
                value: "Phải trả người lao động");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "511",
                column: "AccountName",
                value: "Doanh thu bán hàng và CCDV");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "621",
                column: "AccountName",
                value: "Chi phí NVL trực tiếp");

            migrationBuilder.UpdateData(
                table: "Accounts",
                keyColumn: "AccountNumber",
                keyValue: "642",
                column: "AccountName",
                value: "Chi phí QL doanh nghiệp");
        }
    }
}
