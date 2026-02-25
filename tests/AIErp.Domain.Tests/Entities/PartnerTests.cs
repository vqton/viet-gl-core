namespace AIErp.Domain.Tests.Entities;

using AIErp.Domain.Entities;
using AIErp.Domain.Enums;
using FluentAssertions;

public class PartnerTests
{
    private readonly string _testUser = "testuser";

    [Fact]
    public void Should_CreatePartner_Successfully()
    {
        var partner = Partner.Create(
            code: "KH001",
            name: "Công ty ABC",
            type: PartnerType.Customer,
            createdBy: _testUser,
            taxCode: "0123456789"
        );

        partner.Code.Should().Be("KH001");
        partner.Name.Should().Be("Công ty ABC");
        partner.Type.Should().Be(PartnerType.Customer);
        partner.TaxCode.Should().Be("0123456789");
        partner.IsActive.Should().BeTrue();
        partner.IsSystem.Should().BeFalse();
    }

    [Fact]
    public void Should_ThrowException_WhenCodeIsEmpty()
    {
        var act = () => Partner.Create(
            code: "",
            name: "Công ty ABC",
            type: PartnerType.Customer,
            createdBy: _testUser
        );

        act.Should().Throw<ArgumentException>()
            .WithMessage("*Code is required*");
    }

    [Fact]
    public void Should_ThrowException_WhenNameIsEmpty()
    {
        var act = () => Partner.Create(
            code: "KH001",
            name: "",
            type: PartnerType.Customer,
            createdBy: _testUser
        );

        act.Should().Throw<ArgumentException>()
            .WithMessage("*Name is required*");
    }

    [Fact]
    public void Should_UpdatePartner_Successfully()
    {
        var partner = Partner.Create(
            code: "KH001",
            name: "Công ty ABC",
            type: PartnerType.Customer,
            createdBy: _testUser
        );

        partner.Update(
            name: "Công ty XYZ",
            type: PartnerType.Both,
            modifiedBy: _testUser,
            taxCode: "9876543210"
        );

        partner.Name.Should().Be("Công ty XYZ");
        partner.Type.Should().Be(PartnerType.Both);
        partner.TaxCode.Should().Be("9876543210");
    }

    [Fact]
    public void Should_ThrowException_WhenUpdatingSystemPartner()
    {
        var systemPartner = Partner.Create(
            code: "KH001",
            name: "Công ty ABC",
            type: PartnerType.Customer,
            createdBy: _testUser,
            isSystem: true
        );

        var act = () => systemPartner.Update(
            name: "New Name",
            type: PartnerType.Customer,
            modifiedBy: _testUser
        );

        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*Cannot modify system partner*");
    }

    [Fact]
    public void Should_ThrowException_WhenDeactivatingSystemPartner()
    {
        var systemPartner = Partner.Create(
            code: "KH001",
            name: "Công ty ABC",
            type: PartnerType.Customer,
            createdBy: _testUser,
            isSystem: true
        );

        var act = () => systemPartner.Deactivate(_testUser);

        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*Cannot deactivate system partner*");
    }

    [Fact]
    public void Should_DeactivatePartner_Successfully()
    {
        var partner = Partner.Create(
            code: "KH001",
            name: "Công ty ABC",
            type: PartnerType.Customer,
            createdBy: _testUser
        );

        partner.Deactivate(_testUser);

        partner.IsActive.Should().BeFalse();
    }

    [Fact]
    public void Should_ActivatePartner_Successfully()
    {
        var partner = Partner.Create(
            code: "KH001",
            name: "Công ty ABC",
            type: PartnerType.Customer,
            createdBy: _testUser
        );

        partner.Deactivate(_testUser);
        partner.Activate(_testUser);

        partner.IsActive.Should().BeTrue();
    }

    [Fact]
    public void Should_TrimWhitespace_FromCodeAndName()
    {
        var partner = Partner.Create(
            code: "  KH001  ",
            name: "  Công ty ABC  ",
            type: PartnerType.Customer,
            createdBy: _testUser
        );

        partner.Code.Should().Be("KH001");
        partner.Name.Should().Be("Công ty ABC");
    }
}
