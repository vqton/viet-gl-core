// Sử dụng các thư viện cần thiết
using System;
using System.Collections.Generic;
using System.Linq;

namespace TT99.DMN.Ents
{
    /// <summary>
    /// Entity đại diện cho một Bút toán (Chứng từ Kế toán).
    /// Đây là Aggregate Root chịu trách nhiệm cho tính toàn vẹn của nghiệp vụ ghi sổ kép.
    /// </summary>
    public class JournalEntry
    {
        // Định danh duy nhất cho Bút toán
        public Guid Id { get; private set; } 

        // Số chứng từ (Ví dụ: PT0001, PC0005)
        public string VoucherNumber { get; private set; } 

        // Ngày phát sinh nghiệp vụ
        public DateTime TransactionDate { get; private set; }

        // Mô tả chung về nghiệp vụ
        public string Narration { get; private set; }

        // Trạng thái của bút toán (Ví dụ: Draft, Posted, Reversed)
        public string Status { get; private set; } = "Draft"; // Mặc định là bản nháp

        // Danh sách các dòng bút toán chi tiết (Ledger Entries)
        private readonly List<LedgerEntry> _entries = new List<LedgerEntry>();
        public IReadOnlyList<LedgerEntry> Entries => _entries.AsReadOnly();

        // Constructor
        public JournalEntry(string voucherNumber, DateTime transactionDate, string narration)
        {
            if (string.IsNullOrWhiteSpace(voucherNumber))
            {
                throw new ArgumentException("Voucher number is required for Journal Entry.");
            }
            
            Id = Guid.NewGuid();
            VoucherNumber = voucherNumber;
            TransactionDate = transactionDate.Date; // Chỉ lưu ngày, không lưu thời gian
            Narration = narration;
        }

        // Phương thức cho phép EF Core tạo đối tượng
        private JournalEntry() { }

        /// <summary>
        /// Thêm một dòng bút toán (Ledger Entry) vào bút toán này.
        /// </summary>
        /// <param name="entry">Đối tượng LedgerEntry mới.</param>
        public void AddEntry(LedgerEntry entry)
        {
            if (entry == null)
            {
                throw new ArgumentNullException(nameof(entry));
            }
            
            // Domain Rule: Đảm bảo một dòng chỉ là Nợ HOẶC Có, không thể là cả hai
            if (entry.IsDebit() && entry.IsCredit())
            {
                 throw new InvalidOperationException("A ledger entry cannot be both Debit and Credit simultaneously.");
            }
            
            _entries.Add(entry);
        }

        /// <summary>
        /// Logic Domain: Kiểm tra nguyên tắc Ghi sổ kép (Tổng Nợ phải bằng Tổng Có).
        /// </summary>
        /// <returns>True nếu hợp lệ.</returns>
        public bool IsBalanced()
        {
            // Tính tổng phát sinh Nợ
            decimal totalDebit = _entries.Sum(e => e.DebitAmount);
            // Tính tổng phát sinh Có
            decimal totalCredit = _entries.Sum(e => e.CreditAmount);

            return totalDebit == totalCredit;
        }

        /// <summary>
        /// Đánh dấu bút toán là đã được ghi sổ (Posted), chỉ có thể làm khi bút toán cân bằng.
        /// </summary>
        public void Post()
        {
            if (Status == "Posted")
            {
                throw new InvalidOperationException("Journal entry is already posted.");
            }
            
            if (!IsBalanced())
            {
                // Domain Exception: Nếu không cân bằng, không cho phép ghi sổ
                throw new InvalidOperationException("Cannot post unbalanced journal entry. Total Debit must equal Total Credit.");
            }
            
            Status = "Posted";
        }
    }
}