// File: D:\tt99acct\TT99.PRES\Program.cs
// (Chỉ cập nhật phần đăng ký services)
using FluentValidation;
using MediatR;
using TT99.APPL; // Namespace chứa AssemblyMarker
using TT99.APPL.Behaviors; // Namespace chứa ValidationBehavior
using TT99.DMN.Interfaces; // Thêm using cho interface IJournalingService, IAccountingPeriodRepository
using TT99.APPL.Services;   // Thêm using cho interface IReportQueryService
using Microsoft.EntityFrameworkCore;
using TT99.INFR.Data;
using TT99.INFR.Services;
using TT99.INFR.Repos;
using TT99.INFR.Helpers;
using TT99.DMN.Interfaces;
using TT99.APPL.Services;

var builder = WebApplication.CreateBuilder(args);

// --- Cấu hình Services ---
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var applicationAssembly = typeof(AssemblyMarker).Assembly;

builder.Services.AddMediatR(cfg => cfg.RegisterServicesFromAssembly(applicationAssembly));
builder.Services.AddValidatorsFromAssembly(applicationAssembly);
builder.Services.AddScoped(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));

var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
if (string.IsNullOrEmpty(connectionString))
{
    throw new InvalidOperationException("Connection string 'DefaultConnection' not found in appsettings.json.");
}
builder.Services.AddDbContext<TT99DbContext>(options =>
    options.UseNpgsql(connectionString) // Đã SỬA: Dùng UseNpgsql cho PostgreSQL
);

// --- ĐĂNG KÝ CÁC DỊCH VỤ CỤ THỂ TỪ INFRASTRUCTURE LAYER (TT99.INFR) ---
builder.Services.AddScoped<IJournalingService, JournalingService>(); 
builder.Services.AddScoped<IReportQueryService, ReportQueryService>(); 
builder.Services.AddScoped<IAccountingPeriodRepository, AccountingPeriodRepository>(); // <-- Thêm dòng này


var app = builder.Build();

// --- Seeding Logic ---
using (var scope = app.Services.CreateScope())
{
    var context = scope.ServiceProvider.GetRequiredService<TT99DbContext>();
    context.Database.EnsureCreated(); // Hoặc Migrate

    if (!context.Accounts.Any())
    {
        Console.WriteLine("Seeding Accounts from CSV...");
        var accountsFromCsv = SeedDataHelper.ReadAccountsFromCsv("Data/SeedData/ChartOfAccounts_TT99.csv");
        context.Accounts.AddRange(accountsFromCsv);
        context.SaveChanges();
        Console.WriteLine($"Seeded {accountsFromCsv.Count} accounts.");
    }
    else
    {
        Console.WriteLine("Accounts already exist in the database. Skipping seed.");
    }

    // (Tùy chọn) Seed một số kỳ kế toán ban đầu nếu cần
    // if (!context.AccountingPeriods.Any())
    // {
    //     Console.WriteLine("Seeding Accounting Periods...");
    //     var period2025 = new AccountingPeriod("Năm tài chính 2025", new DateTime(2025, 1, 1), new DateTime(2025, 12, 31));
    //     context.AccountingPeriods.Add(period2025);
    //     context.SaveChanges();
    //     Console.WriteLine("Seeded initial Accounting Period.");
    // }
}
// --- End Seeding Logic ---

// --- Cấu hình Middleware Pipeline ---
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthorization();
app.MapControllers();

app.Run();