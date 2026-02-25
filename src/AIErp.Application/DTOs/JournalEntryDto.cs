namespace AIErp.Application.DTOs;

public class JournalItemDto
{
    public Guid AccountId { get; set; }
    public Guid? PartnerId { get; set; }
    public decimal DebitAmount { get; set; }
    public decimal CreditAmount { get; set; }
    public decimal ExchangeRate { get; set; } = 1.0m;
    public string? Description { get; set; }
}

public class JournalEntryDto
{
    public DateOnly EntryDate { get; set; }
    public Guid FiscalPeriodId { get; set; }
    public string Currency { get; set; } = "VND";
    public decimal ExchangeRate { get; set; } = 1.0m;
    public string Description { get; set; } = string.Empty;
    public List<JournalItemDto> Items { get; set; } = [];
}
