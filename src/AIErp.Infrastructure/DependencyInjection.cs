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

        var provider = configuration["DatabaseProvider"] ?? "Sqlite";

        services.AddDbContext<AppDbContext>(options =>
        {
            switch (provider.ToLowerInvariant())
            {
                case "mariadb":
                case "mysql":
                    options.UseMySql(
                        connectionString,
                        ServerVersion.AutoDetect(connectionString),
                        mysqlOptions =>
                        {
                            mysqlOptions.EnableRetryOnFailure(3);
                            mysqlOptions.CommandTimeout(30);
                        });
                    break;

                case "sqlite":
                default:
                    options.UseSqlite(connectionString);
                    break;
            }
        });

        return services;
    }

    public static IServiceCollection AddInfrastructure<TContext>(
        this IServiceCollection services,
        string connectionString,
        string provider = "Sqlite")
        where TContext : DbContext
    {
        services.AddDbContext<TContext>(options =>
        {
            switch (provider.ToLowerInvariant())
            {
                case "mariadb":
                case "mysql":
                    options.UseMySql(
                        connectionString,
                        ServerVersion.AutoDetect(connectionString),
                        mysqlOptions =>
                        {
                            mysqlOptions.EnableRetryOnFailure(3);
                            mysqlOptions.CommandTimeout(30);
                        });
                    break;

                case "sqlite":
                default:
                    options.UseSqlite(connectionString);
                    break;
            }
        });

        return services;
    }
}
