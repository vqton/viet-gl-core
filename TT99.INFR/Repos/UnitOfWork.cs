using System;
using System.Threading.Tasks;
using TT99.APPL.Intrfs;
using TT99.DMN.Ents;
using TT99.INFR.Data;

namespace TT99.INFR.Repos
{
    /// <summary>
    /// Triển khai Unit of Work, quản lý các Repository và commit thay đổi tới Database.
    /// </summary>
    public class UnitOfWork : IUnitOfWork
    {
        private readonly TT99DbContext _context;
        private IJournalEntryRepository _journalEntryRepository;

        public UnitOfWork(TT99DbContext context)
        {
            _context = context ?? throw new ArgumentNullException(nameof(context));
        }

        // Triển khai lazy loading cho JournalEntries Repository
        public IJournalEntryRepository JournalEntries 
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

        // Triển khai Dispose
        public void Dispose()
        {
            _context.Dispose();
            GC.SuppressFinalize(this);
        }
    }
}