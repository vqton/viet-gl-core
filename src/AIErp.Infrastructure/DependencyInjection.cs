namespace AIErp.Infrastructure;

using AIErp.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        var connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("Connection string 'DefaultConnection' not found.");

        services.AddDbContext<AppDbContext>(options =>
            options.UseSqlite(connectionString));

        return services;
    }

    public static IServiceCollection AddInfrastructure<TContext>(
        this IServiceCollection services,
        string connectionString)
        where TContext : DbContext
    {
        services.AddDbContext<TContext>(options =>
            options.UseSqlite(connectionString));

        return services;
    }
}
