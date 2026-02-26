namespace AIErp.Domain.Services;

using AIErp.Domain.Entities;
using AIErp.Domain.Enums;

public static class AccountingValidationService
{
    private static readonly HashSet<string> CashAccounts = new() { "111", "112", "113" };
    private static readonly HashSet<string> ReceivableAccounts = new() { "131", "138", "141" };
    private static readonly HashSet<string> PayableAccounts = new() { "331", "338", "341" };
    private static readonly HashSet<string> VatAccounts = new() { "3331" };

    private static readonly HashSet<string> PartnerRequiredAccounts = new()
    {
        "131", // Phải thu của khách hàng
        "138", // Phải thu khác
        "141", // Tạm ứng
        "331", // Phải trả cho người bán
        "338", // Phải trả khác
        "341", // Chi tạm ứng
    };

    public static void ValidateJournalEntry(JournalEntry entry, IDictionary<Guid, Account> accounts)
    {
        if (entry == null)
            throw new ArgumentNullException(nameof(entry));
        if (accounts == null)
            throw new ArgumentNullException(nameof(accounts));

        ValidateAccountPairing(entry, accounts);
        ValidatePartnerRequirements(entry, accounts);
        ValidateVatRequirements(entry, accounts);
    }

    private static void ValidateAccountPairing(JournalEntry entry, IDictionary<Guid, Account> accounts)
    {
        var debitAccounts = entry.Items.Where(i => i.DebitAmount > 0).ToList();
        var creditAccounts = entry.Items.Where(i => i.CreditAmount > 0).ToList();

        foreach (var item in debitAccounts)
        {
            if (!accounts.TryGetValue(item.AccountId, out var account))
                continue;

            var accountCode = account.Code;

            // Check if this is a self-debit (same account on both sides) - Nợ 111/Có 111
            var matchingCredit = creditAccounts.FirstOrDefault(c =>
                accounts.TryGetValue(c.AccountId, out var creditAccount) &&
                creditAccount.Code == accountCode);

            if (matchingCredit != null)
            {
                throw new InvalidOperationException(
                    $"Bút toán định khoản Nợ {accountCode}/Có {accountCode} không hợp lệ. Không được định khoản cùng một tài khoản.");
            }

            // Validate 511/111 - Revenue cannot be credited against cash directly per TT99
            if (accountCode.StartsWith("511") || accountCode.StartsWith("515"))
            {
                var hasCashCredit = creditAccounts.Any(c =>
                    accounts.TryGetValue(c.AccountId, out var creditAcc) &&
                    CashAccounts.Any(ca => creditAcc.Code.StartsWith(ca)));

                if (hasCashCredit)
                {
                    throw new InvalidOperationException(
                        $"Bút toán Nợ 511/Có 111 không đúng bản chất. Doanh thu phải được ghi nhận qua các tài khoản phải thu (131) hoặc tiền gửi (112).");
                }
            }
        }
    }

    private static void ValidatePartnerRequirements(JournalEntry entry, IDictionary<Guid, Account> accounts)
    {
        foreach (var item in entry.Items)
        {
            if (!accounts.TryGetValue(item.AccountId, out var account))
                continue;

            var accountCode = account.Code;

            if (PartnerRequiredAccounts.Any(pra => accountCode.StartsWith(pra)) && item.PartnerId == null)
            {
                throw new InvalidOperationException(
                    $"Tài khoản {accountCode} ({account.Name}) bắt buộc phải có thông tin Đối tượng (Khách hàng/Nhà cung cấp) theo Thông tư 99/2025.");
            }
        }
    }

    private static void ValidateVatRequirements(JournalEntry entry, IDictionary<Guid, Account> accounts)
    {
        var hasVatEntry = entry.Items.Any(i =>
            accounts.TryGetValue(i.AccountId, out var acc) &&
            VatAccounts.Any(va => acc.Code.StartsWith(va)) &&
            (i.DebitAmount > 0 || i.CreditAmount > 0));

        if (hasVatEntry && string.IsNullOrWhiteSpace(entry.InvoiceNumber))
        {
            throw new InvalidOperationException(
                "Các bút toán vào tài khoản Thuế GTGT (3331) bắt buộc phải có thông tin Số hóa đơn theo quy định.");
        }
    }

    public static bool RequiresPartner(string accountCode)
    {
        return PartnerRequiredAccounts.Any(pra => accountCode.StartsWith(pra));
    }
}
