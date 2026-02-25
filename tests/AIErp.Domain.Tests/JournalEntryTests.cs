using AIErp.Domain.Entities;
using AIErp.Domain.Enums;
using FluentAssertions;
using DomainEnums = AIErp.Domain.Enums;

namespace AIErp.Domain.Tests;

public class JournalEntryTests
{
    private readonly Guid _fiscalPeriodId = Guid.NewGuid();
    private readonly string _testUser = "testuser";

    [Fact]
    public void Should_BeBalanced_When_SumDebitEqualsSumCredit()
    {
        // Arrange: Create a journal entry with balanced debit and credit
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Balanced Test Entry",
            _testUser
        );

        // Add debit line
        entry.AddItem(JournalItem.Create(
            Guid.NewGuid(),
            1000m,
            0,
            _testUser
        ));

        // Add credit line
        entry.AddItem(JournalItem.Create(
            Guid.NewGuid(),
            0,
            1000m,
            _testUser
        ));

        // Act: Check balance
        bool isBalanced = entry.CheckBalance();

        // Assert: Should be balanced
        isBalanced.Should().BeTrue();
    }

    [Fact]
    public void Should_NotBeBalanced_When_SumDebitDiffersFromSumCredit()
    {
        // Arrange: Create a journal entry with imbalanced debit and credit
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Imbalanced Test Entry",
            _testUser
        );

        // Add debit line: 1000
        entry.AddItem(JournalItem.Create(
            Guid.NewGuid(),
            1000m,
            0,
            _testUser
        ));

        // Add credit line: 800 (not equal to debit)
        entry.AddItem(JournalItem.Create(
            Guid.NewGuid(),
            0,
            800m,
            _testUser
        ));

        // Act: Check balance
        bool isBalanced = entry.CheckBalance();

        // Assert: Should NOT be balanced
        isBalanced.Should().BeFalse();
    }

    [Fact]
    public void Should_FailToPost_When_EntryIsImbalanced()
    {
        // Arrange: Create an imbalanced journal entry
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Imbalanced Entry for Posting",
            _testUser
        );

        // Add imbalanced lines (Debit: 1000, Credit: 800)
        entry.AddItem(JournalItem.Create(
            Guid.NewGuid(),
            1000m,
            0,
            _testUser
        ));
        entry.AddItem(JournalItem.Create(
            Guid.NewGuid(),
            0,
            800m,
            _testUser
        ));

        // Act & Assert: Posting should throw an exception
        var act = () => entry.Post(_testUser, periodId => true);
        
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*not balanced*");
    }

    [Fact]
    public void Should_RequirePartner_For_Account131()
    {
        // Arrange: Create a journal item for account 131 without PartnerId
        var accountId = Guid.NewGuid();
        var item = JournalItem.Create(
            accountId,
            1000m,
            0,
            _testUser,
            partnerId: null // No partner!
        );

        // Act & Assert: Validation should throw because account 131 requires partner
        var act = () => item.ValidatePartnerRequired("131");
        
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*Partner is required*");
    }

    [Fact]
    public void Should_ThrowException_When_Posting_To_Parent_Account()
    {
        // Arrange: Create parent account (not detail)
        var parentAccountId = Guid.NewGuid();
        var parentAccount = Account.Create(
            "111",
            "Tiền",
            AccountType.Asset,
            Domain.Enums.NormalBalance.Debit,
            isDetail: false, // Parent account
            parentId: null,
            createdBy: _testUser
        );
        
        // Use reflection to set the Id since Create generates a new one
        var parentAccountWithId = Account.Create(
            "111",
            "Tiền",
            AccountType.Asset,
            Domain.Enums.NormalBalance.Debit,
            isDetail: false,
            parentId: null,
            createdBy: _testUser
        );

        var leafAccount = Account.Create(
            "1111",
            "Tiền Việt Nam",
            AccountType.Asset,
            Domain.Enums.NormalBalance.Debit,
            isDetail: true,
            parentId: parentAccountWithId.Id,
            createdBy: _testUser
        );

        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Test Post to Parent Account",
            _testUser
        );

        // Add line with parent account (not leaf)
        entry.AddItem(JournalItem.Create(
            parentAccountWithId.Id,
            1000m,
            0,
            _testUser
        ));
        entry.AddItem(JournalItem.Create(
            leafAccount.Id,
            0,
            1000m,
            _testUser
        ));

        // Act & Assert: Posting should throw because parent account is used
        var act = () => entry.Post(
            _testUser, 
            periodId => true,
            accountId => accountId == parentAccountWithId.Id ? parentAccountWithId : leafAccount);

        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*parent account*");
    }

    [Fact]
    public void Should_Succeed_When_Posting_To_Leaf_Account_Only()
    {
        // Arrange: Create leaf accounts only
        var leafAccount1 = Account.Create(
            "1111",
            "Tiền Việt Nam",
            AccountType.Asset,
            Domain.Enums.NormalBalance.Debit,
            isDetail: true,
            parentId: null,
            createdBy: _testUser
        );

        var leafAccount2 = Account.Create(
            "1311",
            "Phải thu khách hàng",
            AccountType.Asset,
            Domain.Enums.NormalBalance.Debit,
            isDetail: true,
            parentId: null,
            createdBy: _testUser
        );

        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Test Post to Leaf Accounts",
            _testUser
        );

        entry.AddItem(JournalItem.Create(
            leafAccount1.Id,
            1000m,
            0,
            _testUser
        ));
        entry.AddItem(JournalItem.Create(
            leafAccount2.Id,
            0,
            1000m,
            _testUser
        ));

        // Act & Assert: Posting should succeed with leaf accounts only
        var act = () => entry.Post(
            _testUser,
            periodId => true,
            accountId => accountId == leafAccount1.Id ? leafAccount1 : leafAccount2);

        act.Should().NotThrow();
        entry.Status.Should().Be(Domain.Enums.VoucherStatus.Posted);
    }
}
