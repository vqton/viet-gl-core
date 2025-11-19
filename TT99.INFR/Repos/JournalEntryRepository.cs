// File: D:\tt99acct\TT99.INFR\Repos\JournalEntryRepository.cs
using Microsoft.EntityFrameworkCore; // Để dùng Include, FirstOrDefaultAsync, Where, OrderBy, ToListAsync
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
// using TT99.APPL.Intrfs; // <-- ĐÃ XÓA
using TT99.DMN.Ents; // Để dùng JournalEntry, LedgerEntry
using TT99.INFR.Data; // Để dùng TT99DbContext
using TT99.DMN.Interfaces; // <-- CẦN để "thấy" IJournalEntryRepository (và IRepository nếu kế thừa)

namespace TT99.INFR.Repos
{
    /// <summary>
    /// Triển khai IJournalEntryRepository.
    /// </summary>
    public class JournalEntryRepository : Repository<JournalEntry>, IJournalEntryRepository // <-- CẬP NHẬT: Triển khai IJournalEntryRepository
    {
        public JournalEntryRepository(TT99DbContext context) : base(context)
        {
        }

        /// <summary>
        /// Triển khai phương thức tìm kiếm đặc thù: Lấy Bút toán theo Số chứng từ.
        /// </summary>
        public async Task<JournalEntry> GetByVoucherNumberAsync(string voucherNumber)
        {
            return await _dbSet
                .Include(e => e.Entries) // Bắt buộc phải Include các dòng chi tiết
                .FirstOrDefaultAsync(e => e.VoucherNumber == voucherNumber);
        }

        /// <summary>
        /// Triển khai phương thức tìm kiếm đặc thù: Lấy bút toán trong khoảng thời gian.
        /// </summary>
        public async Task<IEnumerable<JournalEntry>> GetByDateRangeAsync(DateTime startDate, DateTime endDate)
        {
            return await _dbSet
                .Include(e => e.Entries) // Bắt buộc phải Include các dòng chi tiết
                .Where(e => e.TransactionDate >= startDate.Date && e.TransactionDate <= endDate.Date)
                .OrderBy(e => e.TransactionDate)
                .ToListAsync();
        }

        // Ghi đè phương thức GetById để đảm bảo luôn Include các dòng chi tiết
        // Nếu Repository base chưa làm điều này, bạn có thể ghi đè như sau:
        // Nếu Repository base đã làm, bạn có thể bỏ qua phương thức này.
        public new async Task<JournalEntry> GetByIdAsync(Guid id)
        {
            return await _dbSet
                .Include(e => e.Entries)
                .FirstOrDefaultAsync(e => e.Id == id);
        }
    }
}