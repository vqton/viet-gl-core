// File: D:\tt99acct\TT99.INFR\DependencyInjection.cs
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
// using TT99.APPL.Intrfs; // <-- XÓA DÒNG NÀY
using TT99.APPL.Services;
using TT99.DMN.Interfaces; // <-- ĐÚNG: Để dùng IJournalingService, IUnitOfWork, IJournalEntryRepository (giả sử đặt ở đây)
using TT99.INFR.Data;
using TT99.INFR.Repos;
using TT99.INFR.Services;

namespace TT99.INFR
{
    /// <summary>
    /// Các phương thức mở rộng để cấu hình Dependency Injection cho Lớp Infrastructure.
    /// </summary>
    public static class DependencyInjection
    {
        public static IServiceCollection AddInfrastructure(this IServiceCollection services, IConfiguration configuration)
        {
            // === 1. Cấu hình Database Context (Giả định sử dụng PostgreSQL) ===
            var connectionString = configuration.GetConnectionString("DefaultConnection");
            
            services.AddDbContext<TT99DbContext>(options =>
                options.UseNpgsql(connectionString,
                    b => b.MigrationsAssembly(typeof(TT99DbContext).Assembly.FullName)));

            // === 2. Cấu hình Repositories và Unit of Work (Scope: Per Request) ===
            services.AddScoped<IUnitOfWork, UnitOfWork>(); // Giả sử IUnitOfWork trong TT99.DMN.Interfaces
            services.AddScoped<IJournalEntryRepository, JournalEntryRepository>(); // Giả sử IJournalEntryRepository trong TT99.DMN.Interfaces
            // Có thể thêm IAccountRepository nếu cần

            // === 3. Cấu hình Services (Scope: Per Request) ===
            services.AddScoped<IJournalingService, JournalingService>(); // Domain Service (IJournalingService trong TT99.DMN.Interfaces)
            services.AddScoped<IReportQueryService, ReportQueryService>(); // Application Service (IReportQueryService trong TT99.APPL.Services, ReportQueryService trong TT99.INFR.Services)
            
            return services;
        }
    }
}