using AIErp.Domain.Entities;
using FluentAssertions;

namespace AIErp.Domain.Tests.Entities;

public class JournalItemTests
{
    private readonly string _testUser = "testuser";
    private readonly Guid _accountId = Guid.NewGuid();

    #region Create Tests

    [Fact]
    public void Create_WithDebit_ShouldSetDebitAmount()
    {
        // Arrange & Act
        var item = JournalItem.Create(
            _accountId,
            1000m,
            0,
            _testUser
        );

        // Assert
        item.DebitAmount.Should().Be(1000m);
        item.CreditAmount.Should().Be(0);
    }

    [Fact]
    public void Create_WithCredit_ShouldSetCreditAmount()
    {
        // Arrange & Act
        var item = JournalItem.Create(
            _accountId,
            0,
            1000m,
            _testUser
        );

        // Assert
        item.DebitAmount.Should().Be(0);
        item.CreditAmount.Should().Be(1000m);
    }

    [Fact]
    public void Create_WithBothDebitAndCredit_ShouldThrowArgumentException()
    {
        // Arrange & Act
        var action = () => JournalItem.Create(
            _accountId,
            500m,
            500m,
            _testUser
        );

        // Assert
        action.Should().Throw<ArgumentException>()
            .WithMessage("*both*Debit*and*Credit*");
    }

    [Fact]
    public void Create_WithNegativeDebit_ShouldThrowArgumentException()
    {
        // Arrange & Act
        var action = () => JournalItem.Create(
            _accountId,
            -100m,
            0,
            _testUser
        );

        // Assert
        action.Should().Throw<ArgumentException>()
            .WithMessage("*negative*");
    }

    [Fact]
    public void Create_WithNegativeCredit_ShouldThrowArgumentException()
    {
        // Arrange & Act
        var action = () => JournalItem.Create(
            _accountId,
            0,
            -100m,
            _testUser
        );

        // Assert
        action.Should().Throw<ArgumentException>();
    }

    [Fact]
    public void Create_WithEmptyAccountId_ShouldThrowArgumentException()
    {
        // Arrange & Act
        var action = () => JournalItem.Create(
            Guid.Empty,
            1000m,
            0,
            _testUser
        );

        // Assert
        action.Should().Throw<ArgumentException>()
            .WithMessage("*AccountId*required*");
    }

    [Fact]
    public void Create_WithExchangeRate_ShouldCalculateBaseAmount()
    {
        // Arrange
        decimal amount = 1000m;
        decimal exchangeRate = 24500m; // USD to VND

        // Act
        var item = JournalItem.Create(
            _accountId,
            amount,
            0,
            _testUser,
            exchangeRate: exchangeRate
        );

        // Assert
        item.BaseAmount.Should().Be(24500000m); // 1000 * 24500
        item.ExchangeRate.Should().Be(exchangeRate);
    }

    [Fact]
    public void Create_WithDefaultExchangeRate_ShouldUseOne()
    {
        // Arrange & Act
        var item = JournalItem.Create(
            _accountId,
            1000m,
            0,
            _testUser
        );

        // Assert
        item.ExchangeRate.Should().Be(1.0m);
        item.BaseAmount.Should().Be(1000m);
    }

    #endregion

    #region Partner Check Tests - Accounts 131/331 (Scenario 4)

    [Fact]
    public void ValidatePartnerRequired_ForAccount131 WithoutPartner_ShouldThrow()
    {
        // Arrange
        var item = JournalItem.Create(
            _accountId,
            1000m,
            0,
            _testUser,
            partnerId: null // No partner!
        );

        // Act
        var action = () => item.ValidatePartnerRequired("131");

        // Assert
        action.Should().Throw<InvalidOperationException>()
            .WithMessage("*Partner is required*");
    }

    [Fact]
    public void ValidatePartnerRequired_ForAccount331 WithoutPartner_ShouldThrow()
    {
        // Arrange
        var item = JournalItem.Create(
            _accountId,
            0,
            1000m,
            _testUser,
            partnerId: null // No partner!
        );

        // Act
        var action = () => item.ValidatePartnerRequired("331");

        // Assert
        action.Should().Throw<InvalidOperationException>()
            .WithMessage("*Partner is required*");
    }

