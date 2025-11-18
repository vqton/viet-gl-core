using System.Threading.Tasks;

namespace TT99.APPL.Intrfs
{
    /// <summary>
    /// Giao diện Unit of Work, chịu trách nhiệm quản lý các Repositories và commit/rollback transaction.
    /// </summary>
    public interface IUnitOfWork : IDisposable
    {
        // Property để truy cập Repository Bút toán
        IJournalEntryRepository JournalEntries { get; }

        // Có thể thêm các Repository khác ở đây (ví dụ: IAccountRepository Account)

        /// <summary>
        /// Thực hiện lưu tất cả các thay đổi vào cơ sở dữ liệu (Commit Transaction).
        /// </summary>
        Task<int> CommitAsync();
        
        /// <summary>
        /// Thực hiện lưu tất cả các thay đổi vào cơ sở dữ liệu.
        /// </summary>
        int Commit();
    }
}