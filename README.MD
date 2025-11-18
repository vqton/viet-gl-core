# **TT99ACCT: Hệ thống Kế toán Việt Nam theo Thông tư 99**

## **🇻🇳 Tổng quan Dự án**

**TT99ACCT** là một dự án phần mềm mã nguồn mở được thiết kế nhằm mục đích triển khai hệ thống kế toán doanh nghiệp. Mục tiêu chính của dự án là đảm bảo **tuân thủ nghiêm ngặt các quy định của Thông tư 99/2021/TT-BTC** (Chế độ kế toán Doanh nghiệp tại Việt Nam).

Hệ thống được xây dựng trên nền tảng công nghệ hiện đại, chú trọng vào **hiệu suất xử lý cao**, **tính toàn vẹn dữ liệu** (ACID), và **khả năng bảo trì** dài hạn thông qua kiến trúc phân lớp rõ ràng.

## **🎯 Mục tiêu và Nguyên tắc Kiến trúc**

Triết lý kiến trúc của hệ thống được xác định dựa trên ba nguyên tắc cốt lõi:

1. **Clean Architecture (Kiến trúc Sạch):** Đảm bảo sự phân tách rõ ràng giữa Lớp Nghiệp vụ (Domain) và các Lớp Hạ tầng (Infrastructure) hoặc Giao diện (Presentation). Phương pháp này giúp tăng cường khả năng kiểm thử và thay thế các thành phần.  
2. **CQRS (Tách biệt Trách nhiệm Ghi và Truy vấn):** Áp dụng mô hình Command Query Responsibility Segregation để tối ưu hóa hiệu suất. Luồng Ghi dữ liệu (Commands \- Ghi sổ) và luồng Truy vấn dữ liệu (Queries \- Báo cáo) được xử lý độc lập.  
3. **Tuân thủ TT99 Tuyệt đối:** Lớp TT99.DMN (Domain) chịu trách nhiệm chứa và thực thi toàn bộ logic nghiệp vụ kế toán, bao gồm quy tắc hạch toán Nợ/Có và tính toán báo cáo theo quy định hiện hành của Việt Nam.

## **⚙️ Công nghệ Triển khai**

Dự án sử dụng các công nghệ sau nhằm đảm bảo hiệu suất và độ tin cậy của hệ thống:

| Công nghệ | Vai trò | Ghi chú |
| :---- | :---- | :---- |
| **Ngôn ngữ** | C\# | Ngôn ngữ tĩnh (Static Typing) nhằm đảm bảo tính chính xác và hiệu suất xử lý cao. |
| **Framework** | ASP.NET Core Web API | Cung cấp các điểm cuối API hiệu suất cao cho Lớp Presentation. |
| **Database** | PostgreSQL / SQL Server | Cơ sở dữ liệu quan hệ được lựa chọn để duy trì tính toàn vẹn (ACID) của dữ liệu kế toán. |
| **ORM** | Entity Framework Core (EF Core) | Công cụ ORM để quản lý Persistence Layer và quá trình Database Migration. |
| **Thư viện chính** | MediatR, FluentValidation | Triển khai mô hình CQRS và đảm bảo xác thực dữ liệu đầu vào. |
| **Hosting** | Docker/Linux | Tối ưu hóa cho môi trường container hóa và triển khai Cloud linh hoạt. |

## **📁 Cấu trúc Project (Tuân thủ Quy tắc 8 Ký tự)**

Cấu trúc dự án tuân thủ Clean Architecture và sử dụng các ký hiệu rút gọn (tối đa 8 ký tự) để định danh các lớp:

| Project | Ký hiệu | Vai trò |
| :---- | :---- | :---- |
| **TT99.DMN** | Domain | Chứa các Entities, Giá trị, và Logic nghiệp vụ Kế toán TT99. |
| **TT99.APPL** | Application | Xử lý và điều phối các Commands và Queries. |
| **TT99.INFR** | Infrastructure | Chứa Repositories, DB Context, và các dịch vụ hạ tầng. |
| **TT99.PRES** | Presentation | Điểm cuối API (RESTful Endpoints). |

## **🚀 Hướng dẫn Thiết lập và Vận hành**

Yêu cầu tiên quyết là phải cài đặt **.NET SDK** phiên bản mới nhất.

1. **Sao chép Mã nguồn (Clone Repository):**  
   git clone \[https://github.com/vqton/tt99acct.git\](https://github.com/vqton/tt99acct.git)  
   cd tt99acct

2. **Khôi phục các Gói Phụ thuộc:**  
   dotnet restore

3. **Thiết lập Cơ sở Dữ liệu:**  
   * Cần điều chỉnh chuỗi kết nối (Connection String) trong file cấu hình appsettings.json của project TT99.PRES.  
   * Thực hiện cập nhật lược đồ cơ sở dữ liệu (sẽ được xây dựng sau):

dotnet ef database update \--project TT99.INFR

4. **Khởi chạy Ứng dụng:**  
   dotnet run \--project TT99.PRES

   Dịch vụ API sẽ được kích hoạt, thường tại cổng http://localhost:5000 hoặc http://localhost:5001.

## **🤝 Đóng góp và Hợp tác**

Dự án khuyến khích sự đóng góp từ cộng đồng nhằm mở rộng và cải thiện chất lượng mã nguồn. Mọi đề xuất tính năng mới, báo cáo lỗi hoặc yêu cầu cải tiến có thể được gửi thông qua **Issues** hoặc **Pull Requests**.