using AIErp.Application.DTOs;
using AIErp.Application.Exceptions;
using AIErp.Application.Interfaces;
using AIErp.Domain.Entities;
using AIErp.Domain.Enums;
using AIErp.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;

namespace AIErp.Application.Services;

public class JournalEntryService(AppDbContext dbContext) : IJournalEntryService
{
    private readonly AppDbContext _dbContext = dbContext;

    public async Task<JournalEntryResultDto> CreateAsync(JournalEntryDto dto, string createdBy, CancellationToken cancellationToken = default)
    {
        // Validate fiscal period
        var fiscalPeriod = await _dbContext.FiscalPeriods
            .FirstOrDefaultAsync(p => p.Id == dto.FiscalPeriodId, cancellationToken);

        if (fiscalPeriod == null)
            throw new BusinessException(BusinessErrors.ValidationError, "Fiscal period not found");

        if (!fiscalPeriod.IsOpen)
            throw new BusinessException(BusinessErrors.FiscalPeriodClosed, "Fiscal period is closed");

        // Validate entry date is within period
        if (!fiscalPeriod.ContainsDate(dto.EntryDate))
            throw new BusinessException(BusinessErrors.ValidationError, "Entry date is outside fiscal period");

        // Map DTO to Domain Entity
        var entry = JournalEntry.Create(
            entryDate: dto.EntryDate,
            fiscalPeriodId: dto.FiscalPeriodId,
            currency: dto.Currency,
            description: dto.Description,
            createdBy: createdBy,
            exchangeRate: dto.ExchangeRate
        );

        // Add items
        foreach (var itemDto in dto.Items)
        {
            var item = JournalItem.Create(
                accountId: itemDto.AccountId,
                debitAmount: itemDto.DebitAmount,
                creditAmount: itemDto.CreditAmount,
                createdBy: createdBy,
                partnerId: itemDto.PartnerId,
                exchangeRate: itemDto.ExchangeRate,
                description: itemDto.Description
            );

            // Validate partner for accounts 131/331
            var account = await _dbContext.Accounts.FirstOrDefaultAsync(a => a.Id == itemDto.AccountId, cancellationToken);
            if (account != null)
            {
                item.ValidatePartnerRequired(account.Code);
            }

            entry.AddItem(item);
        }

        // Check balance using Domain method
        if (!entry.CheckBalance())
        {
            throw new BusinessException(
                BusinessErrors.ImbalanceDetected,
                $"Entry is not balanced. Debit: {entry.TotalDebit:N4}, Credit: {entry.TotalCredit:N4}");
        }

        // Validate minimum lines
        if (!entry.HasValidLines())
        {
            throw new BusinessException(BusinessErrors.ValidationError, "Entry must have at least 2 lines with valid amounts");
        }

        // Save to database with Transaction
        await using var transaction = await _dbContext.Database.BeginTransactionAsync(cancellationToken);
        try
        {
            await _dbContext.JournalEntries.AddAsync(entry, cancellationToken);
            await _dbContext.SaveChangesAsync(cancellationToken);
            
            await transaction.CommitAsync(cancellationToken);
        }
        catch
        {
            await transaction.RollbackAsync(cancellationToken);
            throw;
        }

        return MapToResultDto(entry);
    }

    public async Task<JournalEntryResultDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        var entry = await _dbContext.JournalEntries
            .Include(e => e.Items)
            .FirstOrDefaultAsync(e => e.Id == id, cancellationToken);

        return entry == null ? null : MapToResultDto(entry);
    }

    public async Task<JournalEntryResultDto> PostAsync(Guid id, string postedBy, CancellationToken cancellationToken = default)
    {
        await using var transaction = await _dbContext.Database.BeginTransactionAsync(cancellationToken);
        try
        {
            var entry = await _dbContext.JournalEntries
                .Include(e => e.Items)
                .FirstOrDefaultAsync(e => e.Id == id, cancellationToken)
                ?? throw new BusinessException(BusinessErrors.ValidationError, "Journal entry not found");

            var isPeriodOpen = await _dbContext.FiscalPeriods
                .AnyAsync(p => p.Id == entry.FiscalPeriodId && p.IsOpen, cancellationToken);

            entry.Post(postedBy, _ => isPeriodOpen);

            await _dbContext.SaveChangesAsync(cancellationToken);
            await transaction.CommitAsync(cancellationToken);

            return MapToResultDto(entry);
        }
        catch
        {
            await transaction.RollbackAsync(cancellationToken);
            throw;
        }
    }

    public async Task<JournalEntryResultDto> VoidAsync(Guid id, string voidedBy, CancellationToken cancellationToken = default)
    {
        var entry = await _dbContext.JournalEntries
            .Include(e => e.Items)
            .FirstOrDefaultAsync(e => e.Id == id, cancellationToken)
            ?? throw new BusinessException(BusinessErrors.ValidationError, "Journal entry not found");

        entry.Void(voidedBy);

        await _dbContext.SaveChangesAsync(cancellationToken);

        return MapToResultDto(entry);
    }

    private static JournalEntryResultDto MapToResultDto(JournalEntry entry)
    {
        return new JournalEntryResultDto
        {
            Id = entry.Id,
            EntryNumber = entry.EntryNumber,
            EntryDate = entry.EntryDate,
            FiscalPeriodId = entry.FiscalPeriodId,
            Currency = entry.Currency,
            ExchangeRate = entry.ExchangeRate,
            Description = entry.Description,
            Status = (int)entry.Status,
            TotalDebit = entry.TotalDebit,
            TotalCredit = entry.TotalCredit,
            CreatedAt = entry.CreatedAt,
            CreatedBy = entry.CreatedBy,
            PostedAt = entry.PostedAt,
            PostedBy = entry.PostedBy,
            Items = entry.Items.Select(i => new JournalItemResultDto
            {
                Id = i.Id,
                AccountId = i.AccountId,
                PartnerId = i.PartnerId,
                DebitAmount = i.DebitAmount,
                CreditAmount = i.CreditAmount,
                BaseAmount = i.BaseAmount,
                ExchangeRate = i.ExchangeRate,
                Description = i.Description
            }).ToList()
        };
    }
}