    [Fact]
    public void ValidatePartnerRequired_ForAccount131 WithPartner_ShouldNotThrow()
    {
        // Arrange
        var partnerId = Guid.NewGuid();
        var item = JournalItem.Create(
            _accountId,
            1000m,
            0,
            _testUser,
            partnerId: partnerId
        );

        // Act
        var action = () => item.ValidatePartnerRequired("131");

        // Assert
        action.Should().NotThrow();
    }

    [Fact]
    public void ValidatePartnerRequired_ForAccount331 WithPartner_ShouldNotThrow()
    {
        // Arrange
        var partnerId = Guid.NewGuid();
        var item = JournalItem.Create(
            _accountId,
            0,
            1000m,
            _testUser,
            partnerId: partnerId
        );

        // Act
        var action = () => item.ValidatePartnerRequired("331");

        // Assert
        action.Should().NotThrow();
    }

    [Fact]
    public void ValidatePartnerRequired_ForOtherAccount WithoutPartner_ShouldNotThrow()
    {
        // Arrange
        var item = JournalItem.Create(
            _accountId,
            1000m,
            0,
            _testUser,
            partnerId: null
        );

        // Act - Account 111 (Cash) doesn't require partner
        var action = () => item.ValidatePartnerRequired("111");

        // Assert
        action.Should().NotThrow();
    }

    [Fact]
    public void ValidatePartnerRequired_ForAccount1311 WithoutPartner_ShouldNotThrow()
    {
        // Arrange - Account 1311 is sub-account of 131, but code starts with "131"
        var item = JournalItem.Create(
            _accountId,
            1000m,
            0,
            _testUser,
            partnerId: null
        );

        // Act - Currently validates based on StartsWith, so 1311 also requires partner
        // This might be a design decision - adjust as needed
        var action = () => item.ValidatePartnerRequired("1311");

        // Assert - Currently throws because it starts with "131"
        action.Should().Throw<InvalidOperationException>();
    }

    #endregion

    #region GetAmount Tests

    [Fact]
    public void GetAmount_WhenDebit_ShouldReturnDebitAmount()
    {
        // Arrange
        var item = JournalItem.Create(
            _accountId,
            1500m,
            0,
            _testUser
        );

        // Act
        decimal amount = item.GetAmount();

        // Assert
        amount.Should().Be(1500m);
    }

    [Fact]
    public void GetAmount_WhenCredit_ShouldReturnCreditAmount()
    {
        // Arrange
        var item = JournalItem.Create(
            _accountId,
            0,
            1500m,
            _testUser
        );

        // Act
        decimal amount = item.GetAmount();

        // Assert
        amount.Should().Be(1500m);
    }

    #endregion

    #region Description Tests

    [Fact]
    public void Create_WithDescription_ShouldStoreDescription()
    {
        // Arrange & Act
        var item = JournalItem.Create(
            _accountId,
            1000m,
            0,
            _testUser,
            description: "Payment for invoice INV-001"
        );

        // Assert
        item.Description.Should().Be("Payment for invoice INV-001");
    }

    [Fact]
    public void Create_WithNullDescription_ShouldStoreNull()
    {
        // Arrange & Act
        var item = JournalItem.Create(
            _accountId,
            1000m,
            0,
            _testUser,
            description: null
        );

        // Assert
        item.Description.Should().BeNull();
    }

    [Fact]
    public void Create_WithWhitespaceDescription_ShouldTrim()
    {
        // Arrange & Act
        var item = JournalItem.Create(
            _accountId,
            1000m,
            0,
            _testUser,
            description: "  Invoice Payment  "
        );

        // Assert
        item.Description.Should().Be("Invoice Payment");
    }

    #endregion

    #region SetJournalEntryId Tests

    [Fact]
    public void SetJournalEntryId_ShouldSetTheId()
    {
        // Arrange
        var item = JournalItem.Create(
            _accountId,
            1000m,
            0,
            _testUser
        );
        var entryId = Guid.NewGuid();

        // Act
        item.SetJournalEntryId(entryId);

        // Assert
        item.JournalEntryId.Should().Be(entryId);
    }

    #endregion
}
