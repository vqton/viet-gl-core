namespace AIErp.Domain.Tests.Entities;

using AIErp.Domain.Entities;
using AIErp.Domain.Enums;
using FluentAssertions;

public class AccountTests
{
    private readonly string _testUser = "testuser";

    [Fact]
    public void Should_ReturnTrueForCanPost_When_AccountIsDetailAndActive()
    {
        var account = Account.Create(
            "1111",
            "Tiền Việt Nam",
            AccountType.Asset,
            NormalBalance.Debit,
            isDetail: true,
            parentId: Guid.NewGuid(),
            createdBy: _testUser
        );

        account.CanPost().Should().BeTrue();
    }

    [Fact]
    public void Should_ReturnFalseForCanPost_When_AccountIsNotDetail()
    {
        var parentAccount = Account.Create(
            "111",
            "Tiền",
            AccountType.Asset,
            NormalBalance.Debit,
            isDetail: false,
            parentId: null,
            createdBy: _testUser
        );

        parentAccount.CanPost().Should().BeFalse();
    }

    [Fact]
    public void Should_ReturnFalseForCanPost_When_AccountIsInactive()
    {
        var account = Account.Create(
            "1111",
            "Tiền Việt Nam",
            AccountType.Asset,
            NormalBalance.Debit,
            isDetail: true,
            parentId: Guid.NewGuid(),
            createdBy: _testUser
        );

        account.Deactivate(_testUser);
        account.CanPost().Should().BeFalse();
    }

    [Fact]
    public void Should_ThrowException_WhenUpdatingSystemAccount()
    {
        var systemAccount = Account.Create(
            "1111",
            "Tiền Việt Nam",
            AccountType.Asset,
            NormalBalance.Debit,
            isDetail: true,
            parentId: Guid.NewGuid(),
            createdBy: _testUser,
            isSystem: true
        );

        var act = () => systemAccount.Update("New Name", null, _testUser);
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*Cannot modify system account*");
    }

    [Fact]
    public void Should_ThrowException_WhenDeactivatingSystemAccount()
    {
        var systemAccount = Account.Create(
            "1111",
            "Tiền Việt Nam",
            AccountType.Asset,
            NormalBalance.Debit,
            isDetail: true,
            parentId: Guid.NewGuid(),
            createdBy: _testUser,
            isSystem: true
        );

        var act = () => systemAccount.Deactivate(_testUser);
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*Cannot deactivate system account*");
    }

    [Fact]
    public void Should_ThrowException_WhenActivatingSystemAccount()
    {
        var systemAccount = Account.Create(
            "1111",
            "Tiền Việt Nam",
            AccountType.Asset,
            NormalBalance.Debit,
            isDetail: true,
            parentId: Guid.NewGuid(),
            createdBy: _testUser,
            isSystem: true
        );

        systemAccount.Deactivate(_testUser);

        var act = () => systemAccount.Activate(_testUser);
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*Cannot activate system account*");
    }

    [Fact]
    public void Should_ValidateCode_WithCorrectLength()
    {
        var act = () => Account.ValidateCode("12345678901"); // 11 digits
        act.Should().Throw<ArgumentException>()
            .WithMessage("*must be between 3 and 10*");
    }

    [Fact]
    public void Should_ValidateCode_MustBeDigitsOnly()
    {
        var act = () => Account.ValidateCode("12A");
        act.Should().Throw<ArgumentException>()
            .WithMessage("*must contain only digits*");
    }

    [Fact]
    public void Should_CreateSuccessfully_WithValidCode()
    {
        var act = () => Account.ValidateCode("1111");
        act.Should().NotThrow();
    }
}
