namespace AIErp.Application.Services;

using AIErp.Application.DTOs;
using AIErp.Application.Interfaces;
using AIErp.Domain.Entities;
using AIErp.Domain.Enums;
using AIErp.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;

public class ReportingService : IReportingService
{
    private readonly AppDbContext _dbContext;

    public ReportingService(AppDbContext dbContext)
    {
        _dbContext = dbContext;
    }

    public async Task<TrialBalanceDto> GetTrialBalanceAsync(DateTime startDate, DateTime endDate, CancellationToken cancellationToken = default)
    {
        var startDateOnly = DateOnly.FromDateTime(startDate);
        var endDateOnly = DateOnly.FromDateTime(endDate);

        var accounts = await _dbContext.Accounts
            .Where(a => a.IsActive)
            .OrderBy(a => a.Code)
            .ToListAsync(cancellationToken);

        var accountDict = accounts.ToDictionary(a => a.Id);

        var journalEntriesInPeriod = await _dbContext.JournalEntries
            .Where(je => je.EntryDate >= startDateOnly && je.EntryDate <= endDateOnly && je.Status == VoucherStatus.Posted)
            .Include(je => je.Items)
            .ToListAsync(cancellationToken);

        var journalEntriesBeforePeriod = await _dbContext.JournalEntries
            .Where(je => je.EntryDate < startDateOnly && je.Status == VoucherStatus.Posted)
            .Include(je => je.Items)
            .ToListAsync(cancellationToken);

        var accountBalances = CalculateAccountBalances(accounts, journalEntriesBeforePeriod, journalEntriesInPeriod);

        var lines = new List<TrialBalanceLineDto>();
        foreach (var account in accounts.Where(a => a.IsDetail))
        {
            var balance = accountBalances[account.Id];
            lines.Add(new TrialBalanceLineDto
            {
                AccountCode = account.Code,
                AccountName = account.Name,
                IsDetail = account.IsDetail,
                OpeningDebit = balance.OpeningDebit,
                OpeningCredit = balance.OpeningCredit,
                Debit = balance.Debit,
                Credit = balance.Credit,
                ClosingDebit = balance.ClosingDebit,
                ClosingCredit = balance.ClosingCredit
            });
        }

        var level1Accounts = accounts.Where(a => a.Code.Length <= 3).ToList();
        foreach (var parent in level1Accounts)
        {
            var childIds = accounts.Where(a => a.Code.StartsWith(parent.Code) && a.Code != parent.Code).Select(a => a.Id).ToList();
            if (!childIds.Any()) continue;

            var accountCodes = accountDict.Where(x => childIds.Contains(x.Key)).Select(x => x.Value.Code).ToHashSet();
            var childOpeningDebit = lines.Where(l => accountCodes.Contains(l.AccountCode)).Sum(l => l.OpeningDebit);
            var childOpeningCredit = lines.Where(l => accountCodes.Contains(l.AccountCode)).Sum(l => l.OpeningCredit);
            var childDebit = lines.Where(l => accountCodes.Contains(l.AccountCode)).Sum(l => l.Debit);
            var childCredit = lines.Where(l => accountCodes.Contains(l.AccountCode)).Sum(l => l.Credit);
            var childClosingDebit = lines.Where(l => accountCodes.Contains(l.AccountCode)).Sum(l => l.ClosingDebit);
            var childClosingCredit = lines.Where(l => accountCodes.Contains(l.AccountCode)).Sum(l => l.ClosingCredit);

            lines.Insert(0, new TrialBalanceLineDto
            {
                AccountCode = parent.Code,
                AccountName = parent.Name,
                IsDetail = false,
                OpeningDebit = childOpeningDebit,
                OpeningCredit = childOpeningCredit,
                Debit = childDebit,
                Credit = childCredit,
                ClosingDebit = childClosingDebit,
                ClosingCredit = childClosingCredit
            });
        }

        return new TrialBalanceDto
        {
            StartDate = startDate,
            EndDate = endDate,
            Lines = lines.OrderBy(l => l.AccountCode).ToList(),
            TotalOpeningDebit = lines.Sum(l => l.OpeningDebit),
            TotalOpeningCredit = lines.Sum(l => l.OpeningCredit),
            TotalDebit = lines.Sum(l => l.Debit),
            TotalCredit = lines.Sum(l => l.Credit),
            TotalClosingDebit = lines.Sum(l => l.ClosingDebit),
            TotalClosingCredit = lines.Sum(l => l.ClosingCredit)
        };
    }

