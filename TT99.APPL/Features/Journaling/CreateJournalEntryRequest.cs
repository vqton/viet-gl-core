// Thêm using này
using System.Text.Json.Serialization; 

public record CreateJournalEntryRequest
{
    public DateTime TransactionDate { get; init; }
    public string VoucherNumber { get; init; }
    public string Narration { get; init; }

    // Sử dụng [JsonPropertyName] để DTO C# (Entries) 
    // có thể liên kết với JSON key (ledgerEntries)
    [JsonPropertyName("ledgerEntries")]
    public List<LedgerEntryRequest> Entries { get; init; }
}

public record LedgerEntryRequest
{
    public string AccountNumber { get; init; }
    public string Description { get; init; }
    public decimal DebitAmount { get; init; }
    public decimal CreditAmount { get; init; }
}