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
}
