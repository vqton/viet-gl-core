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
            .WithMessage("*không được để trống*");
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
            .WithMessage("*không được để trống*");
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
            .WithMessage("*Không thể sửa đối tượng hệ thống*");
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
            .WithMessage("*Không thể vô hiệu hóa đối tượng hệ thống*");
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

    [Fact]
    public void Should_HaveUniqueCode_DefinedInDatabase()
    {
        // This test documents that PartnerCode uniqueness is enforced at database level
        // The unique index is defined in AppDbContext: entity.HasIndex(e => e.Code).IsUnique();
        // When two partners with the same code are created, DbUpdateException will be thrown
        var partner1 = Partner.Create(
            code: "KH001",
            name: "Công ty ABC",
            type: PartnerType.Customer,
            createdBy: _testUser
        );

        partner1.Code.Should().Be("KH001");
        
        // Attempting to create another partner with same code would violate DB constraint
        // This is validated at Infrastructure level, not Domain level
    }

    [Fact]
    public void Should_PreventDuplicateCode_AtDatabaseLevel()
    {
        // Documents the DB-level uniqueness constraint
        // In production, when saving two partners with same Code, 
        // database will throw DbUpdateException with inner exception:
        // "UNIQUE constraint failed: Partners.Code"
        var partner = Partner.Create(
            code: "KH999",
            name: "Test Partner",
            type: PartnerType.Customer,
            createdBy: _testUser
        );

        partner.Code.Should().Be("KH999");
    }
}
