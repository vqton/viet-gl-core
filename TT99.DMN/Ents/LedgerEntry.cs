// Sử dụng các thư viện cần thiết
using System;

namespace TT99.DMN.Ents
{
    /// <summary>
    /// Đại diện cho một dòng chi tiết trong bút toán (Nợ HOẶC Có).
    /// Đây là Value Object vì nó chỉ xác định giá trị và không có định danh độc lập.
    /// </summary>
    public class LedgerEntry
    {
        // Số tài khoản phát sinh Nợ hoặc Có
        public string AccountNumber { get; private set; }

        // Mô tả chi tiết cho dòng nghiệp vụ này
        public string Description { get; private set; }

        // Số tiền phát sinh bên Nợ
        public decimal DebitAmount { get; private set; }

        // Số tiền phát sinh bên Có
        public decimal CreditAmount { get; private set; }

        // Constructor
        public LedgerEntry(string accountNumber, string description, decimal debit, decimal credit)
        {
            if (string.IsNullOrWhiteSpace(accountNumber))
            {
                throw new ArgumentException("Account number is required for a ledger entry.");
            }
            if (debit < 0 || credit < 0)
            {
                throw new ArgumentException("Debit and Credit amounts must be non-negative.");
            }

            AccountNumber = accountNumber;
            Description = description;
            DebitAmount = debit;
            CreditAmount = credit;
        }

        // Phương thức cho phép EF Core tạo đối tượng
        private LedgerEntry() { }

        /// <summary>
        /// Logic Domain: Kiểm tra xem dòng bút toán này có phải là Nợ hay không.
        /// </summary>
        public bool IsDebit() => DebitAmount > 0 && CreditAmount == 0;

        /// <summary>
        /// Logic Domain: Kiểm tra xem dòng bút toán này có phải là Có hay không.
        /// </summary>
        public bool IsCredit() => CreditAmount > 0 && DebitAmount == 0;
    }
}