    public async Task<GeneralLedgerDto> GetGeneralLedgerAsync(string accountCode, DateTime startDate, DateTime endDate, CancellationToken cancellationToken = default)
    {
        var startDateOnly = DateOnly.FromDateTime(startDate);
        var endDateOnly = DateOnly.FromDateTime(endDate);

        var account = await _dbContext.Accounts
            .FirstOrDefaultAsync(a => a.Code == accountCode, cancellationToken);

        if (account == null)
            throw new InvalidOperationException($"Không tìm thấy tài khoản {accountCode}");

        var childAccounts = await _dbContext.Accounts
            .Where(a => a.Code.StartsWith(accountCode) && a.IsActive)
            .Select(a => a.Id)
            .ToListAsync(cancellationToken);

        var openingBalance = await CalculateOpeningBalanceAsync(childAccounts, startDateOnly, cancellationToken);

        var journalItems = await _dbContext.JournalItems
            .Include(ji => ji.JournalEntry)
            .Include(ji => ji.Partner)
            .Where(ji => childAccounts.Contains(ji.AccountId)
                && ji.JournalEntry!.EntryDate >= startDateOnly
                && ji.JournalEntry.EntryDate <= endDateOnly
                && ji.JournalEntry.Status == VoucherStatus.Posted)
            .OrderBy(ji => ji.JournalEntry!.EntryDate)
            .ThenBy(ji => ji.JournalEntry!.EntryNumber)
            .ToListAsync(cancellationToken);

        var runningBalance = openingBalance;
        var lines = new List<GeneralLedgerLineDto>();

        foreach (var item in journalItems)
        {
            var debit = item.DebitAmount;
            var credit = item.CreditAmount;
            runningBalance += debit - credit;

            lines.Add(new GeneralLedgerLineDto
            {
                Date = item.JournalEntry!.EntryDate.ToDateTime(TimeOnly.MinValue),
                EntryNumber = item.JournalEntry.EntryNumber,
                Description = item.JournalEntry.Description,
                PartnerCode = item.Partner?.Code ?? "",
                PartnerName = item.Partner?.Name ?? "",
                Debit = debit,
                Credit = credit,
                RunningBalance = runningBalance
            });
        }

        return new GeneralLedgerDto
        {
            AccountCode = account.Code,
            AccountName = account.Name,
            StartDate = startDate,
            EndDate = endDate,
            OpeningBalance = openingBalance,
            Lines = lines,
            ClosingBalance = runningBalance
        };
    }

    private Dictionary<Guid, AccountBalance> CalculateAccountBalances(
        List<Account> accounts,
        List<JournalEntry> entriesBeforePeriod,
        List<JournalEntry> entriesInPeriod)
    {
        var balances = accounts.ToDictionary(a => a.Id, _ => new AccountBalance());

        foreach (var entry in entriesBeforePeriod)
        {
            foreach (var item in entry.Items)
            {
                if (!balances.ContainsKey(item.AccountId)) continue;
                var account = accounts.First(a => a.Id == item.AccountId);
                var balance = balances[item.AccountId];

                if (account.NormalBalance == NormalBalance.Debit)
                {
                    var net = item.DebitAmount - item.CreditAmount;
                    if (net > 0)
                        balance.OpeningDebit += net;
                    else
                        balance.OpeningCredit -= net;
                }
                else
                {
                    var net = item.CreditAmount - item.DebitAmount;
                    if (net > 0)
                        balance.OpeningCredit += net;
                    else
                        balance.OpeningDebit -= net;
                }
            }
        }

        foreach (var entry in entriesInPeriod)
        {
            foreach (var item in entry.Items)
            {
                if (!balances.ContainsKey(item.AccountId)) continue;
                balances[item.AccountId].Debit += item.DebitAmount;
                balances[item.AccountId].Credit += item.CreditAmount;
            }
        }

        foreach (var account in accounts)
        {
            var balance = balances[account.Id];
            var net = (balance.OpeningDebit + balance.Debit) - (balance.OpeningCredit + balance.Credit);
            if (net > 0)
            {
                balance.ClosingDebit = net;
                balance.ClosingCredit = 0;
            }
            else
            {
                balance.ClosingDebit = 0;
                balance.ClosingCredit = -net;
            }
        }

        return balances;
    }

    private async Task<decimal> CalculateOpeningBalanceAsync(List<Guid> accountIds, DateOnly beforeDate, CancellationToken cancellationToken)
    {
        var entries = await _dbContext.JournalEntries
            .Where(je => je.EntryDate < beforeDate && je.Status == VoucherStatus.Posted)
            .Include(je => je.Items)
            .ToListAsync(cancellationToken);

        decimal balance = 0;
        var accounts = await _dbContext.Accounts
            .Where(a => accountIds.Contains(a.Id))
            .ToDictionaryAsync(a => a.Id, a => a.NormalBalance, cancellationToken);

        foreach (var entry in entries)
        {
            foreach (var item in entry.Items.Where(i => accountIds.Contains(i.AccountId)))
            {
                var normalBalance = accounts.GetValueOrDefault(item.AccountId, NormalBalance.Debit);
                if (normalBalance == NormalBalance.Debit)
                    balance += item.DebitAmount - item.CreditAmount;
                else
                    balance += item.CreditAmount - item.DebitAmount;
            }
        }

        return balance;
    }

    private class AccountBalance
    {
        public decimal OpeningDebit { get; set; }
        public decimal OpeningCredit { get; set; }
        public decimal Debit { get; set; }
        public decimal Credit { get; set; }
        public decimal ClosingDebit { get; set; }
        public decimal ClosingCredit { get; set; }
    }
}
