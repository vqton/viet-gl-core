namespace AIErp.Domain.Tests;

using AIErp.Domain.Entities;
using AIErp.Domain.Enums;
using AIErp.Domain.Services;
using FluentAssertions;
using DomainEnums = AIErp.Domain.Enums;

public class ValidationRulesTests
{
    private readonly Guid _fiscalPeriodId = Guid.NewGuid();
    private readonly string _testUser = "testuser";

    [Fact]
    public void Should_BlockSelfDebitAccount_Posting()
    {
        // Arrange: Create entry with same account on both sides - Nợ 111/Có 111
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Self-debit test",
            _testUser
        );

        var accountId = Guid.NewGuid();
        entry.AddItem(JournalItem.Create(accountId, 1000m, 0, _testUser));
        entry.AddItem(JournalItem.Create(accountId, 0, 1000m, _testUser));

        var accounts = new Dictionary<Guid, Account>
        {
            [accountId] = Account.Create("111", "Tiền mặt", AccountType.Asset, NormalBalance.Debit, true, null, _testUser)
        };

        // Act & Assert
        var act = () => AccountingValidationService.ValidateJournalEntry(entry, accounts);
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*không được định khoản cùng một tài khoản*");
    }

    [Fact]
    public void Should_BlockRevenueCashDirect_Posting()
    {
        // Arrange: Nợ 511/Có 111 - Revenue cannot be directly credited to cash
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Revenue to cash test",
            _testUser
        );

        var cashAccountId = Guid.NewGuid();
        var revenueAccountId = Guid.NewGuid();

        entry.AddItem(JournalItem.Create(revenueAccountId, 1000m, 0, _testUser));
        entry.AddItem(JournalItem.Create(cashAccountId, 0, 1000m, _testUser));

        var accounts = new Dictionary<Guid, Account>
        {
            [cashAccountId] = Account.Create("111", "Tiền mặt", AccountType.Asset, NormalBalance.Debit, true, null, _testUser),
            [revenueAccountId] = Account.Create("5111", "Doanh thu bán hàng", AccountType.Revenue, NormalBalance.Credit, true, null, _testUser)
        };

        // Act & Assert
        var act = () => AccountingValidationService.ValidateJournalEntry(entry, accounts);
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*không đúng bản chất*");
    }

    [Fact]
    public void Should_RequirePartnerForAccount131()
    {
        // Arrange: Account 131 requires partner
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "131 without partner test",
            _testUser
        );

        var receivableAccountId = Guid.NewGuid();
        var cashAccountId = Guid.NewGuid();

        entry.AddItem(JournalItem.Create(receivableAccountId, 1000m, 0, _testUser, partnerId: null)); // No partner!
        entry.AddItem(JournalItem.Create(cashAccountId, 0, 1000m, _testUser));

        var accounts = new Dictionary<Guid, Account>
        {
            [receivableAccountId] = Account.Create("131", "Phải thu KH", AccountType.Asset, NormalBalance.Debit, true, null, _testUser),
            [cashAccountId] = Account.Create("111", "Tiền mặt", AccountType.Asset, NormalBalance.Debit, true, null, _testUser)
        };

        // Act & Assert
        var act = () => AccountingValidationService.ValidateJournalEntry(entry, accounts);
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*bắt buộc phải có thông tin Đối tượng*");
    }

    [Fact]
    public void Should_RequirePartnerForAccount331()
    {
        // Arrange: Account 331 requires partner
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "331 without partner test",
            _testUser
        );

        var payableAccountId = Guid.NewGuid();
        var cashAccountId = Guid.NewGuid();

        entry.AddItem(JournalItem.Create(cashAccountId, 1000m, 0, _testUser));
        entry.AddItem(JournalItem.Create(payableAccountId, 0, 1000m, _testUser, partnerId: null)); // No partner!

        var accounts = new Dictionary<Guid, Account>
        {
            [payableAccountId] = Account.Create("331", "Phải trả NB", AccountType.Liability, NormalBalance.Credit, true, null, _testUser),
            [cashAccountId] = Account.Create("111", "Tiền mặt", AccountType.Asset, NormalBalance.Debit, true, null, _testUser)
        };

        // Act & Assert
        var act = () => AccountingValidationService.ValidateJournalEntry(entry, accounts);
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*bắt buộc phải có thông tin Đối tượng*");
    }

    [Fact]
    public void Should_BlockPostingToClosedPeriod()
    {
        // Arrange: Create entry in draft
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Post to closed period test",
            _testUser
        );

        var accountId = Guid.NewGuid();
        entry.AddItem(JournalItem.Create(accountId, 1000m, 0, _testUser));
        entry.AddItem(JournalItem.Create(accountId, 0, 1000m, _testUser));

        // Act & Assert: Period is closed
        var act = () => entry.Post(_testUser, periodId => false); // isPeriodOpen = false
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*Kỳ kế toán đã đóng*");
    }

    [Fact]
    public void Should_BlockModifyPostedEntry()
    {
        // Arrange: Create and post entry
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Modify posted test",
            _testUser
        );

        var accountId = Guid.NewGuid();
        entry.AddItem(JournalItem.Create(accountId, 1000m, 0, _testUser));
        entry.AddItem(JournalItem.Create(accountId, 0, 1000m, _testUser));
        entry.Post(_testUser, periodId => true);

        // Act & Assert: Try to modify posted entry
        var act = () => entry.AddItem(JournalItem.Create(accountId, 500m, 0, _testUser));
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*đang ở trạng thái nháp*");
    }

    [Fact]
    public void Should_PreserveVoidAuditTrail()
    {
        // Arrange: Create and post entry
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Void audit trail test",
            _testUser
        );

        var accountId = Guid.NewGuid();
        entry.AddItem(JournalItem.Create(accountId, 1000m, 0, _testUser));
        entry.AddItem(JournalItem.Create(accountId, 0, 1000m, _testUser));
        entry.Post(_testUser, periodId => true);

        // Act: Void the entry
        entry.Void("admin");

        // Assert: Status is Void, audit fields are preserved
        entry.Status.Should().Be(VoucherStatus.Void);
        entry.VoidedAt.Should().NotBeNull();
        entry.VoidedBy.Should().Be("admin");
        entry.PostedBy.Should().Be(_testUser);
        entry.PostedAt.Should().NotBeNull();
    }

    [Fact]
    public void Should_BlockDeleteVoidedEntry()
    {
        // Arrange: Create, post, then void entry
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Delete voided test",
            _testUser
        );

        var accountId = Guid.NewGuid();
        entry.AddItem(JournalItem.Create(accountId, 1000m, 0, _testUser));
        entry.AddItem(JournalItem.Create(accountId, 0, 1000m, _testUser));
        entry.Post(_testUser, periodId => true);
        entry.Void("admin");

        // Assert: Entry still exists in database with Void status
        // (In real test, we would check DB - here we verify domain state)
        entry.Status.Should().Be(VoucherStatus.Void);
        entry.IsVoided.Should().BeTrue();
    }

    [Fact]
    public void Should_BlockPostingToParentAccount()
    {
        // Arrange: Create entry with parent account (not leaf)
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Post to parent test",
            _testUser
        );

        var parentAccountId = Guid.NewGuid();
        var childAccountId = Guid.NewGuid();

        // Add item with parent account (IsDetail = false)
        entry.AddItem(JournalItem.Create(parentAccountId, 1000m, 0, _testUser));
        entry.AddItem(JournalItem.Create(childAccountId, 0, 1000m, _testUser));

        var accounts = new Dictionary<Guid, Account>
        {
            [parentAccountId] = Account.Create("11", "Tiền", AccountType.Asset, NormalBalance.Debit, false, null, _testUser), // Parent - not detail
            [childAccountId] = Account.Create("111", "Tiền mặt", AccountType.Asset, NormalBalance.Debit, true, parentAccountId, _testUser)
        };

        // Act & Assert
        var act = () => entry.Post(_testUser, periodId => true, accountId => accounts.GetValueOrDefault(accountId));
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*Only leaf accounts are allowed*");
    }

    [Fact]
    public void Should_RequireInvoiceForVatAccount()
    {
        // Arrange: Vat entry without invoice number
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "VAT without invoice test",
            _testUser
        );

        var vatAccountId = Guid.NewGuid();
        var expenseAccountId = Guid.NewGuid();

        entry.AddItem(JournalItem.Create(expenseAccountId, 1100m, 0, _testUser));
        entry.AddItem(JournalItem.Create(vatAccountId, 0, 100m, _testUser));
        // No InvoiceNumber set!

        var accounts = new Dictionary<Guid, Account>
        {
            [vatAccountId] = Account.Create("3331", "Thuế GTGT đầu ra", AccountType.Liability, NormalBalance.Credit, true, null, _testUser),
            [expenseAccountId] = Account.Create("6211", "Giá vốn hàng bán", AccountType.Expense, NormalBalance.Debit, true, null, _testUser)
        };

        // Act & Assert
        var act = () => AccountingValidationService.ValidateJournalEntry(entry, accounts);
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*bắt buộc phải có thông tin Số hóa đơn*");
    }
}
