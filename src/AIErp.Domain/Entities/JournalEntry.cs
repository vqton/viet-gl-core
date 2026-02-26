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

    // Tax compliance fields per Circular 99/2025
    public string? InvoiceNumber { get; private set; }
    public DateOnly? InvoiceDate { get; private set; }
    public decimal? TaxRate { get; private set; }
    
    public DateTime CreatedAt { get; private set; }
    public string CreatedBy { get; private set; } = string.Empty;
    public DateTime LastModifiedAt { get; private set; }
    public string LastModifiedBy { get; private set; } = string.Empty;
    public Guid RowVersion { get; private set; } = Guid.NewGuid();

    public void RegenerateRowVersion() => RowVersion = Guid.NewGuid();

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
            throw new ArgumentException("Diễn giải không được để trống", nameof(description));

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
            throw new InvalidOperationException("Chỉ được thêm dòng khi chứng từ đang ở trạng thái nháp");

        item.SetJournalEntryId(Id);
        Items.Add(item);
        RecalculateTotals();
    }

    public void RemoveItem(Guid itemId)
    {
        if (Status != VoucherStatus.Draft)
            throw new InvalidOperationException("Chỉ được xóa dòng khi chứng từ đang ở trạng thái nháp");

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

    public void Post(string postedBy, Func<Guid, bool> isPeriodOpen, Func<Guid, Account?> getAccount = null!)
    {
        if (Status != VoucherStatus.Draft)
            throw new InvalidOperationException("Chỉ được ghi sổ khi chứng từ đang ở trạng thái nháp");

        if (!CheckBalance())
            throw new InvalidOperationException("Chứng từ không cân bằng - Tổng Nợ phải bằng Tổng Có");

        if (!HasValidLines())
            throw new InvalidOperationException("Chứng từ phải có ít nhất 2 dòng với số tiền hợp lệ");

        if (!isPeriodOpen(FiscalPeriodId))
            throw new InvalidOperationException("Kỳ kế toán đã đóng, không thể ghi sổ");

        if (getAccount != null)
        {
            foreach (var item in Items)
            {
                var account = getAccount(item.AccountId);
                if (account == null)
                    throw new InvalidOperationException($"Account with ID {item.AccountId} not found");
                
                if (!account.IsDetail)
                    throw new InvalidOperationException($"Cannot post to parent account {account.Code} ({account.Name}). Only leaf accounts are allowed per Circular 99/2025.");
            }
        }

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
            throw new InvalidOperationException("Chỉ được sửa chứng từ đang ở trạng thái nháp");

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

    public void SetInvoiceInfo(string? invoiceNumber, DateOnly? invoiceDate, decimal? taxRate)
    {
        if (Status != VoucherStatus.Draft)
            throw new InvalidOperationException("Chỉ được cập nhật thông tin hóa đơn khi chứng từ đang ở trạng thái nháp");

        InvoiceNumber = invoiceNumber?.Trim();
        InvoiceDate = invoiceDate;
        TaxRate = taxRate;
    }

    public bool IsVoided => Status == VoucherStatus.Void;
    public bool IsPosted => Status == VoucherStatus.Posted;
    public bool IsDraft => Status == VoucherStatus.Draft;
}
