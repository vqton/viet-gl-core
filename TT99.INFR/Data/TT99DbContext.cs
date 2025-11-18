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
            
            // === Cấu hình Entity Account ===
            modelBuilder.Entity<Account>(entity =>
            {
                // Key chính: AccountNumber
                entity.HasKey(e => e.AccountNumber); 
                entity.Property(e => e.AccountNumber).IsRequired().HasMaxLength(20); 
                entity.Property(e => e.AccountName).IsRequired().HasMaxLength(256);
                
                // Ánh xạ AccountType (Giả định là Enum hoặc Value Object) sang string trong DB
                entity.Property(e => e.Type).HasConversion<string>().HasMaxLength(30); 
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
            
            // === SEEDING DỮ LIỆU DANH MỤC TÀI KHOẢN (TT99) ===
            // Ghi chú: Sử dụng AccountType Enum đã định nghĩa trong TT99.DMN/Ents/Account.cs
            modelBuilder.Entity<Account>().HasData(
                // --- Loại 1 - TÀI SẢN NGẮN HẠN (CURRENT ASSETS) ---
                // 11 - Tiền và các khoản tương đương tiền
                new Account("111", "Tiền mặt", AccountType.Asset),
                new Account("112", "Tiền gửi ngân hàng", AccountType.Asset),
                new Account("113", "Tiền đang chuyển", AccountType.Asset),

                // 12 - Các khoản đầu tư tài chính ngắn hạn
                new Account("121", "Chứng khoán kinh doanh", AccountType.Asset),
                new Account("128", "Đầu tư nắm giữ đến ngày đáo hạn", AccountType.Asset),

                // 13 - Các khoản phải thu
                new Account("131", "Phải thu của khách hàng", AccountType.Asset),
                new Account("133", "Thuế GTGT được khấu trừ", AccountType.Asset),
                new Account("136", "Phải thu nội bộ", AccountType.Asset),
                new Account("138", "Phải thu khác", AccountType.Asset),

                // 14 - Hàng tồn kho
                new Account("141", "Tạm ứng", AccountType.Asset),
                new Account("142", "Chi phí trả trước", AccountType.Asset),
                new Account("151", "Hàng mua đang đi đường", AccountType.Asset),
                new Account("152", "Nguyên liệu, vật liệu", AccountType.Asset),
                new Account("153", "Công cụ, dụng cụ", AccountType.Asset),
                new Account("154", "Chi phí sản xuất, kinh doanh dở dang", AccountType.Asset),
                new Account("155", "Thành phẩm", AccountType.Asset),
                new Account("156", "Hàng hóa", AccountType.Asset),
                new Account("157", "Hàng gửi đi bán", AccountType.Asset),

                // 17 - Tài sản ngắn hạn khác
                new Account("171", "Gửi giữ kinh doanh chứng khoán", AccountType.Asset),

                // --- Loại 2 - TÀI SẢN DÀI HẠN (NON-CURRENT ASSETS) ---
                // 21 - Tài sản cố định
                new Account("211", "Tài sản cố định hữu hình", AccountType.Asset),
                new Account("213", "Tài sản cố định vô hình", AccountType.Asset),
                new Account("214", "Hao mòn tài sản cố định", AccountType.Asset), // Loại trừ

                // 22 - Đầu tư tài chính dài hạn
                new Account("221", "Đầu tư vào công ty liên kết, liên doanh", AccountType.Asset),
                new Account("222", "Đầu tư góp vốn vào đơn vị khác", AccountType.Asset),

                // 24 - Tài sản dở dang dài hạn
                new Account("241", "Xây dựng cơ bản dở dang", AccountType.Asset),
                new Account("242", "Bất động sản đầu tư dở dang", AccountType.Asset),

                // 27 - Tài sản dài hạn khác
                new Account("271", "Gửi giữ kinh doanh chứng khoán (dài hạn)", AccountType.Asset),
                new Account("272", "Ký quỹ, ký cược dài hạn", AccountType.Asset),

                // --- Loại 3 - NỢ PHẢI TRẢ (LIABILITIES) ---
                // 31 - Phải trả ngắn hạn
                new Account("311", "Phải trả cho người bán", AccountType.Liability),
                new Account("315", "Vay ngắn hạn", AccountType.Liability),
                new Account("331", "Phải trả người lao động", AccountType.Liability),
                new Account("333", "Thuế và các khoản phải nộp nhà nước", AccountType.Liability),
                new Account("334", "Phải trả người mua", AccountType.Liability),
                new Account("335", "Chi phí phải trả", AccountType.Liability),
                new Account("336", "Phải trả nội bộ", AccountType.Liability),
                new Account("337", "Phải trả khách hàng", AccountType.Liability),
                new Account("338", "Phải trả khác", AccountType.Liability),

                // 34 - Phải trả dài hạn
                new Account("341", "Vay dài hạn", AccountType.Liability),
                new Account("343", "Trái phiếu phát hành", AccountType.Liability),
                new Account("344", "Nhận ký quỹ dài hạn", AccountType.Liability),

                // --- Loại 4 - VỐN CHỦ SỞ HỮU (EQUITY) ---
                new Account("411", "Vốn đầu tư của chủ sở hữu", AccountType.Equity),
                new Account("412", "Thặng dư vốn cổ phần", AccountType.Equity), // hoặc Quỹ phát hành
                new Account("413", "Chênh lệch tỷ giá hối đoái", AccountType.Equity),
                new Account("414", "Quỹ đầu tư phát triển", AccountType.Equity),
                new Account("415", "Quỹ hỗ trợ sắp xếp doanh nghiệp", AccountType.Equity),
                new Account("417", "Quỹ khen thưởng, phúc lợi", AccountType.Equity),
                new Account("418", "Quỹ bình ổn giá", AccountType.Equity),
                new Account("419", "Vốn góp của thành viên", AccountType.Equity), // cho Công ty TNHH
                new Account("421", "Lợi nhuận sau thuế chưa phân phối", AccountType.Equity),

                // --- Loại 5 - DOANH THU (REVENUE) ---
                new Account("511", "Doanh thu bán hàng và cung cấp dịch vụ", AccountType.Revenue),
                new Account("515", "Doanh thu hoạt động tài chính", AccountType.Revenue),
                new Account("521", "Các khoản giảm trừ doanh thu", AccountType.Expense), // Loại trừ
                new Account("531", "Hàng bán bị trả lại", AccountType.Expense), // Loại trừ (nếu hạch toán riêng)
                new Account("532", "Chiết khấu thương mại", AccountType.Expense), // Loại trừ (nếu hạch toán riêng)

                // --- Loại 6 - CHI PHÍ (EXPENSES) ---
                // 61 - Chi phí sản xuất, kinh doanh
                new Account("611", "Mua hàng (hàng hóa, nguyên vật liệu)", AccountType.Expense), // cho ngành thương mại
                new Account("621", "Chi phí nguyên vật liệu trực tiếp", AccountType.Expense),
                new Account("622", "Chi phí nhân công trực tiếp", AccountType.Expense),
                new Account("623", "Chi phí sản xuất chung", AccountType.Expense),
                new Account("627", "Chi phí quản lý doanh nghiệp", AccountType.Expense),

                // 63 - Chi phí tài chính
                new Account("632", "Giá vốn hàng bán", AccountType.Expense),
                new Account("635", "Chi phí tài chính", AccountType.Expense),

                // 64 - Chi phí khác
                new Account("641", "Chi phí bán hàng", AccountType.Expense),
                new Account("642", "Chi phí quản lý doanh nghiệp", AccountType.Expense),
                new Account("6421", "Chi phí tiền lương", AccountType.Expense), // TK cấp 2 (nếu cần)
                new Account("6422", "Chi phí bảo hiểm, bảo hộ lao động", AccountType.Expense), // TK cấp 2 (nếu cần)
                new Account("811", "Chi phí khác", AccountType.Expense),

                // --- Loại 8 - XÁC ĐỊNH KẾT QUẢ KINH DOANH (INCOME SUMMARY / PROFIT & LOSS) ---
                new Account("911", "Xác định kết quả kinh doanh", AccountType.Other), // Tài khoản lỗ/lãi

                // --- Loại 0 - TÀI KHOẢN NGOÀI BẢNG CÂN ĐỐI KẾ TOÁN (OFF-BALANCE SHEET ACCOUNTS) ---
                new Account("001", "Tài sản thuê", AccountType.Other), // Ví dụ TK ngoài bảng
                new Account("002", "Vật tư, hàng hóa nhận giữ hộ", AccountType.Other), // Ví dụ TK ngoài bảng
                new Account("003", "Ký quỹ, ký cược", AccountType.Other), // Ví dụ TK ngoài bảng (nếu không hạch toán vào 171/272)
                new Account("004", "Chứng từ, sổ sách kế toán đã xử lý", AccountType.Other), // Ví dụ TK ngoài bảng
                new Account("005", "Công cụ, dụng cụ không đủ tiêu chuẩn tài sản cố định", AccountType.Other), // Ví dụ TK ngoài bảng
                new Account("006", "Tài sản thiếu chờ xử lý", AccountType.Other), // Ví dụ TK ngoài bảng
                new Account("007", "Tài sản thừa chờ xử lý", AccountType.Other), // Ví dụ TK ngoài bảng
                new Account("008", "Nợ khó đòi đã xử lý", AccountType.Other), // Ví dụ TK ngoài bảng
                new Account("009", "Tài sản của đơn vị cấp trên giao", AccountType.Other)  // Ví dụ TK ngoài bảng
            );
        }
    }
}