namespace AIErp.Application.Interfaces;

using AIErp.Application.DTOs;

public interface IAccountService
{
    Task<IEnumerable<AccountTreeDto>> GetFullTreeAsync(CancellationToken cancellationToken = default);
    Task<AccountDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);
    Task<AccountDto?> GetByCodeAsync(string code, CancellationToken cancellationToken = default);
    Task<IEnumerable<AccountDto>> GetAllAsync(CancellationToken cancellationToken = default);
    Task<IEnumerable<AccountDto>> SearchAsync(string? searchTerm, bool? isDetail, CancellationToken cancellationToken = default);
    Task<AccountDto> CreateAsync(CreateAccountDto dto, string createdBy, CancellationToken cancellationToken = default);
    Task<AccountDto> UpdateAsync(Guid id, UpdateAccountDto dto, string modifiedBy, CancellationToken cancellationToken = default);
    Task DeactivateAsync(Guid id, string modifiedBy, CancellationToken cancellationToken = default);
    Task ActivateAsync(Guid id, string modifiedBy, CancellationToken cancellationToken = default);
}
