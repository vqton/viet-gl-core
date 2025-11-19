// File: D:\tt99acct\TT99.DMN\Interfaces\IUnitOfWork.cs
using System;
using System.Threading.Tasks;

namespace TT99.DMN.Interfaces
{
    public interface IUnitOfWork : IDisposable
    {
        // Các Repository property (nếu có nhiều)
        // IAccountRepository Accounts { get; }
        IJournalEntryRepository JournalEntries { get; }

        // Phương thức commit
        int Commit();
        Task<int> CommitAsync();
         Task<int> SaveChangesAsync(CancellationToken cancellationToken);
    }
}