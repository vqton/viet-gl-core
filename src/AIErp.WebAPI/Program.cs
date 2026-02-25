using AIErp.Application;
using AIErp.Application.DTOs;
using AIErp.Application.Exceptions;
using AIErp.Application.Interfaces;
using AIErp.Infrastructure;
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
builder.Services.AddControllers();
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
