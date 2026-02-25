namespace AIErp.Application.DTOs;

public class FiscalPeriodDto
{
    public Guid Id { get; set; }
    public int Year { get; set; }
    public int Period { get; set; }
    public DateOnly StartDate { get; set; }
    public DateOnly EndDate { get; set; }
    public bool IsOpen { get; set; }
    public bool IsAdjustmentPeriod { get; set; }
    public string? Description { get; set; }
}
