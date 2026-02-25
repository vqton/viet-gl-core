namespace AIErp.WebAPI.Controllers;

using AIErp.Application.DTOs;
using AIErp.Application.Exceptions;
using AIErp.Application.Interfaces;
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/v1/[controller]")]
public class FiscalPeriodsController(IFiscalPeriodService service) : ControllerBase
{
    private readonly IFiscalPeriodService _service = service;

    [HttpGet]
    public async Task<IActionResult> GetAll(CancellationToken cancellationToken)
    {
        var periods = await _service.GetAllAsync(cancellationToken);
        return Ok(ApiResponse.Success(periods));
    }

    [HttpGet("current")]
    public async Task<IActionResult> GetCurrent(CancellationToken cancellationToken)
    {
        var period = await _service.GetCurrentPeriodAsync(cancellationToken);
        return Ok(ApiResponse.Success(period));
    }

    [HttpGet("{id:guid}")]
    public async Task<IActionResult> GetById(Guid id, CancellationToken cancellationToken)
    {
        var period = await _service.GetByIdAsync(id, cancellationToken);
        if (period == null)
            return NotFound(ApiResponse.Error("NOT_FOUND", "Fiscal period not found"));

        return Ok(ApiResponse.Success(period));
    }

    [HttpPost("{id:guid}/open")]
    public async Task<IActionResult> Open(Guid id, CancellationToken cancellationToken)
    {
        try
        {
            var period = await _service.OpenAsync(id, "API_USER", cancellationToken);
            return Ok(ApiResponse.Success(period));
        }
        catch (BusinessException ex)
        {
            return BadRequest(ApiResponse.Error(ex.ErrorCode, ex.Message));
        }
    }

    [HttpPost("{id:guid}/close")]
    public async Task<IActionResult> Close(Guid id, CancellationToken cancellationToken)
    {
        try
        {
            var period = await _service.CloseAsync(id, "API_USER", cancellationToken);
            return Ok(ApiResponse.Success(period));
        }
        catch (BusinessException ex)
        {
            return BadRequest(ApiResponse.Error(ex.ErrorCode, ex.Message));
        }
    }
}
