using AIErp.Domain.Enums;
using AIErp.Domain.Entities;

namespace AIErp.Domain.Entities;

public class JournalEntry
{
    public Guid Id { get; private set; }
    public string EntryNumber { get; private set; } = string.Empty;
    public DateOnly EntryDate { get; private set; }
    public Guid FiscalPeriodId { get; private set; }
    public string Currency { get; private set; } = "VND";
    public decimal ExchangeRate { get; private set; } = 1.0m;
    public string Description { get; private set; } = string.Empty;
    public VoucherStatus Status { get; private set; }
    public decimal TotalDebit { get; private set; }
    public decimal TotalCredit { get; private set; }
    
    public DateTime? PostedAt { get; private set; }
    public string? PostedBy { get; private set; }
    public DateTime? VoidedAt { get; private set; }
    public string? VoidedBy { get; private set; }
    public Guid? OriginalEntryId { get; private set; }
    
    public DateTime CreatedAt { get; private set; }
    public string CreatedBy { get; private set; } = string.Empty;
    public DateTime LastModifiedAt { get; private set; }
    public string LastModifiedBy { get; private set; } = string.Empty;

    public FiscalPeriod? FiscalPeriod { get; private set; }
    public ICollection<JournalItem> Items { get; private set; } = new List<JournalItem>();

    private JournalEntry() { }

    public static JournalEntry Create(
        DateOnly entryDate,
        Guid fiscalPeriodId,
        string currency,
        string description,
        string createdBy,
        decimal exchangeRate = 1.0m,
        string? entryNumber = null)
    {
        if (string.IsNullOrWhiteSpace(description))
            throw new ArgumentException("Description is required", nameof(description));

        var entry = new JournalEntry
        {
            Id = Guid.NewGuid(),
            EntryNumber = entryNumber ?? GenerateEntryNumber(),
            EntryDate = entryDate,
            FiscalPeriodId = fiscalPeriodId,
            Currency = currency?.ToUpperInvariant() ?? "VND",
            ExchangeRate = exchangeRate,
            Description = description.Trim(),
            Status = VoucherStatus.Draft,
            TotalDebit = 0,
            TotalCredit = 0,
            CreatedAt = DateTime.UtcNow,
            CreatedBy = createdBy,
            LastModifiedAt = DateTime.UtcNow,
            LastModifiedBy = createdBy
        };

        return entry;
    }

    public void AddItem(JournalItem item)
    {
        if (Status != VoucherStatus.Draft)
            throw new InvalidOperationException("Cannot add items to a non-draft entry");

        item.SetJournalEntryId(Id);
        Items.Add(item);
        RecalculateTotals();
    }

    public void RemoveItem(Guid itemId)
    {
        if (Status != VoucherStatus.Draft)
            throw new InvalidOperationException("Cannot remove items from a non-draft entry");

        var item = Items.FirstOrDefault(i => i.Id == itemId);
        if (item != null)
        {
            Items.Remove(item);
            RecalculateTotals();
        }
    }

    private void RecalculateTotals()
    {
        TotalDebit = Items.Sum(i => i.DebitAmount);
        TotalCredit = Items.Sum(i => i.CreditAmount);
    }

    public bool CheckBalance()
    {
        return Math.Abs(TotalDebit - TotalCredit) == 0;
    }

    public bool HasValidLines()
    {
        return Items.Count >= 2 && Items.All(i => i.DebitAmount > 0 || i.CreditAmount > 0);
    }

    public void Post(string postedBy, Func<Guid, bool> isPeriodOpen)
    {
        if (Status != VoucherStatus.Draft)
            throw new InvalidOperationException("Only draft entries can be posted");

        if (!CheckBalance())
            throw new InvalidOperationException("Entry is not balanced - Debit must equal Credit");

        if (!HasValidLines())
            throw new InvalidOperationException("Entry must have at least 2 lines with valid amounts");

        if (!isPeriodOpen(FiscalPeriodId))
            throw new InvalidOperationException("Fiscal period is not open for posting");

        Status = VoucherStatus.Posted;
        PostedAt = DateTime.UtcNow;
        PostedBy = postedBy;
        LastModifiedAt = DateTime.UtcNow;
        LastModifiedBy = postedBy;
    }

    public void Void(string voidedBy)
    {
        if (Status == VoucherStatus.Void)
            throw new InvalidOperationException("Entry is already voided");

        if (Status != VoucherStatus.Draft && Status != VoucherStatus.Posted)
            throw new InvalidOperationException("Cannot void entry in current status");

        Status = VoucherStatus.Void;
        VoidedAt = DateTime.UtcNow;
        VoidedBy = voidedBy;
        LastModifiedAt = DateTime.UtcNow;
        LastModifiedBy = voidedBy;
    }

    public void UpdateDescription(string description, string modifiedBy)
    {
        if (Status != VoucherStatus.Draft)
            throw new InvalidOperationException("Only draft entries can be modified");

        if (string.IsNullOrWhiteSpace(description))
            throw new ArgumentException("Description is required", nameof(description));

        Description = description.Trim();
        LastModifiedAt = DateTime.UtcNow;
        LastModifiedBy = modifiedBy;
    }

    private static string GenerateEntryNumber()
    {
        return $"JE/{DateTime.UtcNow:yyyyMMdd}/{Guid.NewGuid().ToString()[..8].ToUpper()}";
    }
}
