## Mô hình Domain: Nghiệp vụ & Chứng từ (Transactions)

### Tổng quan

Tài liệu này mô tả **Mô hình Domain: Nghiệp vụ & Chứng từ (Transactions)**, tập trung vào cách một **chứng từ kế toán** (theo Phụ lục I TT99/2025 hoặc mẫu tự thiết kế) được xử lý, xác thực và biến đổi thành một hoặc nhiều **bút toán kế toán** (Journal Entry) hợp lệ, tuân thủ **nguyên tắc ghi sổ kép** và **hệ thống tài khoản kế toán** theo **Thông tư 99/2025/TT-BTC**. Đây là "động cơ" cốt lõi của hệ thống kế toán, thể hiện logic nghiệp vụ (Business Logic) được đóng gói trong lớp **Domain**.

---

### 1. What (Cái gì?)

*   **Là tập hợp các thực thể (Entities), đối tượng giá trị (Value Objects), và dịch vụ (Services) trong lớp miền (Domain Layer)** của hệ thống phần mềm kế toán.
*   **Là quy trình và logic xử lý để chuyển đổi một "Chứng từ kế toán"** (ví dụ: Hóa đơn bán hàng, Phiếu chi tiền mặt, Phiếu nhập kho, Bảng phân bổ khấu hao, Phiếu thu, Phiếu xuất kho...) **thành một hoặc nhiều "Bút toán kế toán" (Journal Entry)** hợp lệ.
*   **Là các quy tắc nghiệp vụ (Business Rules/Invariants)** được định nghĩa và thực thi *trong lớp miền* để đảm bảo tính chính xác, hợp lệ và nhất quán của dữ liệu giao dịch trước khi được ghi nhận vào sổ cái (General Ledger).
*   **Là sự kết hợp giữa các lớp trong kiến trúc (Presentation, Application, Domain, Infrastructure)** để thực hiện một nghiệp vụ kế toán hoàn chỉnh từ đầu vào (chứng từ) đến đầu ra (bút toán trong DB).

---

### 2. Who (Ai?)

*   **Người thực hiện nghiệp vụ kế toán:** Nhân viên kế toán, kế toán trưởng, hoặc các bộ phận nghiệp vụ (mua hàng, bán hàng, nhân sự, kho) thực hiện các công việc tạo ra chứng từ và ghi nhận giao dịch.
*   **Người sử dụng hệ thống:** Kế toán viên nhập liệu, quản lý, kiểm toán nội bộ, và các bên liên quan khác sử dụng hệ thống để xem xét, xử lý và báo cáo thông tin giao dịch.
*   **Các thành phần phần mềm liên quan:**
    *   **Lớp Trình bày (Presentation - `TT99.PRES`):** Người dùng nhập thông tin chứng từ qua giao diện (UI/API). Controller nhận yêu cầu.
    *   **Lớp Ứng dụng (Application - `TT99.APPL`):** `Command` đại diện cho yêu cầu tạo giao dịch (ví dụ: `CreateSalesInvoiceCommand`, `RecordPaymentCommand`). `Handler` (ví dụ: `CreateSalesInvoiceHandler`) xử lý logic ứng dụng (gọi Validator, gọi Domain Service/Entity methods). `Query` và `Handler` cho việc truy vấn giao dịch.
    *   **Lớp Miền (Domain - `TT99.DMN`):** Chứa các **Entities** chính như `JournalEntry`, `LedgerEntry`, `Account`. Chứa các **Value Objects** nếu cần (ví dụ: `Money`, `VATRate`). Chứa **Domain Services** (nếu logic không nằm gọn trong Entity) và **Domain Events** (nếu cần). **Quan trọng nhất:** Chứa *các phương thức và quy tắc* (invariants) xử lý nghiệp vụ, ví dụ:
        *   `JournalEntry.IsBalanced()` (kiểm tra ghi sổ kép).
        *   `JournalEntry.Post()` (kiểm tra `IsBalanced`, rồi đổi trạng thái).
        *   `JournalEntry.AddEntry()` (kiểm tra tính hợp lệ của dòng bút toán).
        *   `Account` (kiểm tra tài khoản tồn tại, loại tài khoản phù hợp).
        *   Các phương thức trong `JournalEntry` hoặc `Account` thực hiện kiểm tra logic nghiệp vụ cụ thể (ví dụ: không ghi nợ TK 3331 trực tiếp, trừ khi có nghiệp vụ cụ thể).
    *   **Lớp Hạ tầng (Infrastructure - `TT99.INFR`):** `DbContext` (`TT99DbContext`) quản lý các Entity. `Repository` thực hiện thao tác với DB. `JournalingService` (triển khai `IJournalingService` từ Application Layer) có thể chứa logic giao dịch DB, gọi Repository, và đảm bảo tính toàn vẹn dữ liệu khi lưu `JournalEntry`.

