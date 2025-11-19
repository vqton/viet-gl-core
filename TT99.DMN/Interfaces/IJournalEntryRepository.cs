// File: D:\tt99acct\TT99.DMN\Interfaces\IJournalEntryRepository.cs
using System;
using System.Collections.Generic;
using System.Threading.Tasks;
using TT99.DMN.Ents;
// using TT99.DMN.Interfaces; // <-- Có thể thêm dòng này nếu bạn muốn làm rõ, nhưng không bắt buộc vì cùng namespace

namespace TT99.DMN.Interfaces
{
    public interface IJournalEntryRepository : IRepository<JournalEntry> // <-- Bây giờ dòng này sẽ không lỗi nữa
    {
        // Các phương thức đặc thù cho JournalEntry
        Task<JournalEntry> GetByVoucherNumberAsync(string voucherNumber);
        Task<IEnumerable<JournalEntry>> GetByDateRangeAsync(DateTime startDate, DateTime endDate);
    }
}