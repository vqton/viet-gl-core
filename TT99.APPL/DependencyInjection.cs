using MediatR;
using Microsoft.Extensions.DependencyInjection;
using System.Reflection;

namespace TT99.APPL
{
    /// <summary>
    /// Các phương thức mở rộng để cấu hình Dependency Injection cho Lớp Application.
    /// </summary>
    public static class DependencyInjection
    {
        public static IServiceCollection AddApplication(this IServiceCollection services)
        {
            // Thêm MediatR và tự động tìm kiếm tất cả Handlers (IRequestHandler, IQueryHandler,...) 
            // trong assembly hiện tại (TT99.APPL).
            services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(Assembly.GetExecutingAssembly()));

            // Thêm các dịch vụ khác của Application (nếu có)
            
            return services;
        }
    }
}