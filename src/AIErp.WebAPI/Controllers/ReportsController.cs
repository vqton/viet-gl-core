namespace AIErp.WebAPI.Controllers;

using AIErp.Application.DTOs;
using AIErp.Application.Interfaces;
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/v1/[controller]")]
public class ReportsController(IReportingService reportingService) : ControllerBase
{
    private readonly IReportingService _reportingService = reportingService;

    [HttpGet("trial-balance")]
    public async Task<IActionResult> GetTrialBalance(
        [FromQuery] DateTime startDate,
        [FromQuery] DateTime endDate,
        CancellationToken cancellationToken)
    {
        if (startDate > endDate)
            return BadRequest(ApiResponse.Error("INVALID_DATE_RANGE", "Ngày bắt đầu phải trước ngày kết thúc"));

        var report = await _reportingService.GetTrialBalanceAsync(startDate, endDate, cancellationToken);
        return Ok(ApiResponse.Success(report));
    }

    [HttpGet("general-ledger")]
    public async Task<IActionResult> GetGeneralLedger(
        [FromQuery] string accountCode,
        [FromQuery] DateTime startDate,
        [FromQuery] DateTime endDate,
        CancellationToken cancellationToken)
    {
        if (string.IsNullOrWhiteSpace(accountCode))
            return BadRequest(ApiResponse.Error("INVALID_ACCOUNT_CODE", "Mã tài khoản không được để trống"));

        if (startDate > endDate)
            return BadRequest(ApiResponse.Error("INVALID_DATE_RANGE", "Ngày bắt đầu phải trước ngày kết thúc"));

        try
        {
            var report = await _reportingService.GetGeneralLedgerAsync(accountCode, startDate, endDate, cancellationToken);
            return Ok(ApiResponse.Success(report));
        }
        catch (InvalidOperationException ex)
        {
            return NotFound(ApiResponse.Error("ACCOUNT_NOT_FOUND", ex.Message));
        }
    }
}
