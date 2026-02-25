using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Mvc.Filters;
using Microsoft.EntityFrameworkCore;

namespace AIErp.WebAPI.Filters;

public class GlobalExceptionFilter : IExceptionFilter
{
    private readonly ILogger<GlobalExceptionFilter> _logger;

    public GlobalExceptionFilter(ILogger<GlobalExceptionFilter> logger)
    {
        _logger = logger;
    }

    public void OnException(ExceptionContext context)
    {
        if (context.Exception is DbUpdateConcurrencyException)
        {
            _logger.LogWarning(context.Exception, "Concurrency conflict detected");
            
            context.Result = new ObjectResult(new
            {
                success = false,
                error = new
                {
                    code = "CONCURRENCY_CONFLICT",
                    message = "Dữ liệu đã bị thay đổi bởi phiên làm việc khác. Vui lòng tải lại dữ liệu mới nhất."
                },
                timestamp = DateTime.UtcNow
            })
            {
                StatusCode = 409
            };
            
            context.ExceptionHandled = true;
            return;
        }

        if (context.Exception is InvalidOperationException invalidOpEx)
        {
            _logger.LogWarning(invalidOpEx, "Invalid operation");
            
            context.Result = new ObjectResult(new
            {
                success = false,
                error = new
                {
                    code = "BUSINESS_RULE_VIOLATION",
                    message = invalidOpEx.Message
                },
                timestamp = DateTime.UtcNow
            })
            {
                StatusCode = 400
            };
            
            context.ExceptionHandled = true;
            return;
        }

        if (context.Exception is ArgumentException argEx)
        {
            _logger.LogWarning(argEx, "Argument validation error");
            
            context.Result = new ObjectResult(new
            {
                success = false,
                error = new
                {
                    code = "VALIDATION_ERROR",
                    message = argEx.Message
                },
                timestamp = DateTime.UtcNow
            })
            {
                StatusCode = 400
            };
            
            context.ExceptionHandled = true;
            return;
        }

        _logger.LogError(context.Exception, "Unhandled exception");
        
        context.Result = new ObjectResult(new
        {
            success = false,
            error = new
            {
                code = "INTERNAL_ERROR",
                message = "Đã xảy ra lỗi hệ thống. Vui lòng thử lại sau."
            },
            timestamp = DateTime.UtcNow
        })
        {
            StatusCode = 500
        };
        
        context.ExceptionHandled = true;
    }
}
