namespace AIErp.Domain.Tests.Entities;

using AIErp.Domain.Entities;
using FluentAssertions;

public class FiscalPeriodTests
{
    private readonly string _testUser = "testuser";

    [Fact]
    public void Should_CreateFiscalPeriod_Successfully()
    {
        var startDate = new DateOnly(2025, 1, 1);
        var endDate = new DateOnly(2025, 1, 31);

        var period = FiscalPeriod.Create(
            year: 2025,
            period: 1,
            startDate: startDate,
            endDate: endDate,
            createdBy: _testUser
        );

        period.Year.Should().Be(2025);
        period.Period.Should().Be(1);
        period.IsOpen.Should().BeFalse();
        period.StartDate.Should().Be(startDate);
        period.EndDate.Should().Be(endDate);
    }

    [Fact]
    public void Should_OpenPeriod_Successfully()
    {
        var period = FiscalPeriod.Create(
            year: 2025,
            period: 1,
            startDate: new DateOnly(2025, 1, 1),
            endDate: new DateOnly(2025, 1, 31),
            createdBy: _testUser
        );

        period.Open(_testUser);

        period.IsOpen.Should().BeTrue();
    }

    [Fact]
    public void Should_ClosePeriod_Successfully()
    {
        var period = FiscalPeriod.Create(
            year: 2025,
            period: 1,
            startDate: new DateOnly(2025, 1, 1),
            endDate: new DateOnly(2025, 1, 31),
            createdBy: _testUser
        );

        period.Open(_testUser);
        period.Close(_testUser);

        period.IsOpen.Should().BeFalse();
    }

    [Fact]
    public void Should_ThrowException_WhenOpeningAlreadyOpenPeriod()
    {
        var period = FiscalPeriod.Create(
            year: 2025,
            period: 1,
            startDate: new DateOnly(2025, 1, 1),
            endDate: new DateOnly(2025, 1, 31),
            createdBy: _testUser
        );

        period.Open(_testUser);

        var act = () => period.Open(_testUser);
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*already open*");
    }

    [Fact]
    public void Should_ThrowException_WhenClosingAlreadyClosedPeriod()
    {
        var period = FiscalPeriod.Create(
            year: 2025,
            period: 1,
            startDate: new DateOnly(2025, 1, 1),
            endDate: new DateOnly(2025, 1, 31),
            createdBy: _testUser
        );

        var act = () => period.Close(_testUser);
        act.Should().Throw<InvalidOperationException>()
            .WithMessage("*already closed*");
    }

    [Fact]
    public void Should_RejectPosting_WhenPeriodIsClosed()
    {
        var period = FiscalPeriod.Create(
            year: 2025,
            period: 1,
            startDate: new DateOnly(2025, 1, 1),
            endDate: new DateOnly(2025, 1, 31),
            createdBy: _testUser
        );

        // Period is closed by default
        period.IsOpen.Should().BeFalse();
    }

    [Fact]
    public void Should_AllowPosting_WhenPeriodIsOpen()
    {
        var period = FiscalPeriod.Create(
            year: 2025,
            period: 1,
            startDate: new DateOnly(2025, 1, 1),
            endDate: new DateOnly(2025, 1, 31),
            createdBy: _testUser
        );

        period.Open(_testUser);

        period.IsOpen.Should().BeTrue();
    }

    [Fact]
    public void Should_ThrowException_WhenStartDateAfterEndDate()
    {
        var act = () => FiscalPeriod.Create(
            year: 2025,
            period: 1,
            startDate: new DateOnly(2025, 1, 31),
            endDate: new DateOnly(2025, 1, 1),
            createdBy: _testUser
        );

        act.Should().Throw<ArgumentException>()
            .WithMessage("*StartDate must be before EndDate*");
    }

    [Fact]
    public void Should_ThrowException_WhenInvalidYear()
    {
        var act = () => FiscalPeriod.Create(
            year: 1800,
            period: 1,
            startDate: new DateOnly(1800, 1, 1),
            endDate: new DateOnly(1800, 1, 31),
            createdBy: _testUser
        );

        act.Should().Throw<ArgumentException>()
            .WithMessage("*Invalid year*");
    }

    [Fact]
    public void Should_ContainDate_ReturnTrue_WhenDateInRange()
    {
        var period = FiscalPeriod.Create(
            year: 2025,
            period: 1,
            startDate: new DateOnly(2025, 1, 1),
            endDate: new DateOnly(2025, 1, 31),
            createdBy: _testUser
        );

        period.ContainsDate(new DateOnly(2025, 1, 15)).Should().BeTrue();
    }

    [Fact]
    public void Should_ContainDate_ReturnFalse_WhenDateOutOfRange()
    {
        var period = FiscalPeriod.Create(
            year: 2025,
            period: 1,
            startDate: new DateOnly(2025, 1, 1),
            endDate: new DateOnly(2025, 1, 31),
            createdBy: _testUser
        );

        period.ContainsDate(new DateOnly(2025, 2, 1)).Should().BeFalse();
    }
}
