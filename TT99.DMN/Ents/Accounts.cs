// File: D:\tt99acct\TT99.DMN\Ents\Account.cs
using System;

namespace TT99.DMN.Ents
{
    /// <summary>
    /// Định nghĩa các loại tài khoản kế toán theo TT99 (Ví dụ: Tài sản, Nguồn vốn, Doanh thu, Chi phí).
    /// </summary>
    public enum AccountType
    {
        Asset,        // Tài sản (1xx, 2xx)
        Liability,    // Nợ phải trả (3xx)
        Equity,       // Vốn chủ sở hữu (4xx)
        Revenue,      // Doanh thu (5xx)
        Expense,      // Chi phí (6xx, 8xx)
        Other         // Khác (7xx, 9xx)
    }

    /// <summary>
    /// Entity đại diện cho Tài khoản Kế toán theo TT99.
    /// </summary>
    public class Account
    {
        // Số tài khoản (Ví dụ: "111", "642", "6421"). Dùng string để dễ dàng xử lý các TK cấp 1, 2, 3.
        public string AccountNumber { get; private set; } 
        
        // Tên tài khoản (Ví dụ: "Tiền mặt", "Chi phí quản lý doanh nghiệp", "Chi phí nhân viên quản lý")
        public string AccountName { get; private set; }

        // Loại tài khoản để xác định số dư đầu kỳ, cuối kỳ và nguyên tắc ghi sổ kép
        public AccountType Type { get; private set; }

        // Cấp tài khoản (1, 2, 3). TK cấp 1 là tổng hợp, cấp 2, 3 chi tiết hơn.
        public int Level { get; private set; } = 1; 

        // Có phải là tài khoản tổng hợp không? (Tài khoản cấp 1 thường là tổng hợp, cấp 2, 3 là chi tiết)
        // Có thể tính toán từ Level, nhưng giữ lại nếu có logic riêng
        public bool IsSummaryAccount { get; private set; } = true; 

        // Tài khoản cha (nếu có). Null nếu là TK cấp 1.
        public string? ParentAccountNumber { get; private set; } 

        // Có thể có các thuộc tính khác theo TT99 nếu cần:
        // public bool IsActive { get; private set; } = true; // Khoá/mở tài khoản
        // public bool IsUsedForCalculation { get; private set; } // Có dùng để tính toán số dư không?

        // Constructor cho TK cấp 1 (hoặc TK độc lập)
        public Account(string number, string name, AccountType type, int level = 1, string? parentNumber = null)
            : this(number, name, type, level, parentNumber, level == 1) // Gọi constructor đầy đủ
        {
        }

        // Constructor đầy đủ
        public Account(string number, string name, AccountType type, int level, string? parentNumber, bool isSummary)
        {
            if (string.IsNullOrWhiteSpace(number) || string.IsNullOrWhiteSpace(name))
            {
                // Domain Logic: Đảm bảo số và tên TK không trống
                throw new ArgumentException("Account number and name must be provided.");
            }
            if (level < 1 || level > 3) // TT99 thường dùng đến cấp 3
            {
                 throw new ArgumentException("Account level must be between 1 and 3.");
            }
            if (level > 1 && string.IsNullOrEmpty(parentNumber))
            {
                 // Domain Logic: TK cấp 2, 3 phải có TK cha
                 throw new ArgumentException("Sub-accounts (Level > 1) must have a parent account number.");
            }

            AccountNumber = number;
            AccountName = name;
            Type = type;
            Level = level;
            ParentAccountNumber = parentNumber;
            IsSummaryAccount = isSummary;
        }

        // Phương thức cho phép EF Core tạo đối tượng (private, không khuyến khích dùng trực tiếp)
        private Account() { }
    }
}