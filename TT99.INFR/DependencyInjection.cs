using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using TT99.APPL.Intrfs; // IUnitOfWork, IJournalEntryRepository, IReportQueryService
using TT99.APPL.Services;
using TT99.DMN.Interfaces; // IJournalingService
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
            
            // Nếu sử dụng PostgreSQL
            services.AddDbContext<TT99DbContext>(options =>
                options.UseNpgsql(connectionString,
                    b => b.MigrationsAssembly(typeof(TT99DbContext).Assembly.FullName)));
            
            // Hoặc nếu sử dụng SQL Server:
            /*
            services.AddDbContext<TT99DbContext>(options =>
                options.UseSqlServer(connectionString,
                    b => b.MigrationsAssembly(typeof(TT99DbContext).Assembly.FullName)));
            */

            // === 2. Cấu hình Repositories và Unit of Work (Scope: Per Request) ===
            services.AddScoped<IUnitOfWork, UnitOfWork>();
            services.AddScoped<IJournalEntryRepository, JournalEntryRepository>();
            // Có thể thêm IAccountRepository nếu cần

            // === 3. Cấu hình Services (Scope: Per Request) ===
            services.AddScoped<IJournalingService, JournalingService>(); // Domain Service
            services.AddScoped<IReportQueryService, ReportQueryService>(); // Application Service
            
            return services;
        }
    }
}