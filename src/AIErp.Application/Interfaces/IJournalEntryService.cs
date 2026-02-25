using AIErp.Application.DTOs;

namespace AIErp.Application.Interfaces;

public interface IJournalEntryService
{
    Task<JournalEntryResultDto> CreateAsync(JournalEntryDto dto, string createdBy, CancellationToken cancellationToken = default);
    Task<JournalEntryResultDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);
    Task<JournalEntryResultDto> PostAsync(Guid id, string postedBy, CancellationToken cancellationToken = default);
    Task<JournalEntryResultDto> VoidAsync(Guid id, string voidedBy, CancellationToken cancellationToken = default);
}
