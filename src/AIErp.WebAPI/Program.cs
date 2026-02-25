using AIErp.Application;
using AIErp.Application.DTOs;
using AIErp.Application.Exceptions;
using AIErp.Application.Interfaces;
using AIErp.Infrastructure;
using AIErp.Infrastructure.Persistence;
using AIErp.Infrastructure.SeedData;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using Microsoft.OpenApi.Models;
using System.Text.Json.Serialization;
using Swashbuckle.AspNetCore.SwaggerUI;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        // Configure JSON serializer for Enums as String
        options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
        options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
        options.JsonSerializerOptions.PropertyNamingPolicy = null; // Keep PascalCase
    });

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new() { Title = "AIErp API", Version = "v1" });
});

// Register Application services
builder.Services.AddApplication();

// Register Infrastructure services
builder.Services.AddInfrastructure(builder.Configuration);

var app = builder.Build();

// Ensure database is created and migrated
using (var scope = app.Services.CreateScope())
{
    var dbContext = scope.ServiceProvider.GetRequiredService<AIErp.Infrastructure.Persistence.AppDbContext>();
    try
    {
        dbContext.Database.EnsureCreated();
        Console.WriteLine("Database ensured created successfully.");

        // Seed data if empty
        if (!await dbContext.Accounts.AnyAsync())
        {
            var accounts = IdentitySeed.GetChartOfAccounts();
            await dbContext.Accounts.AddRangeAsync(accounts);
            await dbContext.SaveChangesAsync();
            Console.WriteLine($"Seeded {accounts.Count} accounts.");
        }

        if (!await dbContext.FiscalPeriods.AnyAsync())
        {
            var periods = IdentitySeed.GetFiscalPeriods();
            await dbContext.FiscalPeriods.AddRangeAsync(periods);
            await dbContext.SaveChangesAsync();
            Console.WriteLine($"Seeded {periods.Count} fiscal periods.");
        }
    }
    catch (Exception ex)
    {
        Console.WriteLine($"Error creating database: {ex.Message}");
    }
}

// Global Exception Handler
app.UseExceptionHandler(errorApp =>
{
    errorApp.Run(async context =>
    {
        context.Response.StatusCode = 500;
        context.Response.ContentType = "application/json";
        
        await context.Response.WriteAsJsonAsync(new
        {
            success = false,
            error = new
            {
                code = "INTERNAL_ERROR",
                message = "An unexpected error occurred"
            },
            timestamp = DateTime.UtcNow.ToString("o")
        });
    });
});

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "AIErp API v1"));
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

app.Run();

// Standard API Response Envelope
public static class ApiResponse
{
    public static IActionResult Success(object? data, int statusCode = 200)
    {
        return new JsonResult(new
        {
            success = true,
            data,
            timestamp = DateTime.UtcNow.ToString("o")
        })
        {
            StatusCode = statusCode
        };
    }

    public static IActionResult Error(string errorCode, string message, object? details = null, int statusCode = 400)
    {
        return new JsonResult(new
        {
            success = false,
            error = new
            {
                code = errorCode,
                message,
                details
            },
            timestamp = DateTime.UtcNow.ToString("o")
        })
        {
            StatusCode = statusCode
        };
    }
}
