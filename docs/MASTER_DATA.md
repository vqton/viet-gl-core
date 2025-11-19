## Tổng quan

Tài liệu này mô tả các loại **Master Data** (Dữ liệu gốc) chính được sử dụng trong hệ thống kế toán TT99. Master Data là các danh mục dữ liệu cơ bản, ổn định, làm nền tảng cho việc ghi nhận các nghiệp vụ kinh tế phát sinh và đảm bảo tính nhất quán, chính xác trong toàn hệ thống theo quy định của **Thông tư 99/2025/TT-BTC**.

## Mục lục

1.  [Hệ thống Tài khoản Kế toán (Chart of Accounts)](#1-hệ-thống-tài-khoản-kế-toán-chart-of-accounts)
2.  [Danh mục Đối tượng Kế toán (Object Master Data)](#2-danh-mục-đối-tượng-kế-toán-object-master-data)
3.  [Chính sách Kế toán (Accounting Policies)](#3-chính-sách-kế-toán-accounting-policies)
4.  [Quản lý và Quản trị Master Data](#4-quản-lý-và-quản-trị-master-data)

---

## 1. Hệ thống Tài khoản Kế toán (Chart of Accounts)

### 1.1. Mô tả

Là danh mục các tài khoản được sử dụng để ghi nhận các nghiệp vụ kinh tế phát sinh, tuân thủ theo **Phụ lục II** của TT99/2025.

### 1.2. Cấu trúc

*   **Tài khoản cấp 1:** Phản ánh nhóm tài khoản lớn (Tài sản, Nợ phải trả, Vốn, Doanh thu, Chi phí...).
*   **Tài khoản cấp 2, cấp 3:** Phân tích chi tiết hơn tài khoản cấp 1.
*   **Tài khoản loại trừ (Contra Accounts):** Ví dụ: Hao mòn (214), Dự phòng (229, 352), Giảm trừ doanh thu (521).

### 1.3. Yêu cầu/Quy tắc

*   Phải được thiết lập ban đầu theo Phụ lục II.
*   Có thể mở rộng cấp 3, 4... nhưng không làm thay đổi nội dung phản ánh của cấp 1, 2.
*   Có phân loại (AccountType: Asset, Liability, Equity, Revenue, Expense, Other).
*   Có phân cấp (Level: 1, 2, 3...).
*   Có tài khoản cha (ParentAccountNumber) nếu là cấp con.

### 1.4. Liên quan đến Mã nguồn

*   Entity: `Account` (trong `TT99.DMN.Ents`).
*   Database: Bảng `Accounts`, seeding data từ `ChartOfAccounts_TT99.csv`.

---

## 2. Danh mục Đối tượng Kế toán (Object Master Data)

### 2.1. Khách hàng/Nhà cung cấp (Customer/Supplier)

*   **Mô tả:** Danh sách các bên liên quan đến giao dịch mua bán, thanh toán.
*   **Thuộc tính chính:** Mã, Tên, Mã số thuế, Địa chỉ, Người liên hệ, Tài khoản ngân hàng.
*   **Liên quan đến:** TK 131, 331, 511, 611, v.v.

### 2.2. Vật tư, Hàng hóa, Dịch vụ (Inventory)

*   **Mô tả:** Danh sách các loại vật tư, hàng hóa, dịch vụ mà doanh nghiệp mua, bán, sử dụng.
*   **Thuộc tính chính:** Mã hàng, Tên hàng, Đơn vị tính, Nhóm hàng, Mã vạch, Thuế suất.
*   **Liên quan đến:** TK 152, 155, 156, 611, 632, 511, v.v.

### 2.3. Tài sản cố định (Fixed Assets)

*   **Mô tả:** Danh sách các tài sản cố định hữu hình, vô hình của doanh nghiệp.
*   **Thuộc tính chính:** Mã TSCĐ, Tên TSCĐ, Năm SX, Năm đưa vào SD, Nguyên giá, Thời gian khấu hao, Phương pháp khấu hao, Bộ phận sử dụng.
*   **Liên quan đến:** TK 211, 212, 213, 214, 215, 217, v.v.

### 2.4. Nhân viên (Employee)

*   **Mô tả:** Danh sách nhân viên trong công ty.
*   **Thuộc tính chính:** Mã NV, Họ tên, Bộ phận, Chức vụ.
*   **Liên quan đến:** TK 334, 622, 6271, v.v.

### 2.5. Bộ phận/Phòng ban (Department)

*   **Mô tả:** Danh sách các bộ phận, phòng ban trong doanh nghiệp.
*   **Thuộc tính chính:** Mã BP, Tên BP.
*   **Liên quan đến:** Phân bổ chi phí (TK 627, 641, 642...).

### 2.6. Kho (Warehouse)

*   **Mô tả:** Danh sách các kho nơi lưu trữ vật tư, hàng hóa.
*   **Thuộc tính chính:** Mã kho, Tên kho, Địa chỉ.
*   **Liên quan đến:** Nhập xuất tồn kho (TK 152, 155, 156...).

*(Có thể bổ sung các đối tượng khác như Công trình, Hợp đồng nếu áp dụng)*

---

## 3. Chính sách Kế toán (Accounting Policies)

*   **Mô tả:** Các phương pháp và chính sách kế toán được doanh nghiệp áp dụng, ảnh hưởng đến cách ghi nhận và xử lý nghiệp vụ.
*   **Ví dụ:**
    *   Phương pháp tính giá xuất kho (Bình quân, FIFO, Đích danh).
    *   Phương pháp khấu hao TSCĐ (Đường thẳng, số dư giảm dần...).
    *   Phương pháp phân bổ chi phí sản xuất chung.
*   **Lưu ý:** Việc thiết lập và thay đổi các chính sách này cần được kiểm soát và ghi nhận theo quy định (liên quan đến BCTC và Thuyết minh BCTC).

---

## 4. Quản lý và Quản trị Master Data

*   **Quyền truy cập:** Ai được phép thêm/sửa/xóa các loại Master Data (thường là Admin, Kế toán trưởng).
*   **Quy trình cập nhật:** Có cần phê duyệt khi thêm mới hoặc sửa đổi Master Data quan trọng không?
*   **Tính toàn vẹn dữ liệu:** Hệ thống có kiểm tra ràng buộc khi sử dụng Master Data trong giao dịch không (ví dụ: tài khoản không tồn tại, khách hàng không tồn tại)?
*   **Audit Log:** Có ghi nhận lại lịch sử thay đổi Master Data không?

---
