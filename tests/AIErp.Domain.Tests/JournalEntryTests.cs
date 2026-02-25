using AIErp.Domain.Entities;
using FluentAssertions;

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
}
