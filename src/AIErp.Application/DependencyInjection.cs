using AIErp.Application.Interfaces;
using AIErp.Application.Services;
using Microsoft.Extensions.DependencyInjection;

namespace AIErp.Application;

public static class DependencyInjection
{
    public static IServiceCollection AddApplication(this IServiceCollection services)
    {
        services.AddScoped<IJournalEntryService, JournalEntryService>();
        services.AddScoped<IAccountService, AccountService>();
        services.AddScoped<IPartnerService, PartnerService>();

        return services;
    }
}
