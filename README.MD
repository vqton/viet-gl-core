TT99ACCT: Hệ thống Kế toán Việt Nam theo Thông tư 99

🇻🇳 Giới thiệu Dự án

TT99ACCT là một dự án mã nguồn mở nhằm triển khai một hệ thống phần mềm kế toán cấp doanh nghiệp, tuân thủ nghiêm ngặt Thông tư 99/2021/TT-BTC (Chế độ kế toán Doanh nghiệp).

Dự án được xây dựng dựa trên kiến trúc hiện đại, tập trung vào hiệu suất, tính toàn vẹn dữ liệu (ACID), và khả năng bảo trì mã nguồn dài hạn.

🎯 Mục tiêu và Triết lý Kiến trúc

Hệ thống được thiết kế theo các nguyên tắc sau:

Clean Architecture: Tách biệt triệt để Logic Nghiệp vụ (Domain) khỏi các lớp Hạ tầng (Infrastructure) và Giao diện (Presentation).

CQRS (Command Query Responsibility Segregation): Tách biệt luồng Ghi dữ liệu (Commands - Ghi sổ) và luồng Đọc dữ liệu (Queries - Báo cáo) để tối ưu hóa hiệu suất.

Tuân thủ TT99: Lớp TT99.DMN chứa tất cả các quy tắc hạch toán Nợ/Có, tính toán số dư và quy tắc báo cáo theo chuẩn Việt Nam.

⚙️ Công nghệ và Yêu cầu

Công nghệ

Vai trò

Ghi chú

Ngôn ngữ

C#

Đảm bảo tính an toàn (Type Safety) và hiệu suất cao.

Framework

ASP.NET Core Web API

Xây dựng API tốc độ cao (Presentation Layer).

Database

PostgreSQL / SQL Server

Cơ sở dữ liệu quan hệ cho tính toàn vẹn tuyệt đối.

ORM

Entity Framework Core (EF Core)

Quản lý kết nối Database và Migrations.

Thư viện chính

MediatR, FluentValidation

Triển khai CQRS và Xác thực đầu vào.

Hosting

Docker/Linux

Tối ưu hóa cho môi trường containerization.

📁 Cấu trúc Project (Quy tắc 8 Ký tự)

Dự án được tổ chức thành 4 layers chính theo kiến trúc sạch, tuân thủ quy tắc đặt tên 8 ký tự:

Project

Ký hiệu

Vai trò

TT99.DMN

Domain

Lõi chứa Entities, Interfaces, và Logic Kế toán TT99.

TT99.APPL

Application

Chứa Commands, Queries, và Handlers (Triển khai CQRS).

TT99.INFR

Infrastructure

Chứa EF Core Context, Repositories, và Triển khai Database.

TT99.PRES

Presentation

ASP.NET Core Web API Endpoints.

🚀 Hướng dẫn Thiết lập Ban đầu

Đảm bảo bạn đã cài đặt .NET SDK mới nhất.

Clone Dự án:

git clone [https://github.com/vqton/tt99acct.git](https://github.com/vqton/tt99acct.git)
cd tt99acct



Restore Dependencies:

dotnet restore



Cấu hình Database:

Cập nhật chuỗi kết nối (Connection String) trong file appsettings.json của project TT99.PRES (hoặc TT99.INFR).

Áp dụng Migrations (sẽ được xây dựng sau):

dotnet ef database update --project TT99.INFR



Chạy Ứng dụng:

dotnet run --project TT99.PRES



API sẽ khởi động, thường là tại http://localhost:5000 hoặc http://localhost:5001.

🤝 Đóng góp

Chúng tôi hoan nghênh mọi đóng góp để cải thiện tính tuân thủ và mở rộng của hệ thống kế toán này. Vui lòng tạo một Issue hoặc gửi Pull Request cho các tính năng mới hoặc sửa lỗi.