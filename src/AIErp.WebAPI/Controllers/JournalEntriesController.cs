using AIErp.Application.DTOs;
using AIErp.Application.Exceptions;
using AIErp.Application.Interfaces;
using Microsoft.AspNetCore.Mvc;

namespace AIErp.WebAPI.Controllers;

[ApiController]
[Route("api/v1/[controller]")]
public class JournalEntriesController(IJournalEntryService journalEntryService) : ControllerBase
{
    private readonly IJournalEntryService _journalEntryService = journalEntryService;

    [HttpPost]
    public async Task<IActionResult> Create([FromBody] JournalEntryDto dto, CancellationToken cancellationToken)
    {
        try
        {
            // Get user from claims (simplified - in production, get from authentication)
            var createdBy = User.Identity?.Name ?? "system";
            
            var result = await _journalEntryService.CreateAsync(dto, createdBy, cancellationToken);
            
            return CreatedAtAction(nameof(GetById), new { id = result.Id }, new
            {
                success = true,
                data = result,
                timestamp = DateTime.UtcNow.ToString("o")
            });
        }
        catch (BusinessException ex)
        {
            return BadRequest(new
            {
                success = false,
                error = new
                {
                    code = ex.ErrorCode,
                    message = ex.Message
                },
                timestamp = DateTime.UtcNow.ToString("o")
            });
        }
        catch (Exception)
        {
            return StatusCode(500, new
            {
                success = false,
                error = new
                {
                    code = "INTERNAL_ERROR",
                    message = "An unexpected error occurred"
                },
                timestamp = DateTime.UtcNow.ToString("o")
            });
        }
    }

    [HttpGet("{id:guid}")]
    public async Task<IActionResult> GetById(Guid id, CancellationToken cancellationToken)
    {
        try
        {
            var result = await _journalEntryService.GetByIdAsync(id, cancellationToken);
            
            if (result == null)
                return NotFound(new
                {
                    success = false,
                    error = new
                    {
                        code = "NOT_FOUND",
                        message = "Journal entry not found"
                    },
                    timestamp = DateTime.UtcNow.ToString("o")
                });

            return Ok(new
            {
                success = true,
                data = result,
                timestamp = DateTime.UtcNow.ToString("o")
            });
        }
        catch (Exception)
        {
            return StatusCode(500, new
            {
                success = false,
                error = new
                {
                    code = "INTERNAL_ERROR",
                    message = "An unexpected error occurred"
                },
                timestamp = DateTime.UtcNow.ToString("o")
            });
        }
    }

    [HttpPost("{id:guid}/post")]
    public async Task<IActionResult> Post(Guid id, CancellationToken cancellationToken)
    {
        try
        {
            var postedBy = User.Identity?.Name ?? "system";
            var result = await _journalEntryService.PostAsync(id, postedBy, cancellationToken);

            return Ok(new
            {
                success = true,
                data = result,
                timestamp = DateTime.UtcNow.ToString("o")
            });
        }
        catch (BusinessException ex)
        {
            return BadRequest(new
            {
                success = false,
                error = new
                {
                    code = ex.ErrorCode,
                    message = ex.Message
                },
                timestamp = DateTime.UtcNow.ToString("o")
            });
        }
        catch (Exception)
        {
            return StatusCode(500, new
            {
                success = false,
                error = new
                {
                    code = "INTERNAL_ERROR",
                    message = "An unexpected error occurred"
                },
                timestamp = DateTime.UtcNow.ToString("o")
            });
        }
    }

    [HttpPost("{id:guid}/void")]
    public async Task<IActionResult> Void(Guid id, CancellationToken cancellationToken)
    {
        try
        {
            var voidedBy = User.Identity?.Name ?? "system";
            var result = await _journalEntryService.VoidAsync(id, voidedBy, cancellationToken);

            return Ok(new
            {
                success = true,
                data = result,
                timestamp = DateTime.UtcNow.ToString("o")
            });
        }
        catch (BusinessException ex)
        {
            return BadRequest(new
            {
                success = false,
                error = new
                {
                    code = ex.ErrorCode,
                    message = ex.Message
                },
                timestamp = DateTime.UtcNow.ToString("o")
            });
        }
        catch (Exception)
        {
            return StatusCode(500, new
            {
                success = false,
                error = new
                {
                    code = "INTERNAL_ERROR",
                    message = "An unexpected error occurred"
                },
                timestamp = DateTime.UtcNow.ToString("o")
            });
        }
    }
}
