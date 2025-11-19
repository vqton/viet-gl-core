// File: D:\tt99acct\TT99.INFR\Repos\UnitOfWork.cs
using System;
using System.Threading.Tasks;

using TT99.DMN.Ents;
using TT99.INFR.Data;
using TT99.DMN.Interfaces; // <-- THÊM DÒNG NÀY

namespace TT99.INFR.Repos
{
    /// <summary>
    /// Triển khai Unit of Work, quản lý các Repository và commit thay đổi tới Database.
    /// </summary>
    public class UnitOfWork : IUnitOfWork // <-- Bây giờ dòng này sẽ không lỗi nữa
    {
        private readonly TT99DbContext _context;
        private IJournalEntryRepository _journalEntryRepository;

        public UnitOfWork(TT99DbContext context)
        {
            _context = context ?? throw new ArgumentNullException(nameof(context));
        }

        // Triển khai lazy loading cho JournalEntries Repository
        public IJournalEntryRepository JournalEntries // <-- Bây giờ dòng này sẽ không lỗi nữa
        {
            get
            {
                // Chỉ khởi tạo Repository khi được gọi lần đầu
                if (_journalEntryRepository == null)
                {
                    _journalEntryRepository = new JournalEntryRepository(_context);
                }
                return _journalEntryRepository;
            }
        }

        // Triển khai CommitAsync
        public async Task<int> CommitAsync()
        {
            return await _context.SaveChangesAsync();
        }
        
        // Triển khai Commit
        public int Commit()
        {
            return _context.SaveChanges();
        }
       // **Triển khai SaveChangesAsync với CancellationToken**
        public async Task<int> SaveChangesAsync(CancellationToken cancellationToken)
        {
            return await _context.SaveChangesAsync(cancellationToken);
        }
        // Triển khai Dispose
        public void Dispose()
        {
            _context.Dispose();
            GC.SuppressFinalize(this);
        }
    }
}