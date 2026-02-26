namespace AIErp.Application.Interfaces;

using AIErp.Application.DTOs;

public interface IReportingService
{
    Task<TrialBalanceDto> GetTrialBalanceAsync(DateTime startDate, DateTime endDate, CancellationToken cancellationToken = default);
    Task<GeneralLedgerDto> GetGeneralLedgerAsync(string accountCode, DateTime startDate, DateTime endDate, CancellationToken cancellationToken = default);
}