---

### 3. When (Khi nào?)

*   **Khi một nghiệp vụ kinh tế, tài chính phát sinh** trong doanh nghiệp (ví dụ: bán hàng cho khách, mua nguyên vật liệu, trả lương nhân viên, trích khấu hao TSCĐ).
*   **Khi chứng từ kế toán hợp pháp được lập hoặc nhận** từ bên ngoài (hóa đơn đầu vào, phiếu thu từ khách hàng).
*   **Khi hệ thống xử lý yêu cầu nhập liệu hoặc xử lý tự động** (ví dụ: phân bổ chi phí trả trước cuối tháng, kết chuyển cuối kỳ).
*   **Trong suốt kỳ kế toán**, khi các giao dịch liên tục phát sinh và cần được ghi nhận kịp thời.
*   **Cụ thể trong hệ thống phần mềm:**
    *   Khi một `Command` (ví dụ: `CreateSalesInvoiceCommand`) được gửi thông qua MediatR từ Controller.
    *   Khi `CreateSalesInvoiceHandler` nhận Command, gọi Validator, gọi các phương thức trong Domain để xử lý (tạo `JournalEntry`, kiểm tra `IsBalanced`, `Post`...).
    *   Khi `JournalEntry` cuối cùng được xác nhận là hợp lệ, nó được truyền cho `IJournalingService` để lưu vào cơ sở dữ liệu thông qua `DbContext` và `Repository`.

---

### 4. Why (Tại sao?)

*   **Để tuân thủ các quy định kế toán của Việt Nam**, đặc biệt là **Thông tư 99/2025/TT-BTC**, yêu cầu ghi nhận đầy đủ, kịp thời, chính xác, trung thực, minh bạch các nghiệp vụ kinh tế phát sinh theo **nguyên tắc ghi sổ kép** và **hệ thống tài khoản quy định** (Phụ lục II TT99).
*   **Để đảm bảo tính chính xác và toàn vẹn dữ liệu kế toán:** Logic nghiệp vụ được đặt trong lớp Domain (Domain Logic) đảm bảo rằng các bút toán được tạo ra là hợp lệ (cân bằng, tài khoản tồn tại, tuân thủ quy tắc ghi Nợ/Có theo từng loại tài khoản).
*   **Để phục vụ cho việc lập Báo cáo tài chính:** Các giao dịch được ghi nhận chính xác là đầu vào cơ sở để tổng hợp và tạo ra các **Báo cáo tài chính theo mẫu Phụ lục III của TT99/2025** (Bảng Cân đối Kế toán, Báo cáo Kết quả Kinh doanh, Báo cáo Lưu chuyển Tiền tệ, Bản Thuyết minh).
*   **Để hỗ trợ kiểm soát nội bộ và kiểm toán:** Một quy trình xử lý giao dịch rõ ràng, có kiểm tra, có căn cứ và ghi nhận đầy đủ giúp kiểm soát hoạt động và phục vụ kiểm toán dễ dàng. Nhật ký hệ thống (Audit Log) ghi lại quá trình xử lý.
*   **Để phản ánh đúng bản chất kinh tế của các giao dịch:** Mô hình miền đảm bảo logic xử lý phản ánh đúng bản chất của nghiệp vụ thực tế, không chỉ dựa trên hình thức pháp lý, giúp số liệu kế toán có ý nghĩa và đáng tin cậy.

---

### 5. Ví dụ minh họa: Chuyển đổi từ Chứng từ sang Bút toán

