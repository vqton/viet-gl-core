## Tổng quan

Tài liệu này mô tả kiến trúc phần mềm cho hệ thống kế toán TT99, được thiết kế để xử lý hiệu quả các yêu cầu phức tạp và quy định nghiêm ngặt của **Thông tư 99/2025/TT-BTC**. Kiến trúc này nhấn mạnh vào **tính tách biệt (Separation of Concerns)**, **tính mở rộng (Scalability)**, **tính bảo trì (Maintainability)**, và **tính tuân thủ (Compliance)**.

Mô hình được áp dụng là **Domain-Driven Design (DDD)** kết hợp với mẫu hình **Command Query Responsibility Segregation (CQRS)** sử dụng thư viện **MediatR**. Điều này giúp phân tách rõ ràng giữa logic nghiệp vụ (Domain), yêu cầu từ người dùng (Application), và cách hệ thống giao tiếp với thế giới bên ngoài (Presentation/Infrastructure).

---

## Mô hình Kiến trúc Lớp (Layered Architecture)

Hệ thống được chia thành các lớp (Layers) chính sau:

### 1. Lớp Trình bày (Presentation Layer - `TT99.PRES`)

*   **Mục đích:** Là điểm tiếp xúc đầu tiên với người dùng hoặc hệ thống bên ngoài (ví dụ: API HTTP).
*   **Trách nhiệm:**
    *   Tiếp nhận yêu cầu (Requests) từ người dùng (qua API, UI).
    *   Xác thực người dùng (Authentication).
    *   Phân quyền người dùng (Authorization).
    *   Gửi yêu cầu (Commands/Queries) tới lớp Ứng dụng thông qua **MediatR**.
    *   Trả về phản hồi (Responses) cho người dùng.
*   **Thành phần chính:**
    *   **Controllers:** Xử lý các endpoint API.
    *   **Mô hình DTO đầu vào (Input DTOs):** Dữ liệu nhận từ client.
    *   **Mô hình DTO đầu ra (Output DTOs/ViewModels):** Dữ liệu trả về cho client.
    *   **Middleware:** Xử lý cross-cutting concerns như logging, exception handling cơ bản.

### 2. Lớp Ứng dụng (Application Layer - `TT99.APPL`)

*   **Mục đích:** Điều phối các hoạt động giữa các lớp, chứa logic ứng dụng và xử lý yêu cầu.
*   **Trách nhiệm:**
    *   Nhận Commands (yêu cầu thay đổi trạng thái) và Queries (yêu cầu dữ liệu) từ lớp Trình bày.
    *   Xác thực đầu vào (Input Validation) sử dụng **FluentValidation**.
    *   Gọi các phương thức trong **Domain Services** hoặc **Aggregate Roots**.
    *   Giao tiếp với **Infrastructure Services** (nếu cần) để truy cập dữ liệu hoặc hệ thống bên ngoài.
    *   Trả kết quả (thành công/thất bại) về cho lớp Trình bày.
    *   Xử lý các hành vi chung (Cross-Cutting Concerns) thông qua **MediatR Pipeline Behaviors** (ví dụ: Validation, Logging).
*   **Thành phần chính:**
    *   **Commands:** Mô tả các yêu cầu thay đổi (ví dụ: `CreateJournalEntryCommand`).
    *   **Queries:** Mô tả các yêu cầu truy vấn (ví dụ: `GetGeneralLedgerQuery`).
    *   **Handlers:** Xử lý Commands/Queries (ví dụ: `CreateJournalEntryHandler`, `GetGeneralLedgerHandler`).
    *   **Validators:** Xác thực Commands/Queries (ví dụ: `CreateJournalEntryCommandValidator`).
    *   **Pipeline Behaviors:** Áp dụng logic chung (ví dụ: `ValidationBehavior`).
    *   **Interfaces (cho Services):** Định nghĩa các giao diện cho các dịch vụ được sử dụng bởi lớp này (ví dụ: `IJournalingService`, `IReportQueryService`).

### 3. Lớp Miền (Domain Layer - `TT99.DMN`)

