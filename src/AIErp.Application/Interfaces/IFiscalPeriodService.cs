namespace AIErp.Application.Interfaces;

using AIErp.Application.DTOs;

public interface IFiscalPeriodService
{
    Task<IEnumerable<FiscalPeriodDto>> GetAllAsync(CancellationToken cancellationToken = default);
    Task<FiscalPeriodDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);
    Task<FiscalPeriodDto?> GetByYearPeriodAsync(int year, int period, CancellationToken cancellationToken = default);
    Task<FiscalPeriodDto?> GetCurrentPeriodAsync(CancellationToken cancellationToken = default);
    Task<FiscalPeriodDto> OpenAsync(Guid id, string openedBy, CancellationToken cancellationToken = default);
    Task<FiscalPeriodDto> CloseAsync(Guid id, string closedBy, CancellationToken cancellationToken = default);
}