**Ví dụ: Ghi nhận nghiệp vụ bán hàng (chưa có hóa đơn điện tử, chỉ ghi nhận bán hàng nội bộ)**

1.  **Chứng từ đầu vào:** Người dùng nhập thông tin vào một form "Tạo hóa đơn bán hàng" trong hệ thống (hoặc API nhận dữ liệu). Dữ liệu này bao gồm: Số hóa đơn, Ngày, Khách hàng (131), Doanh thu (511), Thuế GTGT đầu ra (3331), Giá vốn (632), Mã hàng đã bán (liên quan đến TK 155/156 - giả sử có mapping).
2.  **Tạo Command:** `CreateSalesInvoiceCommand` được tạo với các thông tin trên.
3.  **Xử lý Command (Application Layer):**
    *   `CreateSalesInvoiceHandler` nhận Command.
    *   Gọi `FluentValidation` để kiểm tra dữ liệu đầu vào (ví dụ: ngày không âm, số tiền dương).
4.  **Xử lý trong Domain Layer:**
    *   `Handler` tạo một đối tượng `JournalEntry` mới (ví dụ: `new JournalEntry(voucherNumber, transactionDate, narration)`).
    *   Dựa trên thông tin từ `CreateSalesInvoiceCommand`, `Handler` tạo các `LedgerEntry`:
        *   `new LedgerEntry("131", "Phải thu khách hàng ABC", debitAmount, 0)` (Nợ 131).
        *   `new LedgerEntry("511", "Doanh thu bán hàng", 0, revenueAmount)` (Có 511).
        *   `new LedgerEntry("3331", "Thuế GTGT phải nộp", 0, vatAmount)` (Có 3331).
        *   `new LedgerEntry("632", "Giá vốn hàng bán", costOfGoodsSoldAmount, 0)` (Nợ 632).
        *   `new LedgerEntry("155", "Thành phẩm", 0, costOfGoodsSoldAmount)` (Có 155 - giả sử ghi giảm trực tiếp).
    *   `Handler` gọi `journalEntry.AddEntry(ledgerEntry)` cho từng dòng.
    *   `Handler` gọi `journalEntry.IsBalanced()` để kiểm tra tính cân bằng (Tổng Nợ = Tổng Có).
    *   Nếu cân bằng, `Handler` gọi `journalEntry.Post()` để đánh dấu bút toán đã được ghi sổ.
    *   **Lưu ý:** Các logic kiểm tra tài khoản tồn tại, loại tài khoản đúng quy tắc (ví dụ: TK 131 là tài sản, tăng ghi Nợ) cũng được thực hiện *trong Domain* hoặc *trước khi gọi Domain* với sự hỗ trợ của Domain.
5.  **Lưu vào DB (Infrastructure Layer):**
    *   `Handler` gọi `IJournalingService.CreateJournalEntryAsync(journalEntry)`.
    *   `JournalingService` (trong `TT99.INFR.Services`) nhận `JournalEntry`.
    *   `JournalingService` thêm `JournalEntry` vào `DbContext` (`_context.JournalEntries.Add(entry)`).
    *   `JournalingService` gọi `_context.SaveChangesAsync()` *trong một giao dịch DB (Database Transaction)* để đảm bảo toàn bộ bút toán được ghi nhận hoặc bị rollback nếu có lỗi.
6.  **Kết quả:** Một `JournalEntry` hoàn chỉnh, hợp lệ, đã được ghi vào bảng `JournalEntries` và `LedgerEntries` (nếu là Owned Entity) trong cơ sở dữ liệu. Bút toán này phản ánh đúng nghiệp vụ bán hàng và tuân thủ nguyên tắc ghi sổ kép và hệ thống tài khoản TT99.

---

### 6. Kết luận

Mô hình Domain: Nghiệp vụ & Chứng từ là trung tâm của hệ thống kế toán phần mềm. Việc thiết kế và thực thi logic nghiệp vụ *trong lớp miền* là then chốt để đảm bảo hệ thống *phản ánh chính xác*, *tuân thủ pháp luật kế toán* (TT99/2025), và *cung cấp dữ liệu đáng tin cậy* cho các báo cáo tài chính và quá trình ra quyết định.