*   **Mục đích:** Trung tâm của hệ thống, chứa *mô hình miền (Domain Model)* và *logic nghiệp vụ cốt lõi (Business Logic)* theo TT99.
*   **Trách nhiệm:**
    *   Định nghĩa các **Entities**, **Value Objects**, và **Aggregate Roots** phản ánh đúng mô hình nghiệp vụ kế toán (Tài khoản, Bút toán, Sổ cái, v.v.).
    *   Đóng gói logic nghiệp vụ phức tạp và các quy tắc ràng buộc (Business Rules/Invariants) *bên trong* các Aggregate Roots và Entities (ví dụ: `JournalEntry.IsBalanced()`, `JournalEntry.Post()`).
    *   Đảm bảo tính toàn vẹn dữ liệu theo nguyên tắc ghi sổ kép, cấu trúc tài khoản TT99, và các nguyên tắc kế toán khác.
    *   Định nghĩa các **Interfaces** cho các dịch vụ phụ thuộc vào lớp miền (Repository Interfaces).
*   **Thành phần chính:**
    *   **Entities:** Các đối tượng có định danh (ID) (ví dụ: `Account`, `JournalEntry`).
    *   **Value Objects:** Các đối tượng không có định danh, chỉ định nghĩa giá trị (ví dụ: `LedgerEntry` nếu chỉ là dòng chi tiết trong `JournalEntry`).
    *   **Aggregate Roots:** Các Entity gốc quản lý các Entity/Value Object con (ví dụ: `JournalEntry`).
    *   **Domain Services:** Chứa logic nghiệp vụ không nằm gọn trong một Entity/Aggregate cụ thể (nếu cần).
    *   **Domain Events:** Sự kiện xảy ra trong miền (nếu cần cho các hành động phản hồi).
    *   **Interfaces (cho Repositories):** Giao diện để truy cập dữ liệu (ví dụ: `IJournalEntryRepository`).

### 4. Lớp Hạ tầng (Infrastructure Layer - `TT99.INFR`)

*   **Mục đích:** Cung cấp các dịch vụ kỹ thuật và triển khai các interface từ các lớp trên (Application, Domain).
*   **Trách nhiệm:**
    *   Triển khai **Repository Interfaces** để truy cập cơ sở dữ liệu (thông qua EF Core).
    *   Triển khai các **Application Service Interfaces** (nếu logic phức tạp cần tách khỏi Domain Service).
    *   Cấu hình và quản lý **DbContext** (EF Core).
    *   Giao tiếp với các hệ thống bên ngoài (API bên thứ 3 như Hóa đơn điện tử, Ngân hàng - nếu cần).
    *   Cung cấp các tiện ích kỹ thuật (Logging, Caching - nếu có).
*   **Thành phần chính:**
    *   **Repositories:** Triển khai `IRepository` hoặc interface cụ thể (ví dụ: `JournalEntryRepository`).
    *   **Services:** Triển khai interface từ Application/Domain (ví dụ: `JournalingService`, `ReportQueryService`).
    *   **Data (DbContext, Configuration):** `TT99DbContext`, `Entity Configuration` (Fluent API).
    *   **External Service Adapters:** Lớp để gọi API bên ngoài.

---

## Mẫu hình CQRS với MediatR

*   **Command:** Đại diện cho một yêu cầu thay đổi trạng thái hệ thống (Write). Được xử lý bởi `IRequestHandler<Command, TResponse>`.
*   **Query:** Đại diện cho một yêu cầu lấy dữ liệu (Read). Được xử lý bởi `IRequestHandler<Query, TResponse>`.
*   **MediatR:** Thư viện đóng vai trò trung gian (Mediator), nhận Command/Query và chuyển chúng đến Handler tương ứng. Hỗ trợ các Pipeline Behaviors để áp dụng logic chung.

---

## Tách biệt Loại trừ (Contra Accounts) và Tài khoản cấp (Account Levels)

*   **Entity `Account`:** Được thiết kế để hỗ trợ `Level` và `ParentAccountNumber`, phản ánh đúng cấu trúc phân cấp trong Phụ lục II của TT99.
*   **Logic Miền:** Có thể được mở rộng để xử lý riêng các tài khoản loại trừ (Contra Accounts) như Hao mòn (214), Dự phòng (229, 352), Giảm trừ doanh thu (521) nếu cần logic đặc biệt trong các phép tính tổng hợp (ví dụ: tính số dư thực tế của tài khoản tài sản sau khi trừ hao mòn).

---

## Tóm tắt

Kiến trúc này phân tách rõ ràng các mối quan tâm, đặt logic nghiệp vụ cốt lõi (theo TT99) vào lớp **Domain**, sử dụng **CQRS** để tách biệt đọc/ghi, và **MediatR** để giảm sự phụ thuộc giữa các thành phần. Điều này tạo ra một hệ thống dễ hiểu, dễ kiểm thử, dễ bảo trì và mở rộng, đồng thời đảm bảo tính tuân thủ với các quy định kế toán phức tạp.
