using System;
using System.Threading;
using System.Threading.Tasks;
using TT99.DMN.Ents;

namespace TT99.DMN.Interfaces
{
    /// <summary>
    /// Giao diện định nghĩa các dịch vụ nghiệp vụ chính liên quan đến Sổ Nhật Ký (Journaling).
    /// </summary>
    public interface IJournalingService
    {
        /// <summary>
        /// Xử lý, xác thực, ghi sổ và lưu trữ một bút toán mới vào hệ thống.
        /// Phương thức này được Command Handler gọi.
        /// </summary>
        /// <returns>ID (Guid) của bút toán đã được ghi sổ.</returns>
        Task<Guid> CreateJournalEntryAsync(JournalEntry entry, CancellationToken cancellationToken);
        
        /// <summary>
        /// Xác thực tất cả các quy tắc nghiệp vụ Kế toán (tính cân bằng, tồn tại TK, quy tắc hạch toán) trước khi ghi sổ.
        /// </summary>
        Task ValidateAndPostEntryAsync(JournalEntry entry);
        
        /// <summary>
        /// Triển khai logic đảo ngược bút toán.
        /// </summary>
        void ReverseEntry(Guid journalEntryId);
    }
}