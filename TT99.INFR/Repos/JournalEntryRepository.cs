using Microsoft.EntityFrameworkCore;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using TT99.APPL.Intrfs;
using TT99.DMN.Ents;
using TT99.INFR.Data;

namespace TT99.INFR.Repos
{
    /// <summary>
    /// Triển khai IJournalEntryRepository.
    /// </summary>
    public class JournalEntryRepository : Repository<JournalEntry>, IJournalEntryRepository
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
        public new async Task<JournalEntry> GetByIdAsync(Guid id)
        {
            return await _dbSet
                .Include(e => e.Entries)
                .FirstOrDefaultAsync(e => e.Id == id);
        }
    }
}