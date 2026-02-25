using AIErp.Domain.Entities;
using AIErp.Domain.Enums;
using FluentAssertions;
using Xunit;

namespace AIErp.Domain.Tests.Entities;

public class JournalEntryTests
{
    private readonly Guid _fiscalPeriodId = Guid.NewGuid();
    private readonly string _testUser = "testuser";

    #region Create Tests

    [Fact]
    public void Create_WithValidData_ShouldCreateDraftEntry()
    {
        // Arrange & Act
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Test Entry",
            _testUser
        );

        // Assert
        entry.Should().NotBeNull();
        entry.Status.Should().Be(VoucherStatus.Draft);
        entry.TotalDebit.Should().Be(0);
        entry.TotalCredit.Should().Be(0);
        entry.Currency.Should().Be("VND");
    }

    [Fact]
    public void Create_WithCustomCurrency_ShouldUseProvidedCurrency()
    {
        // Arrange & Act
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "USD",
            "USD Entry",
            _testUser
        );

        // Assert
        entry.Currency.Should().Be("USD");
    }

    [Fact]
    public void Create_WithNullDescription_ShouldThrowArgumentException()
    {
        // Arrange & Act
        var action = () => JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            null!,
            _testUser
        );

        // Assert
        action.Should().Throw<ArgumentException>()
            .WithMessage("*Description*");
    }

    [Fact]
    public void Create_WithEmptyDescription_ShouldThrowArgumentException()
    {
        // Arrange & Act
        var action = () => JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "   ",
            _testUser
        );

        // Assert
        action.Should().Throw<ArgumentException>();
    }

    #endregion

    #region Balance Check Tests

    [Fact]
    public void CheckBalance_WhenBalanced_ReturnsTrue()
    {
        // Arrange
        var entry = CreateBalancedEntry(1000m, 1000m);

        // Act
        bool result = entry.CheckBalance();

        // Assert
        result.Should().BeTrue();
    }

    [Fact]
    public void CheckBalance_WhenImbalanced_ReturnsFalse()
    {
        // Arrange
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Imbalanced Entry",
            _testUser
        );

        entry.AddItem(JournalItem.Create(
            Guid.NewGuid(),
            1000m,
            0,
            _testUser
        ));
        entry.AddItem(JournalItem.Create(
            Guid.NewGuid(),
            0,
            950m,
            _testUser
        ));

        // Act
        bool result = entry.CheckBalance();

        // Assert
        result.Should().BeFalse();
    }

    [Fact]
    public void CheckBalance_WhenBothSidesZero_ReturnsTrue()
    {
        // Arrange
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Zero Entry",
            _testUser
        );

        // Act
        bool result = entry.CheckBalance();

        // Assert
        result.Should().BeTrue();
    }

    #endregion

    #region Imbalanced Voucher - Prevent Posting (Scenario 1)

    [Fact]
    public void Post_WhenImbalanced_ShouldThrowInvalidOperationException()
    {
        // Arrange
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Imbalanced Entry",
            _testUser
        );

        // Debit: 1000, Credit: 950 = Imbalanced!
        entry.AddItem(JournalItem.Create(
            Guid.NewGuid(),
            1000m,
            0,
            _testUser
        ));
        entry.AddItem(JournalItem.Create(
            Guid.NewGuid(),
            0,
            950m,
            _testUser
        ));

        // Act
        var action = () => entry.Post(_testUser, periodId => true);

        // Assert
        action.Should().Throw<InvalidOperationException>()
            .WithMessage("*not balanced*");
    }

    [Fact]
    public void Post_WhenBalanced_ShouldSucceed()
    {
        // Arrange
        var entry = CreateBalancedEntry(1000m, 1000m);

        // Act
        entry.Post(_testUser, periodId => true);

        // Assert
        entry.Status.Should().Be(VoucherStatus.Posted);
        entry.PostedAt.Should().NotBeNull();
        entry.PostedBy.Should().Be(_testUser);
    }

    #endregion

    #region Zero Amount Handling (Scenario 2)

    [Fact]
    public void Create_WithZeroAmount_ShouldSucceed()
    {
        // Arrange & Act - Zero amounts are allowed at JournalItem level
        // Validation happens at JournalEntry.HasValidLines() level
        var item = JournalItem.Create(
            Guid.NewGuid(),
            0m,
            0m,
            _testUser
        );

        // Assert - Item is created (amount = 0)
        item.DebitAmount.Should().Be(0);
        item.CreditAmount.Should().Be(0);
    }

    [Fact]
    public void HasValidLines_WithZeroAmountLine_ShouldReturnFalse()
    {
        // Arrange
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Zero Line Test",
            _testUser
        );

        // Add a valid line and a zero line
        entry.AddItem(JournalItem.Create(
            Guid.NewGuid(),
            1000m,
            0,
            _testUser
        ));

        // Act
        bool result = entry.HasValidLines();

        // Assert - should return false because not all lines have positive amounts
        result.Should().BeFalse();
    }

    [Fact]
    public void HasValidLines_WithAllPositiveAmounts_ShouldReturnTrue()
    {
        // Arrange
        var entry = CreateBalancedEntry(1000m, 1000m);

        // Act
        bool result = entry.HasValidLines();

        // Assert
        result.Should().BeTrue();
    }

    #endregion

    #region Status Lock - POSTED Cannot Be Modified (Scenario 3)

    [Fact]
    public void AddItem_WhenPosted_ShouldThrowInvalidOperationException()
    {
        // Arrange
        var entry = CreateBalancedEntry(1000m, 1000m);
        entry.Post(_testUser, periodId => true);

        // Act
        var action = () => entry.AddItem(JournalItem.Create(
            Guid.NewGuid(),
            500m,
            0,
            _testUser
        ));

        // Assert
        action.Should().Throw<InvalidOperationException>()
            .WithMessage("*non-draft*");
    }

    [Fact]
    public void UpdateDescription_WhenPosted_ShouldThrowInvalidOperationException()
    {
        // Arrange
        var entry = CreateBalancedEntry(1000m, 1000m);
        entry.Post(_testUser, periodId => true);

        // Act
        var action = () => entry.UpdateDescription("New Description", _testUser);

        // Assert
        action.Should().Throw<InvalidOperationException>()
            .WithMessage("*draft*");
    }

    [Fact]
    public void Post_WhenAlreadyPosted_ShouldThrowInvalidOperationException()
    {
        // Arrange
        var entry = CreateBalancedEntry(1000m, 1000m);
        entry.Post(_testUser, periodId => true);

        // Act
        var action = () => entry.Post(_testUser, periodId => true);

        // Assert
        action.Should().Throw<InvalidOperationException>()
            .WithMessage("*draft*");
    }

    [Fact]
    public void Void_WhenPosted_ShouldSucceed()
    {
        // Arrange
        var entry = CreateBalancedEntry(1000m, 1000m);
        entry.Post(_testUser, periodId => true);

        // Act
        entry.Void(_testUser);

        // Assert
        entry.Status.Should().Be(VoucherStatus.Void);
        entry.VoidedAt.Should().NotBeNull();
        entry.VoidedBy.Should().Be(_testUser);
    }

    #endregion

    #region Fiscal Period Tests

    [Fact]
    public void Post_WhenPeriodClosed_ShouldThrowInvalidOperationException()
    {
        // Arrange
        var entry = CreateBalancedEntry(1000m, 1000m);

        // Act
        var action = () => entry.Post(_testUser, periodId => false); // Period is closed

        // Assert
        action.Should().Throw<InvalidOperationException>()
            .WithMessage("*not open*");
    }

    #endregion

    #region Void Tests

    [Fact]
    public void Void_WhenDraft_ShouldSucceed()
    {
        // Arrange
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Draft to Void",
            _testUser
        );

        // Act
        entry.Void(_testUser);

        // Assert
        entry.Status.Should().Be(VoucherStatus.Void);
        entry.VoidedAt.Should().NotBeNull();
    }

    [Fact]
    public void Void_WhenAlreadyVoided_ShouldThrowInvalidOperationException()
    {
        // Arrange
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Already Voided",
            _testUser
        );
        entry.Void(_testUser);

        // Act
        var action = () => entry.Void(_testUser);

        // Assert
        action.Should().Throw<InvalidOperationException>()
            .WithMessage("*already voided*");
    }

    #endregion

    #region Helper Methods

    private JournalEntry CreateBalancedEntry(decimal debit, decimal credit)
    {
        var entry = JournalEntry.Create(
            DateOnly.FromDateTime(DateTime.Today),
            _fiscalPeriodId,
            "VND",
            "Balanced Test Entry",
            _testUser
        );

        entry.AddItem(JournalItem.Create(
            Guid.NewGuid(),
            debit,
            0,
            _testUser
        ));

        entry.AddItem(JournalItem.Create(
            Guid.NewGuid(),
            0,
            credit,
            _testUser
        ));

        return entry;
    }

    #endregion
}
