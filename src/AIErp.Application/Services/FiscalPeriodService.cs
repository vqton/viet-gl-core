namespace AIErp.Application.Services;

using AIErp.Application.DTOs;
using AIErp.Application.Exceptions;
using AIErp.Application.Interfaces;
using AIErp.Domain.Entities;
using AIErp.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;

public class FiscalPeriodService(AppDbContext dbContext) : IFiscalPeriodService
{
    private readonly AppDbContext _dbContext = dbContext;

    public async Task<IEnumerable<FiscalPeriodDto>> GetAllAsync(CancellationToken cancellationToken = default)
    {
        var periods = await _dbContext.FiscalPeriods
            .OrderBy(p => p.Year)
            .ThenBy(p => p.Period)
            .ToListAsync(cancellationToken);

        return periods.Select(MapToDto);
    }

    public async Task<FiscalPeriodDto?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default)
    {
        var period = await _dbContext.FiscalPeriods
            .FirstOrDefaultAsync(p => p.Id == id, cancellationToken);

        return period == null ? null : MapToDto(period);
    }

    public async Task<FiscalPeriodDto?> GetByYearPeriodAsync(int year, int period, CancellationToken cancellationToken = default)
    {
        var periodEntity = await _dbContext.FiscalPeriods
            .FirstOrDefaultAsync(p => p.Year == year && p.Period == period, cancellationToken);

        return periodEntity == null ? null : MapToDto(periodEntity);
    }

    public async Task<FiscalPeriodDto?> GetCurrentPeriodAsync(CancellationToken cancellationToken = default)
    {
        var now = DateOnly.FromDateTime(DateTime.UtcNow);
        var period = await _dbContext.FiscalPeriods
            .FirstOrDefaultAsync(p => p.StartDate <= now && p.EndDate >= now, cancellationToken);

        return period == null ? null : MapToDto(period);
    }

    public async Task<FiscalPeriodDto> OpenAsync(Guid id, string openedBy, CancellationToken cancellationToken = default)
    {
        var period = await _dbContext.FiscalPeriods
            .FirstOrDefaultAsync(p => p.Id == id, cancellationToken)
            ?? throw new BusinessException(BusinessErrors.ValidationError, "Fiscal period not found");

        period.Open(openedBy);
        await _dbContext.SaveChangesAsync(cancellationToken);

        return MapToDto(period);
    }

    public async Task<FiscalPeriodDto> CloseAsync(Guid id, string closedBy, CancellationToken cancellationToken = default)
    {
        var period = await _dbContext.FiscalPeriods
            .FirstOrDefaultAsync(p => p.Id == id, cancellationToken)
            ?? throw new BusinessException(BusinessErrors.ValidationError, "Fiscal period not found");

        period.Close(closedBy);
        await _dbContext.SaveChangesAsync(cancellationToken);

        return MapToDto(period);
    }

    private static FiscalPeriodDto MapToDto(FiscalPeriod period)
    {
        return new FiscalPeriodDto
        {
            Id = period.Id,
            Year = period.Year,
            Period = period.Period,
            StartDate = period.StartDate,
            EndDate = period.EndDate,
            IsOpen = period.IsOpen,
            IsAdjustmentPeriod = period.IsAdjustmentPeriod,
            Description = period.Description
        };
    }
}
