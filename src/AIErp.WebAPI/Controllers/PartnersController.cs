namespace AIErp.WebAPI.Controllers;

using AIErp.Application.DTOs;
using AIErp.Application.Exceptions;
using AIErp.Application.Interfaces;
using Microsoft.AspNetCore.Mvc;

[ApiController]
[Route("api/v1/[controller]")]
public class PartnersController(IPartnerService service) : ControllerBase
{
    private readonly IPartnerService _service = service;

    [HttpGet]
    public async Task<IActionResult> GetAll(CancellationToken cancellationToken)
    {
        var partners = await _service.GetAllAsync(cancellationToken);
        return Ok(ApiResponse.Success(partners));
    }

    [HttpGet("{id:guid}")]
    public async Task<IActionResult> GetById(Guid id, CancellationToken cancellationToken)
    {
        var partner = await _service.GetByIdAsync(id, cancellationToken);
        if (partner == null)
            return NotFound(ApiResponse.Error("NOT_FOUND", "Partner not found"));

        return Ok(ApiResponse.Success(partner));
    }

    [HttpPost]
    public async Task<IActionResult> Create([FromBody] CreatePartnerDto dto, CancellationToken cancellationToken)
    {
        try
        {
            var partner = await _service.CreateAsync(dto, "API_USER", cancellationToken);
            return CreatedAtAction(nameof(GetById), new { id = partner.Id }, ApiResponse.Success(partner));
        }
        catch (BusinessException ex)
        {
            return BadRequest(ApiResponse.Error(ex.ErrorCode, ex.Message));
        }
    }

    [HttpPut("{id:guid}")]
    public async Task<IActionResult> Update(Guid id, [FromBody] UpdatePartnerDto dto, CancellationToken cancellationToken)
    {
        try
        {
            var partner = await _service.UpdateAsync(id, dto, "API_USER", cancellationToken);
            return Ok(ApiResponse.Success(partner));
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
            await _service.DeleteAsync(id, "API_USER", cancellationToken);
            return Ok(ApiResponse.Success(new { id, message = "Partner deactivated" }));
        }
        catch (BusinessException ex)
        {
            return BadRequest(ApiResponse.Error(ex.ErrorCode, ex.Message));
        }
    }
}
