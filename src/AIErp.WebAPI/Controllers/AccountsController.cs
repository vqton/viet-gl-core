namespace AIErp.WebAPI.Controllers;

using AIErp.Application.DTOs;
using AIErp.Application.Exceptions;
using AIErp.Application.Interfaces;
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/v1/[controller]")]
public class AccountsController(IAccountService service) : ControllerBase
{
    private readonly IAccountService _service = service;

    [HttpGet]
    public async Task<IActionResult> GetAll(CancellationToken cancellationToken)
    {
        var accounts = await _service.GetAllAsync(cancellationToken);
        return Ok(ApiResponse.Success(accounts));
    }

    [HttpGet("tree")]
    public async Task<IActionResult> GetTree(CancellationToken cancellationToken)
    {
        var tree = await _service.GetFullTreeAsync(cancellationToken);
        return Ok(ApiResponse.Success(tree));
    }

    [HttpGet("search")]
    public async Task<IActionResult> Search(
        [FromQuery] string? searchTerm,
        [FromQuery] bool? isDetail,
        CancellationToken cancellationToken = default)
    {
        var accounts = await _service.SearchAsync(searchTerm, isDetail, cancellationToken);
        return Ok(ApiResponse.Success(accounts));
    }

    [HttpGet("code/{code}")]
    public async Task<IActionResult> GetByCode(string code, CancellationToken cancellationToken)
    {
        var account = await _service.GetByCodeAsync(code, cancellationToken);
        if (account == null)
            return NotFound(ApiResponse.Error("NOT_FOUND", "Account not found"));

        return Ok(ApiResponse.Success(account));
    }

    [HttpGet("{id:guid}")]
    public async Task<IActionResult> GetById(Guid id, CancellationToken cancellationToken)
    {
        var account = await _service.GetByIdAsync(id, cancellationToken);
        if (account == null)
            return NotFound(ApiResponse.Error("NOT_FOUND", "Account not found"));

        return Ok(ApiResponse.Success(account));
    }

    [HttpPost]
    public async Task<IActionResult> Create([FromBody] CreateAccountDto dto, CancellationToken cancellationToken)
    {
        try
        {
            var account = await _service.CreateAsync(dto, "API_USER", cancellationToken);
            return CreatedAtAction(nameof(GetById), new { id = account.Id }, ApiResponse.Success(account));
        }
        catch (BusinessException ex)
        {
            return BadRequest(ApiResponse.Error(ex.ErrorCode, ex.Message));
        }
    }

    [HttpPut("{id:guid}")]
    public async Task<IActionResult> Update(Guid id, [FromBody] UpdateAccountDto dto, CancellationToken cancellationToken)
    {
        try
        {
            var account = await _service.UpdateAsync(id, dto, "API_USER", cancellationToken);
            return Ok(ApiResponse.Success(account));
        }
        catch (BusinessException ex)
        {
            return BadRequest(ApiResponse.Error(ex.ErrorCode, ex.Message));
        }
    }

    [HttpDelete("{id:guid}")]
    public async Task<IActionResult> Delete(Guid id, CancellationToken cancellationToken)
    {
        try
        {
            await _service.DeactivateAsync(id, "API_USER", cancellationToken);
            return Ok(ApiResponse.Success(new { id, message = "Account deactivated" }));
        }
        catch (BusinessException ex)
        {
            return BadRequest(ApiResponse.Error(ex.ErrorCode, ex.Message));
        }
    }

    [HttpPost("{id:guid}/activate")]
    public async Task<IActionResult> Activate(Guid id, CancellationToken cancellationToken)
    {
        try
        {
            await _service.ActivateAsync(id, "API_USER", cancellationToken);
            return Ok(ApiResponse.Success(new { id, message = "Account activated" }));
        }
        catch (BusinessException ex)
        {
            return BadRequest(ApiResponse.Error(ex.ErrorCode, ex.Message));
        }
    }
}
