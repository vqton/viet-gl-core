namespace AIErp.Domain.Services;

using AIErp.Domain.Entities;

public static class AccountingValidationService
{
    private static readonly HashSet<string> PartnerRequiredAccounts = new()
    {
        "131", // Phải thu của khách hàng
        "331", // Phải trả cho người bán
    };

    public static void ValidateJournalEntry(JournalEntry entry, IDictionary<Guid, Account> accounts)
    {
        foreach (var item in entry.Items)
        {
            if (!accounts.TryGetValue(item.AccountId, out var account))
                continue;

            if (PartnerRequiredAccounts.Contains(account.Code) && item.PartnerId == null)
            {
                throw new InvalidOperationException(
                    $"Tài khoản {account.Code} ({account.Name}) yêu cầu phải có Đối tượng (Partner). Vui lòng chọn Khách hàng hoặc Nhà cung cấp.");
            }
        }
    }

    public static bool RequiresPartner(string accountCode)
    {
        return PartnerRequiredAccounts.Contains(accountCode);
    }
}
