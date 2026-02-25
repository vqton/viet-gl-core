namespace AIErp.Application.Interfaces;

using AIErp.Application.DTOs;

public interface IAccountService
{
    Task<IEnumerable<AccountTreeDto>> GetFullTreeAsync(CancellationToken cancellationToken = default);
    Task<AccountDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);
    Task<IEnumerable<AccountDto>> GetAllAsync(CancellationToken cancellationToken = default);
    Task<AccountDto> CreateAsync(CreateAccountDto dto, string createdBy, CancellationToken cancellationToken = default);
}
