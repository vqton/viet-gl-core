using TT99.DMN.Ents;
using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace TT99.APPL.Intrfs
{
    /// <summary>
    /// Giao diện Repository chuyên biệt cho Entity JournalEntry.
    /// Nó kế thừa từ Generic Repository và có thể thêm các phương thức tìm kiếm đặc thù.
    /// </summary>
    public interface IJournalEntryRepository : IRepository<JournalEntry>
    {
        /// <summary>
        /// Tìm kiếm các Bút toán theo số chứng từ.
        /// </summary>
        /// <param name="voucherNumber">Số chứng từ (Voucher Number).</param>
        Task<JournalEntry> GetByVoucherNumberAsync(string voucherNumber);

        /// <summary>
        /// Lấy tất cả các bút toán trong một khoảng thời gian nhất định.
        /// </summary>
        Task<IEnumerable<JournalEntry>> GetByDateRangeAsync(DateTime startDate, DateTime endDate);
    }
}