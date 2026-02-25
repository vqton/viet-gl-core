using AIErp.Application.Interfaces;
using AIErp.Application.Services;
using Microsoft.Extensions.DependencyInjection;

namespace AIErp.Application;

public static class DependencyInjection
{
    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        // Register Application Services
        services.AddScoped<IJournalEntryService, JournalEntryService>();

        return services;
    }
}
