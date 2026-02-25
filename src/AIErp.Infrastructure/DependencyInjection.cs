using AIErp.Infrastructure.Persistence;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;

namespace AIErp.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(
        this IServiceCollection services,
        IConfiguration configuration)
    {
        // Register PostgreSQL DbContext
        var connectionString = configuration.GetConnectionString("DefaultConnection")
            ?? throw new InvalidOperationException("Connection string 'DefaultConnection' not found.");

        services.AddDbContext<AppDbContext>(options =>
            options.UseNpgsql(
                connectionString,
                npgsqlOptions =>
                {
                    npgsqlOptions.CommandTimeout(30);
                    npgsqlOptions.EnableRetryOnFailure(3);
                }));

        return services;
    }

    public static IServiceCollection AddInfrastructure<TContext>(
        this IServiceCollection services,
        string connectionString)
        where TContext : DbContext
    {
        services.AddDbContext<TContext>(options =>
            options.UseNpgsql(
                connectionString,
                npgsqlOptions =>
                {
                    npgsqlOptions.CommandTimeout(30);
                    npgsqlOptions.EnableRetryOnFailure(3);
                }));

        return services;
    }
}
