using AIErp.Domain.ValueObjects;

namespace AIErp.Domain.Entities;

public class JournalItem
{
    public Guid Id { get; private set; }
    public Guid JournalEntryId { get; private set; }
    public Guid AccountId { get; private set; }
    public Guid? PartnerId { get; private set; }
    public decimal DebitAmount { get; private set; }
    public decimal CreditAmount { get; private set; }
    public decimal BaseAmount { get; private set; }
    public decimal ExchangeRate { get; private set; }
    public string? Description { get; private set; }
    
    public DateTime CreatedAt { get; private set; }
    public string CreatedBy { get; private set; } = string.Empty;
    public DateTime LastModifiedAt { get; private set; }
    public string LastModifiedBy { get; private set; } = string.Empty;

    public JournalEntry? JournalEntry { get; private set; }
    public Account? Account { get; private set; }
    public Partner? Partner { get; private set; }

    private JournalItem() { }

    public static JournalItem Create(
        Guid accountId,
        decimal debitAmount,
        decimal creditAmount,
        string createdBy,
        Guid? partnerId = null,
        decimal exchangeRate = 1.0m,
        string? description = null)
    {
        if (accountId == Guid.Empty)
            throw new ArgumentException("AccountId is required", nameof(accountId));
        if (debitAmount < 0 || creditAmount < 0)
            throw new ArgumentException("Amounts cannot be negative");
        if (debitAmount > 0 && creditAmount > 0)
            throw new ArgumentException("A line cannot have both Debit and Credit");

        var amount = debitAmount > 0 ? debitAmount : creditAmount;
        var baseAmount = amount * exchangeRate;

        var item = new JournalItem
        {
            Id = Guid.NewGuid(),
            AccountId = accountId,
            PartnerId = partnerId,
            DebitAmount = debitAmount,
            CreditAmount = creditAmount,
            BaseAmount = baseAmount,
            ExchangeRate = exchangeRate,
            Description = description?.Trim(),
            CreatedAt = DateTime.UtcNow,
            CreatedBy = createdBy,
            LastModifiedAt = DateTime.UtcNow,
            LastModifiedBy = createdBy
        };

        return item;
    }

    public void SetJournalEntryId(Guid journalEntryId)
    {
        JournalEntryId = journalEntryId;
    }

    public void ValidatePartnerRequired(string accountCode)
    {
        if (PartnerId == null && (accountCode.StartsWith("131") || accountCode.StartsWith("331")))
        {
            throw new InvalidOperationException($"Partner is required for account {accountCode}");
        }
    }

    public decimal GetAmount() => DebitAmount > 0 ? DebitAmount : CreditAmount;
}
