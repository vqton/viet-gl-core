// File: D:\tt99acct\TT99.PRES\Program.cs
using FluentValidation;
using MediatR;
using Microsoft.EntityFrameworkCore; // Thêm using này cho AddDbContext
using TT99.APPL; // Namespace chứa AssemblyMarker
using TT99.APPL.Behaviors; // Namespace chứa ValidationBehavior
using TT99.DMN.Interfaces; // Thêm using cho interface IJournalingService
using TT99.APPL.Services;   // Thêm using cho interface IReportQueryService
using TT99.INFR.Data;
using TT99.INFR.Services;       // Thêm using cho TT99DbContext

var builder = WebApplication.CreateBuilder(args);

// --- Cấu hình Services ---

// 1. Thêm dịch vụ Controller/API
builder.Services.AddControllers();

// 2. Thêm Swagger/OpenAPI (Tùy chọn)
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Lấy Assembly chứa tất cả các Handlers, Validators, Commands/Queries (Dự án TT99.APPL)
var applicationAssembly = typeof(AssemblyMarker).Assembly;

// 3. Đăng ký MediatR (quét TT99.APPL)
builder.Services.AddMediatR(cfg => 
{
    cfg.RegisterServicesFromAssembly(applicationAssembly);
});

// 4. Đăng ký tất cả các Validators từ FluentValidation (quét TT99.APPL)
builder.Services.AddValidatorsFromAssembly(applicationAssembly);

// 5. Đăng ký ValidationBehavior vào Pipeline của MediatR
builder.Services.AddScoped(typeof(IPipelineBehavior<,>), typeof(ValidationBehavior<,>));

// 6. ĐĂNG KÝ TT99DbContext (ĐỌC TỪ appsettings.json) - SỬA: DÙNG UseNpgsql
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection"); // Đảm bảo tên này khớp với appsettings.json
if (string.IsNullOrEmpty(connectionString))
{
    throw new InvalidOperationException("Connection string 'DefaultConnection' not found in appsettings.json.");
}
builder.Services.AddDbContext<TT99DbContext>(options =>
    options.UseNpgsql(connectionString) // ĐÃ SỬA: Dùng UseNpgsql cho PostgreSQL
);

// 7. ĐĂNG KÝ CÁC DỊCH VỤ CỤ THỂ TỪ INFRASTRUCTURE LAYER (TT99.INFR)
builder.Services.AddScoped<IJournalingService, JournalingService>(); 
builder.Services.AddScoped<IReportQueryService, ReportQueryService>(); 


var app = builder.Build();

// --- Cấu hình Middleware Pipeline ---

// 1. Cấu hình HTTP Request Pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

// 2. Middleware xử lý Exception (Bạn nên thêm một Global Exception Handler ở đây, nhưng để đơn giản, chúng ta bỏ qua bước đó)
app.UseHttpsRedirection();

// 3. Authorization (Tùy chọn)
app.UseAuthorization();

// 4. Mapping Controller Endpoints
app.MapControllers();

app.Run();