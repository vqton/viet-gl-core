namespace AIErp.Application.DTOs;

public class JournalItemResultDto
{
    public Guid Id { get; set; }
    public Guid AccountId { get; set; }
    public Guid? PartnerId { get; set; }
    public decimal DebitAmount { get; set; }
    public decimal CreditAmount { get; set; }
    public decimal BaseAmount { get; set; }
    public decimal ExchangeRate { get; set; }
    public string? Description { get; set; }
}

public class JournalEntryResultDto
{
    public Guid Id { get; set; }
    public string EntryNumber { get; set; } = string.Empty;
    public DateOnly EntryDate { get; set; }
    public Guid FiscalPeriodId { get; set; }
    public string Currency { get; set; } = "VND";
    public decimal ExchangeRate { get; set; }
    public string Description { get; set; } = string.Empty;
    public int Status { get; set; }
    public decimal TotalDebit { get; set; }
    public decimal TotalCredit { get; set; }
    public DateTime CreatedAt { get; set; }
    public string CreatedBy { get; set; } = string.Empty;
    public DateTime? PostedAt { get; set; }
    public string? PostedBy { get; set; }
    public List<JournalItemResultDto> Items { get; set; } = [];
}
