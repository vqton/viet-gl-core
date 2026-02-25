namespace AIErp.Application.Interfaces;

using AIErp.Application.DTOs;

public interface IPartnerService
{
    Task<IEnumerable<PartnerDto>> GetAllAsync(CancellationToken cancellationToken = default);
    Task<PartnerDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);
    Task<PartnerDto> CreateAsync(CreatePartnerDto dto, string createdBy, CancellationToken cancellationToken = default);
    Task<PartnerDto> UpdateAsync(Guid id, UpdatePartnerDto dto, string modifiedBy, CancellationToken cancellationToken = default);
    Task DeleteAsync(Guid id, string deletedBy, CancellationToken cancellationToken = default);
}
