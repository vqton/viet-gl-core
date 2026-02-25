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
            .WithMessage("*Không thể sửa tài khoản hệ thống*");
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
            .WithMessage("*Không thể vô hiệu hóa tài khoản hệ thống*");
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

        var act = () => systemAccount.Activate(_testUser);
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*Không thể kích hoạt tài khoản hệ thống*");
    }

    [Fact]
    public void Should_ValidateCode_WithCorrectLength()
    {
        var act = () => Account.ValidateCode("12345678901"); // 11 digits
        act.Should().Throw<ArgumentException>()
            .WithMessage("*phải từ 3 đến 10*");
    }

    [Fact]
    public void Should_ValidateCode_MustBeDigitsOnly()
    {
        var act = () => Account.ValidateCode("12A");
        act.Should().Throw<ArgumentException>()
            .WithMessage("*chỉ được phép chứa chữ số*");
    }

    [Fact]
    public void Should_CreateSuccessfully_WithValidCode()
    {
        var act = () => Account.ValidateCode("1111");
        act.Should().NotThrow();
    }

    [Fact]
    public void Should_ThrowException_WhenDeletingSystemAccount()
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

        var act = () => systemAccount.Delete();
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*Không thể xóa tài khoản hệ thống*");
    }

    [Fact]
    public void Should_AllowDelete_WhenAccountIsNotSystem()
    {
        var account = Account.Create(
            "1112",
            "Tiền Việt Nam",
            AccountType.Asset,
            NormalBalance.Debit,
            isDetail: true,
            parentId: Guid.NewGuid(),
            createdBy: _testUser,
            isSystem: false
        );

        var act = () => account.Delete();
        act.Should().NotThrow();
    }

    [Fact]
    public void Should_ReturnFalseForCanPost_WhenAccountIsParent()
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
    public void Should_ReturnTrueForCanPost_WhenAccountIsLeafDetail()
    {
        var parentId = Guid.NewGuid();
        var childAccount = Account.Create(
            "1111",
            "Tiền Việt Nam",
            AccountType.Asset,
            NormalBalance.Debit,
            isDetail: true,
            parentId: parentId,
            createdBy: _testUser
        );

        childAccount.CanPost().Should().BeTrue();
    }
}
