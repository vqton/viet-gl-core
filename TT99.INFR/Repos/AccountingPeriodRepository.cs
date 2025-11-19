// File: D:\tt99acct\TT99.INFR\Repos\AccountingPeriodRepository.cs
using Microsoft.EntityFrameworkCore;
using System;
using System.Threading;
using System.Threading.Tasks;
using TT99.DMN.Ents;
using TT99.DMN.Interfaces;
using TT99.INFR.Data;

namespace TT99.INFR.Repos
{
    /// <summary>
    /// Triển khai IAccountingPeriodRepository sử dụng Entity Framework Core.
    /// </summary>
    public class AccountingPeriodRepository : IAccountingPeriodRepository
    {
        private readonly TT99DbContext _context;

        public AccountingPeriodRepository(TT99DbContext context)
        {
            _context = context;
        }

        public async Task<AccountingPeriod?> GetCurrentPeriodAsync(CancellationToken cancellationToken)
        {
            // Lấy kỳ gần nhất chứa ngày hôm nay và chưa bị khóa
            var today = DateTime.Today;
            return await _context.AccountingPeriods
                .FirstOrDefaultAsync(
                    p => p.StartDate <= today && p.EndDate >= today && !p.IsLocked,
                    cancellationToken
                );
        }
        public async Task<AccountingPeriod?> GetByIdAsync(Guid id, CancellationToken cancellationToken) // <-- Thêm phương thức này
        {
            return await _context.AccountingPeriods
                .FirstOrDefaultAsync(p => p.Id == id, cancellationToken);
        }
        public async Task<AccountingPeriod?> GetPeriodByDateAsync(DateTime transactionDate, CancellationToken cancellationToken)
        {
            var dateOnly = transactionDate.Date;
            return await _context.AccountingPeriods
                .FirstOrDefaultAsync(
                    p => p.StartDate <= dateOnly && p.EndDate >= dateOnly, // Không kiểm tra IsLocked ở đây, để service xử lý sau
                    cancellationToken
                );
        }

        public async Task AddAsync(AccountingPeriod period, CancellationToken cancellationToken)
        {
            await _context.AccountingPeriods.AddAsync(period, cancellationToken);
        }

        public async Task UpdateAsync(AccountingPeriod period, CancellationToken cancellationToken)
        {
            _context.AccountingPeriods.Update(period); // EF Core sẽ đánh dấu là Modified
        }
    }
}