// File: D:\tt99acct\TT99.INFR\Data\TT99DbContext.cs
using Microsoft.EntityFrameworkCore;
using TT99.DMN.Ents; 
using TT99.DMN.Interfaces; 

namespace TT99.INFR.Data
{
    /// <summary>
    /// Database Context cho Entity Framework Core.
    /// Chịu trách nhiệm quản lý phiên kết nối DB và ánh xạ Entities.
    /// </summary>
    public class TT99DbContext : DbContext
    {
        // DbSet cho Entity Bút toán (Aggregate Root)
        public DbSet<JournalEntry> JournalEntries { get; set; }
        
        // DbSet cho Entity Tài khoản
        public DbSet<Account> Accounts { get; set; }
        
        // Constructor
        public TT99DbContext(DbContextOptions<TT99DbContext> options) : base(options)
        {
        }

        /// <summary>
        /// Phương thức cấu hình ánh xạ Entity tới Database và Seeding Data.
        /// </summary>
        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {
            base.OnModelCreating(modelBuilder);
            
            // === Cấu hình Entity Account (Updated for TT99 Hierarchy) ===
            modelBuilder.Entity<Account>(entity =>
            {
                // Key chính: AccountNumber
                entity.HasKey(e => e.AccountNumber); 
                entity.Property(e => e.AccountNumber).IsRequired().HasMaxLength(20); 
                entity.Property(e => e.AccountName).IsRequired().HasMaxLength(256);
                
                // Ánh xạ AccountType (Giả định là Enum hoặc Value Object) sang string trong DB
                entity.Property(e => e.Type).HasConversion<string>().HasMaxLength(30);

                // Cấu hình các thuộc tính mới cho TT99 Hierarchy
                entity.Property(e => e.Level).IsRequired();
                entity.Property(e => e.ParentAccountNumber).HasMaxLength(20);

                // Optional: Cấu hình quan hệ cha-con (nếu cần cho truy vấn phức tạp sau này)
                // entity.HasOne<Account>() // TK con
                //      .WithMany() // Không có collection TK con trong Account nếu không cần
                //      .HasForeignKey(e => e.ParentAccountNumber)
                //      .OnDelete(DeleteBehavior.NoAction); // Tránh xóa cha làm mất con
            });

            // === Cấu hình Entity JournalEntry (Aggregate Root) ===
            modelBuilder.Entity<JournalEntry>(entity =>
            {
                // Key chính
                entity.HasKey(e => e.Id);
                entity.Property(e => e.VoucherNumber).IsRequired().HasMaxLength(50);
                entity.Property(e => e.TransactionDate).IsRequired();
                entity.Property(e => e.Narration).HasMaxLength(500);
                entity.Property(e => e.Status).IsRequired().HasMaxLength(20); // Ví dụ: "Draft", "Posted"

                // Cấu hình LedgerEntry là Owned Entity (Value Object)
                entity.OwnsMany(e => e.Entries, entry =>
                {
                    entry.WithOwner().HasForeignKey("JournalEntryId"); // Khóa ngoại tự động
                    entry.Property(l => l.AccountNumber).IsRequired().HasMaxLength(20);
                    // Đảm bảo kiểu dữ liệu trong DB chính xác cho tiền tệ
                    entry.Property(l => l.DebitAmount).HasColumnType("decimal(18, 2)");
                    entry.Property(l => l.CreditAmount).HasColumnType("decimal(18, 2)");
                    entry.Property(l => l.Description).HasMaxLength(256);
                    
                    // Cấu hình ID cho dòng chi tiết (cần cho Owned Entity)
                    entry.Property<int>("Id").ValueGeneratedOnAdd();
                    entry.HasKey("Id"); 
                    entry.ToTable("LedgerEntries"); // Tên bảng cho các dòng chi tiết
                });
            });
            
            // === SEEDING DỮ LIỆU DANH MỤC TÀI KHOẢN (TT99 - Cập nhật với cấp độ và tài khoản cha) ===
            // Ghi chú: Sử dụng AccountType Enum đã định nghĩa trong TT99.DMN/Ents/Account.cs
            // Sử dụng constructor mới của Account: Account(number, name, type, level, parentNumber, isSummary)
            modelBuilder.Entity<Account>().HasData(
                // --- A. LOẠI TÀI KHOẢN TÀI SẢN (Asset Accounts) ---
                // TK cấp 1
                new Account("111", "Tiền mặt", AccountType.Asset, 1, null, true),
                new Account("112", "Tiền gửi không kỳ hạn", AccountType.Asset, 1, null, true),
                new Account("113", "Tiền đang chuyển", AccountType.Asset, 1, null, true),
                new Account("121", "Chứng khoán kinh doanh", AccountType.Asset, 1, null, true),
                new Account("128", "Đầu tư nắm giữ đến ngày đáo hạn", AccountType.Asset, 1, null, true),
                new Account("131", "Phải thu của khách hàng", AccountType.Asset, 1, null, true),
                new Account("133", "Thuế GTGT được khấu trừ", AccountType.Asset, 1, null, true),
                new Account("136", "Phải thu nội bộ", AccountType.Asset, 1, null, true),
                new Account("138", "Phải thu khác", AccountType.Asset, 1, null, true),
                new Account("141", "Tạm ứng", AccountType.Asset, 1, null, true),
                new Account("151", "Hàng mua đang đi đường", AccountType.Asset, 1, null, true),
                new Account("152", "Nguyên liệu, vật liệu", AccountType.Asset, 1, null, true),
                new Account("153", "Công cụ, dụng cụ", AccountType.Asset, 1, null, true),
                new Account("154", "Chi phí sản xuất, kinh doanh dở dang", AccountType.Asset, 1, null, true),
                new Account("155", "Sản phẩm", AccountType.Asset, 1, null, true),
                new Account("156", "Hàng hóa", AccountType.Asset, 1, null, true),
                new Account("157", "Hàng gửi đi bán", AccountType.Asset, 1, null, true),
                new Account("158", "Nguyên liệu, vật tư tại kho bảo thuế", AccountType.Asset, 1, null, true),
                new Account("171", "Giao dịch mua, bán lại trái phiếu chính phủ", AccountType.Asset, 1, null, true),
                new Account("211", "Tài sản cố định hữu hình", AccountType.Asset, 1, null, true),
                new Account("212", "Tài sản cố định thuê tài chính", AccountType.Asset, 1, null, true),
                new Account("213", "Tài sản cố định vô hình", AccountType.Asset, 1, null, true),
                new Account("214", "Hao mòn tài sản cố định", AccountType.Expense, 1, null, true), // Loại trừ
                new Account("215", "Tài sản sinh học", AccountType.Asset, 1, null, true),
                new Account("217", "Bất động sản đầu tư", AccountType.Asset, 1, null, true),
                new Account("221", "Đầu tư vào công ty con", AccountType.Asset, 1, null, true),
                new Account("222", "Đầu tư vào công ty liên doanh, liên kết", AccountType.Asset, 1, null, true),
                new Account("228", "Đầu tư khác", AccountType.Asset, 1, null, true),
                new Account("229", "Dự phòng tổn thất tài sản", AccountType.Asset, 1, null, true), // Often treated as contra-asset
                new Account("241", "Xây dựng cơ bản dở dang", AccountType.Asset, 1, null, true),
                new Account("242", "Chi phí chờ phân bổ", AccountType.Asset, 1, null, true),
                new Account("243", "Tài sản thuế thu nhập hoãn lại", AccountType.Asset, 1, null, true),
                new Account("244", "Ký quỹ, ký cược", AccountType.Asset, 1, null, true),

                // TK cấp 2 cho 128
                new Account("1281", "Tiền gửi có kỳ hạn", AccountType.Asset, 2, "128", false),
                new Account("1282", "Trái phiếu", AccountType.Asset, 2, "128", false),
                new Account("1283", "Cho vay", AccountType.Asset, 2, "128", false),
                new Account("1288", "Các khoản đầu tư khác nắm giữ đến ngày đáo hạn", AccountType.Asset, 2, "128", false),

                // TK cấp 2 cho 133
                new Account("1331", "Thuế GTGT được khấu trừ của hàng hóa, dịch vụ", AccountType.Asset, 2, "133", false),
                new Account("1332", "Thuế GTGT được khấu trừ của TSCĐ", AccountType.Asset, 2, "133", false),

                // TK cấp 2 cho 136
                new Account("1361", "Vốn kinh doanh ở đơn vị trực thuộc", AccountType.Asset, 2, "136", false),
                new Account("1362", "Phải thu nội bộ về chênh lệch tỷ giá", AccountType.Asset, 2, "136", false),
                new Account("1363", "Phải thu nội bộ về chi phí đi vay đủ điều kiện được vốn hóa", AccountType.Asset, 2, "136", false),
                new Account("1368", "Phải thu nội bộ khác", AccountType.Asset, 2, "136", false),

                // TK cấp 2 cho 138
                new Account("1381", "Tài sản thiếu chờ xử lý", AccountType.Asset, 2, "138", false),
                new Account("1388", "Phải thu khác", AccountType.Asset, 2, "138", false),

                // TK cấp 2 cho 214
                new Account("2141", "Hao mòn TSCĐ hữu hình", AccountType.Expense, 2, "214", false), // Loại trừ
                new Account("2142", "Hao mòn TSCĐ thuê tài chính", AccountType.Expense, 2, "214", false), // Loại trừ
                new Account("2143", "Hao mòn TSCĐ vô hình", AccountType.Expense, 2, "214", false), // Loại trừ
                new Account("2147", "Hao mòn BĐSĐT", AccountType.Expense, 2, "214", false), // Loại trừ

                // TK cấp 2 cho 215
                new Account("2151", "Súc vật nuôi cho sản phẩm định kỳ", AccountType.Asset, 2, "215", false),
                new Account("21511", "Súc vật nuôi cho sản phẩm định kỳ chưa đạt đến giai đoạn trưởng thành", AccountType.Asset, 3, "2151", false),
                new Account("21512", "Súc vật nuôi cho sản phẩm định kỳ đạt đến giai đoạn trưởng thành", AccountType.Asset, 3, "2151", false),
                new Account("2152", "Súc vật nuôi lấy sản phẩm một lần", AccountType.Asset, 2, "215", false),
                new Account("21521", "Súc vật nuôi lấy sản phẩm một lần", AccountType.Asset, 3, "2152", false),
                new Account("2153", "Cây trồng theo mùa vụ hoặc lấy sản phẩm một lần", AccountType.Asset, 2, "215", false),

                // TK cấp 2 cho 228
                new Account("2281", "Đầu tư góp vốn vào đơn vị khác", AccountType.Asset, 2, "228", false),
                new Account("2282", "Đầu tư khác", AccountType.Asset, 2, "228", false),

                // TK cấp 2 cho 229
                new Account("2291", "Dự phòng giảm giá chứng khoán kinh doanh", AccountType.Asset, 2, "229", false), // Often treated as contra-asset
                new Account("2292", "Dự phòng tổn thất đầu tư vào đơn vị khác", AccountType.Asset, 2, "229", false), // Often treated as contra-asset
                new Account("2293", "Dự phòng tổn thất các khoản đầu tư tài chính khác", AccountType.Asset, 2, "229", false), // Often treated as contra-asset
                new Account("2294", "Dự phòng giảm giá hàng tồn kho", AccountType.Asset, 2, "229", false), // Often treated as contra-asset
                new Account("2295", "Dự phòng tổn thất tài sản sinh học", AccountType.Asset, 2, "229", false), // Often treated as contra-asset

                // TK cấp 2 cho 241
                new Account("2411", "Mua sắm TSCĐ", AccountType.Asset, 2, "241", false),
                new Account("2412", "Xây dựng cơ bản", AccountType.Asset, 2, "241", false),
                new Account("2413", "Sửa chữa, bảo dưỡng định kỳ TSCĐ", AccountType.Asset, 2, "241", false),
                new Account("2414", "Nâng cấp, cải tạo TSCĐ", AccountType.Asset, 2, "241", false),

                // --- B. LOẠI TÀI KHOẢN NỢ PHẢI TRẢ (Liability Accounts) ---
                // TK cấp 1
                new Account("331", "Phải trả cho người bán", AccountType.Liability, 1, null, true),
                new Account("332", "Phải trả cổ tức, lợi nhuận", AccountType.Liability, 1, null, true),
                new Account("333", "Thuế và các khoản phải nộp Nhà nước", AccountType.Liability, 1, null, true),
                new Account("334", "Phải trả người lao động", AccountType.Liability, 1, null, true),
                new Account("336", "Phải trả nội bộ", AccountType.Liability, 1, null, true),
                new Account("337", "Thanh toán tiền theo hợp đồng xây dựng", AccountType.Liability, 1, null, true),
                new Account("338", "Phải trả, phải nộp khác", AccountType.Liability, 1, null, true),
                new Account("341", "Vay và nợ thuê tài chính", AccountType.Liability, 1, null, true),
                new Account("343", "Trái phiếu phát hành", AccountType.Liability, 1, null, true),
                new Account("344", "Nhận ký quỹ, ký cược", AccountType.Liability, 1, null, true),
                new Account("347", "Thuế thu nhập hoãn lại phải trả", AccountType.Liability, 1, null, true),
                new Account("352", "Dự phòng phải trả", AccountType.Liability, 1, null, true),
                new Account("353", "Quỹ khen thưởng, phúc lợi", AccountType.Liability, 1, null, true), // Listed as Liability in TT99
                new Account("356", "Quỹ phát triển khoa học và công nghệ", AccountType.Liability, 1, null, true), // Listed as Liability in TT99
                new Account("357", "Quỹ bình ổn giá", AccountType.Liability, 1, null, true), // Listed as Liability in TT99

                // TK cấp 2 cho 333
                new Account("3331", "Thuế GTGT phải nộp", AccountType.Liability, 2, "333", false),
                new Account("3332", "Thuế tiêu thụ đặc biệt", AccountType.Liability, 2, "333", false),
                new Account("3333", "Thuế xuất, nhập khẩu", AccountType.Liability, 2, "333", false),
                new Account("3334", "Thuế thu nhập doanh nghiệp", AccountType.Liability, 2, "333", false),
                new Account("3335", "Thuế thu nhập cá nhân", AccountType.Liability, 2, "333", false),
                new Account("3336", "Thuế tài nguyên", AccountType.Liability, 2, "333", false),
                new Account("3337", "Thuế đất, tiền thuê đất", AccountType.Liability, 2, "333", false),
                new Account("3338", "Thuế bảo vệ môi trường", AccountType.Liability, 2, "333", false),
                new Account("3339", "Phí, lệ phí và các khoản phải nộp khác", AccountType.Liability, 2, "333", false),

                // TK cấp 2 cho 336
                new Account("3361", "Phải trả nội bộ về vốn kinh doanh", AccountType.Liability, 2, "336", false),
                new Account("3362", "Phải trả nội bộ về chênh lệch tỷ giá", AccountType.Liability, 2, "336", false),
                new Account("3363", "Phải trả nội bộ về chi phí đi vay đủ điều kiện được vốn hóa", AccountType.Liability, 2, "336", false),
                new Account("3368", "Phải trả nội bộ khác", AccountType.Liability, 2, "336", false),

                // TK cấp 2 cho 338
                new Account("3381", "Tài sản thừa chờ giải quyết", AccountType.Liability, 2, "338", false),
                new Account("3382", "Kinh phí công đoàn", AccountType.Liability, 2, "338", false),
                new Account("3383", "Bảo hiểm xã hội", AccountType.Liability, 2, "338", false),
                new Account("3384", "Bảo hiểm y tế", AccountType.Liability, 2, "338", false),
                new Account("3385", "Bảo hiểm thất nghiệp", AccountType.Liability, 2, "338", false),
                new Account("3387", "Doanh thu chờ phân bổ", AccountType.Liability, 2, "338", false),
                new Account("3388", "Phải trả, phải nộp khác", AccountType.Liability, 2, "338", false),

                // TK cấp 2 cho 341
                new Account("3411", "Các khoản vay", AccountType.Liability, 2, "341", false),
                new Account("3412", "Nợ thuê tài chính", AccountType.Liability, 2, "341", false),

                // TK cấp 2 cho 343
                new Account("3431", "Trái phiếu thường", AccountType.Liability, 2, "343", false),
                new Account("3432", "Trái phiếu chuyển đổi", AccountType.Liability, 2, "343", false),

                // TK cấp 2 cho 352
                new Account("3521", "Dự phòng bảo hành sản phẩm, hàng hóa", AccountType.Liability, 2, "352", false),
                new Account("3522", "Dự phòng bảo hành công trình xây dựng", AccountType.Liability, 2, "352", false),
                new Account("3523", "Dự phòng tái cơ cấu doanh nghiệp", AccountType.Liability, 2, "352", false),
                new Account("3525", "Dự phòng phải trả khác", AccountType.Liability, 2, "352", false),

                // TK cấp 2 cho 353
                new Account("3531", "Quỹ khen thưởng", AccountType.Liability, 2, "353", false), // Listed as Liability in TT99
                new Account("3532", "Quỹ phúc lợi", AccountType.Liability, 2, "353", false), // Listed as Liability in TT99
                new Account("3533", "Quỹ phúc lợi đã hình thành TSCĐ", AccountType.Liability, 2, "353", false), // Listed as Liability in TT99
                new Account("3534", "Quỹ phúc lợi quản lý điều hành công ty", AccountType.Liability, 2, "353", false), // Listed as Liability in TT99

                // TK cấp 2 cho 356
                new Account("3561", "Quỹ phát triển khoa học và công nghệ", AccountType.Liability, 2, "356", false), // Listed as Liability in TT99
                new Account("3562", "Quỹ phát triển khoa học và công nghệ đã hình thành tài sản", AccountType.Liability, 2, "356", false), // Listed as Liability in TT99

                // --- C. LOẠI TÀI KHOẢN VỐN CHỦ SỞ HỮU (Owner's Equity Accounts) ---
                // TK cấp 1
                new Account("411", "Vốn chủ sở hữu", AccountType.Equity, 1, null, true),
                new Account("412", "Chênh lệch đánh giá lại tài sản", AccountType.Equity, 1, null, true),
                new Account("413", "Chênh lệch tỷ giá hối đoái", AccountType.Equity, 1, null, true),
                new Account("414", "Quỹ đầu tư phát triển", AccountType.Equity, 1, null, true),
                new Account("418", "Các quỹ khác thuộc vốn chủ sở hữu", AccountType.Equity, 1, null, true),
                new Account("419", "Cổ phiếu mua lại của chính mình", AccountType.Equity, 1, null, true),
                new Account("421", "Lợi nhuận sau thuế chưa phân phối", AccountType.Equity, 1, null, true),

                // TK cấp 2 cho 411
                new Account("4111", "Vốn góp của chủ sở hữu", AccountType.Equity, 2, "411", false),
                new Account("4112", "Thặng dư vốn", AccountType.Equity, 2, "411", false),
                new Account("4118", "Vốn khác", AccountType.Equity, 2, "411", false),

                // TK cấp 3 cho 4111
                new Account("41111", "Vốn góp của chủ sở hữu phổ thông có quyền biểu quyết", AccountType.Equity, 3, "4111", false),
                new Account("41112", "Vốn góp khác", AccountType.Equity, 3, "4111", false),

                // TK cấp 2 cho 421
                new Account("4211", "Lợi nhuận sau thuế chưa phân phối lũy kế đến cuối năm trước", AccountType.Equity, 2, "421", false),
                new Account("4212", "Lợi nhuận sau thuế chưa phân phối năm nay", AccountType.Equity, 2, "421", false),

                // --- D. LOẠI TÀI KHOẢN DOANH THU (Revenue Accounts) ---
                // TK cấp 1
                new Account("511", "Doanh thu bán hàng và cung cấp dịch vụ", AccountType.Revenue, 1, null, true),
                new Account("515", "Doanh thu hoạt động tài chính", AccountType.Revenue, 1, null, true),

                // --- E. LOẠI TÀI KHOẢN CHI PHÍ SẢN XUẤT, KINH DOANH (Production, Business Expense Accounts) ---
                // TK cấp 1
                new Account("521", "Các khoản giảm trừ doanh thu", AccountType.Revenue, 1, null, true), // Loại trừ
                new Account("621", "Chi phí nguyên liệu, vật liệu trực tiếp", AccountType.Expense, 1, null, true),
                new Account("622", "Chi phí nhân công trực tiếp", AccountType.Expense, 1, null, true),
                new Account("623", "Chi phí sử dụng máy thi công", AccountType.Expense, 1, null, true),
                new Account("627", "Chi phí sản xuất chung", AccountType.Expense, 1, null, true),
                new Account("632", "Giá vốn hàng bán", AccountType.Expense, 1, null, true),
                new Account("635", "Chi phí tài chính", AccountType.Expense, 1, null, true),
                new Account("641", "Chi phí bán hàng", AccountType.Expense, 1, null, true),
                new Account("642", "Chi phí quản lý doanh nghiệp", AccountType.Expense, 1, null, true),

                // TK cấp 2 cho 623
                new Account("6231", "Chi phí nhân công", AccountType.Expense, 2, "623", false),
                new Account("6232", "Chi phí vật liệu", AccountType.Expense, 2, "623", false),
                new Account("6233", "Chi phí dụng cụ sản xuất", AccountType.Expense, 2, "623", false),
                new Account("6234", "Chi phí dịch vụ mua ngoài", AccountType.Expense, 2, "623", false),
                new Account("6238", "Chi phí bằng tiền khác", AccountType.Expense, 2, "623", false),

                // TK cấp 2 cho 627
                new Account("6271", "Chi phí nhân viên phân xưởng", AccountType.Expense, 2, "627", false),
                new Account("6272", "Chi phí vật liệu sản xuất", AccountType.Expense, 2, "627", false),
                new Account("6273", "Chi phí dụng cụ sản xuất", AccountType.Expense, 2, "627", false),
                new Account("6274", "Chi phí khấu hao TSCĐ", AccountType.Expense, 2, "627", false),
                new Account("6275", "Thuế, phí, lệ phí", AccountType.Expense, 2, "627", false),
                new Account("6277", "Chi phí dịch vụ mua ngoài", AccountType.Expense, 2, "627", false),
                new Account("6278", "Chi phí bằng tiền khác", AccountType.Expense, 2, "627", false),

                // TK cấp 2 cho 641
                new Account("6411", "Chi phí nhân viên bán hàng", AccountType.Expense, 2, "641", false),
                new Account("6412", "Chi phí vật liệu, bao bì", AccountType.Expense, 2, "641", false),
                new Account("6413", "Chi phí dụng cụ, vật tư", AccountType.Expense, 2, "641", false),
                new Account("6414", "Chi phí khấu hao TSCĐ", AccountType.Expense, 2, "641", false),
                new Account("6415", "Thuế, phí, lệ phí", AccountType.Expense, 2, "641", false),
                new Account("6417", "Chi phí dịch vụ mua ngoài", AccountType.Expense, 2, "641", false),
                new Account("6418", "Chi phí bằng tiền khác", AccountType.Expense, 2, "641", false),

                // TK cấp 2 cho 642
                new Account("6421", "Chi phí nhân viên quản lý", AccountType.Expense, 2, "642", false),
                new Account("6422", "Chi phí vật liệu văn phòng", AccountType.Expense, 2, "642", false),
                new Account("6423", "Chi phí đồ dùng văn phòng", AccountType.Expense, 2, "642", false),
                new Account("6424", "Chi phí khấu hao TSCĐ", AccountType.Expense, 2, "642", false),
                new Account("6425", "Thuế, phí, lệ phí", AccountType.Expense, 2, "642", false),
                new Account("6426", "Chi phí dự phòng", AccountType.Expense, 2, "642", false),
                new Account("6427", "Chi phí dịch vụ mua ngoài", AccountType.Expense, 2, "642", false),
                new Account("6428", "Chi phí bằng tiền khác", AccountType.Expense, 2, "642", false),

                // --- F. LOẠI TÀI KHOẢN THU NHẬP KHÁC (Other Income Accounts) ---
                // TK cấp 1
                new Account("711", "Thu nhập khác", AccountType.Revenue, 1, null, true),

                // --- G. LOẠI TÀI KHOẢN CHI PHÍ KHÁC (Other Expense Accounts) ---
                // TK cấp 1
                new Account("811", "Chi phí khác", AccountType.Expense, 1, null, true),

                // --- H. LOẠI TÀI KHOẢN THUẾ TNDN (Corporate Income Tax Accounts) ---
                // TK cấp 1
                new Account("821", "Chi phí thuế thu nhập doanh nghiệp", AccountType.Expense, 1, null, true),

                // TK cấp 2 cho 821
                new Account("8211", "Chi phí thuế TNDN hiện hành", AccountType.Expense, 2, "821", false),
                new Account("8212", "Chi phí thuế TNDN hoãn lại", AccountType.Expense, 2, "821", false),

                // --- I. TÀI KHOẢN XÁC ĐỊNH KẾT QUẢ KINH DOANH (Business Results Determination Account) ---
                // TK cấp 1
                new Account("911", "Xác định kết quả kinh doanh", AccountType.Other, 1, null, true)
            );
        }
    }
}