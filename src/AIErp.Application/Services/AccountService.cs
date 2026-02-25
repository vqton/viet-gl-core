namespace AIErp.Application.Services;

using AIErp.Application.DTOs;
using AIErp.Application.Exceptions;
using AIErp.Application.Interfaces;
using AIErp.Domain.Entities;
using AIErp.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;

public class AccountService(AppDbContext dbContext) : IAccountService
{
    private readonly AppDbContext _dbContext = dbContext;

    public async Task<IEnumerable<AccountDto>> GetAllAsync(CancellationToken cancellationToken = default)
    {
        var accounts = await _dbContext.Accounts
            .OrderBy(a => a.Code)
            .ToListAsync(cancellationToken);

        return accounts.Select(MapToDto);
    }

    public async Task<AccountDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        var account = await _dbContext.Accounts
            .FirstOrDefaultAsync(a => a.Id == id, cancellationToken);

        return account == null ? null : MapToDto(account);
    }

    public async Task<IEnumerable<AccountTreeDto>> GetFullTreeAsync(CancellationToken cancellationToken = default)
    {
        var allAccounts = await _dbContext.Accounts
            .OrderBy(a => a.Code)
            .ToListAsync(cancellationToken);

        var accountDtos = allAccounts.Select(MapToTreeDto).ToList();

        var lookup = accountDtos.ToDictionary(a => a.Id);
        var roots = new List<AccountTreeDto>();

        foreach (var account in accountDtos)
        {
            if (account.ParentId == null)
            {
                roots.Add(account);
            }
            else if (lookup.TryGetValue(account.ParentId.Value, out var parent))
            {
                parent.Children.Add(account);
            }
        }

        return roots;
    }

    public async Task<AccountDto> CreateAsync(CreateAccountDto dto, string createdBy, CancellationToken cancellationToken = default)
    {
        Account.ValidateCode(dto.Code);

        var exists = await _dbContext.Accounts
            .AnyAsync(a => a.Code == dto.Code, cancellationToken);

        if (exists)
            throw new BusinessException(BusinessErrors.ValidationError, $"Account code '{dto.Code}' already exists");

        if (dto.ParentId.HasValue)
        {
            var parent = await _dbContext.Accounts
                .FirstOrDefaultAsync(a => a.Id == dto.ParentId, cancellationToken);

            if (parent == null)
                throw new BusinessException(BusinessErrors.ValidationError, "Parent account not found");

            if (!parent.IsDetail)
                throw new BusinessException(BusinessErrors.ValidationError, "Cannot create child account under a non-detail (parent) account");
        }

        var account = Account.Create(
            code: dto.Code,
            name: dto.Name,
            type: dto.Type,
            normalBalance: dto.NormalBalance,
            isDetail: dto.IsDetail,
            parentId: dto.ParentId,
            createdBy: createdBy,
            description: dto.Description
        );

        await _dbContext.Accounts.AddAsync(account, cancellationToken);
        await _dbContext.SaveChangesAsync(cancellationToken);

        return MapToDto(account);
    }

    private static AccountDto MapToDto(Account account)
    {
        return new AccountDto
        {
            Id = account.Id,
            Code = account.Code,
            Name = account.Name,
            Type = account.Type,
            NormalBalance = account.NormalBalance,
            IsDetail = account.IsDetail,
            ParentId = account.ParentId,
            IsActive = account.IsActive,
            Description = account.Description
        };
    }

    private static AccountTreeDto MapToTreeDto(Account account)
    {
        return new AccountTreeDto
        {
            Id = account.Id,
            Code = account.Code,
            Name = account.Name,
            Type = account.Type,
            NormalBalance = account.NormalBalance,
            IsDetail = account.IsDetail,
            ParentId = account.ParentId,
            IsActive = account.IsActive,
            Description = account.Description,
            Children = new List<AccountTreeDto>()
        };
    }
}
