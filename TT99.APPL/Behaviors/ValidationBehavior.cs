using FluentValidation;
using MediatR;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;

namespace TT99.APPL.Behaviors
{
    /// <summary>
    /// Hành vi Pipeline (Pipeline Behavior) này sẽ chạy trước khi Request (Command/Query) được gửi đến Handler.
    /// Nó sẽ tìm tất cả các Validator (đã được đăng ký) cho Request hiện tại và thực hiện kiểm tra.
    /// </summary>
    /// <typeparam name="TRequest">Loại của Request (Command hoặc Query).</typeparam>
    /// <typeparam name="TResponse">Loại của Response.</typeparam>
    public class ValidationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
        where TRequest : IRequest<TResponse>
    {
        // Danh sách các Validators đã được Inject qua Dependency Injection
        private readonly IEnumerable<IValidator<TRequest>> _validators;

        public ValidationBehavior(IEnumerable<IValidator<TRequest>> validators)
        {
            _validators = validators;
        }

        public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken cancellationToken)
        {
            // Kiểm tra xem có bất kỳ Validator nào cho Request này không
            if (_validators.Any())
            {
                // Tạo một Validation Context từ Request
                var context = new ValidationContext<TRequest>(request);

                // Chạy tất cả các Validator một cách bất đồng bộ
                var validationResults = await Task.WhenAll(_validators.Select(v => v.ValidateAsync(context, cancellationToken)));

                // Lấy tất cả các lỗi từ các kết quả Validation
                var failures = validationResults
                    .Where(r => r.Errors.Any())
                    .SelectMany(r => r.Errors)
                    .ToList();

                // Nếu có bất kỳ lỗi nào, ném ra ngoại lệ ValidationException của FluentValidation
                if (failures.Any())
                {
                    // Ngoại lệ này sẽ được Middleware (hoặc Exception Handler) xử lý để trả về lỗi 400 Bad Request
                    throw new ValidationException(failures);
                }
            }

            // Nếu không có lỗi, chuyển Request sang bước tiếp theo trong Pipeline (đến Handler)
            return await next();
        }
    }
}