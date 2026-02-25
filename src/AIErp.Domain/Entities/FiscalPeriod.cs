namespace AIErp.Domain.Entities;

public class FiscalPeriod
{
    public Guid Id { get; private set; }
    public int Year { get; private set; }
    public int Period { get; private set; }
    public DateOnly StartDate { get; private set; }
    public DateOnly EndDate { get; private set; }
    public bool IsOpen { get; private set; }
    public bool IsAdjustmentPeriod { get; private set; }
    public string? Description { get; private set; }
    
    public DateTime CreatedAt { get; private set; }
    public string CreatedBy { get; private set; } = string.Empty;
    public DateTime LastModifiedAt { get; private set; }
    public string LastModifiedBy { get; private set; } = string.Empty;
    public Guid RowVersion { get; private set; } = Guid.NewGuid();

    public void RegenerateRowVersion() => RowVersion = Guid.NewGuid();

    private FiscalPeriod() { }

    public static FiscalPeriod Create(
        int year,
        int period,
        DateOnly startDate,
        DateOnly endDate,
        string createdBy,
        bool isAdjustmentPeriod = false,
        string? description = null)
    {
        if (year < 1900 || year > 9999)
            throw new ArgumentException("Invalid year", nameof(year));
        if (period < 0 || period > 13)
            throw new ArgumentException("Period must be 0-13 (0=yearly)", nameof(period));
        if (startDate > endDate)
            throw new ArgumentException("StartDate must be before EndDate");

        var fiscalPeriod = new FiscalPeriod
        {
            Id = Guid.NewGuid(),
            Year = year,
            Period = period,
            StartDate = startDate,
            EndDate = endDate,
            IsOpen = false,
            IsAdjustmentPeriod = isAdjustmentPeriod,
            Description = description?.Trim(),
            CreatedAt = DateTime.UtcNow,
            CreatedBy = createdBy,
            LastModifiedAt = DateTime.UtcNow,
            LastModifiedBy = createdBy
        };

        return fiscalPeriod;
    }

    public void Open(string modifiedBy)
    {
        if (IsOpen)
            throw new InvalidOperationException("Period is already open");

        IsOpen = true;
        LastModifiedAt = DateTime.UtcNow;
        LastModifiedBy = modifiedBy;
    }

    public void Close(string modifiedBy)
    {
        if (!IsOpen)
            throw new InvalidOperationException("Period is already closed");

        IsOpen = false;
        LastModifiedAt = DateTime.UtcNow;
        LastModifiedBy = modifiedBy;
    }

    public bool ContainsDate(DateOnly date) => date >= StartDate && date <= EndDate;
}
