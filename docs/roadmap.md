# 🗺️ Roadmap: Vietnam GL Engine cho SME (Theo Thông tư 133/2016/TT-BTC)

> **Mục tiêu**: Xây dựng một **thư viện GL (General Ledger) mở, nhẹ, tuân thủ pháp lý Việt Nam**, dành riêng cho doanh nghiệp nhỏ và vừa (SME).  
> **Nguyên tắc**: Logic nghiệp vụ tách biệt, không phụ thuộc DB/UI, dễ tích hợp, dễ mở rộng.

---

## 🎯 Tổng quan

| Giai đoạn | Tên | Mục tiêu chính | Trạng thái |
|----------|-----|----------------|------------|
| **Giai đoạn 0** | Chuẩn bị nền tảng | Hiểu TT 133, thiết kế domain model | ✅ Hoàn thành |
| **Giai đoạn 1** | GL cốt lõi | Ghi sổ kép, quản lý số dư, validate | ✅ Hoàn thành |
| **Giai đoạn 2** | Báo cáo tài chính | Sinh B01-DNN, B02-DNN theo quý/năm | ✅ Hoàn thành |
| **Giai đoạn 3** | Đóng gói & mở rộng | CLI, package, kết chuyển, khoá sổ | ✅ Hoàn thành |
| **Giai đoạn 4** | Tính năng kế toán nâng cao | Số dư đầu kỳ, B03/B09-DNN, sub-ledger... | 🔄 Đang thực hiện |
| **Giai đoạn 4.1** | Khoá kỳ kế toán | Ngăn ghi sổ vào kỳ đã chốt | ✅ **ĐÃ HOÀN THÀNH** |

---

## 🧭 Giai đoạn 0: Chuẩn bị nền tảng

### Mục tiêu
Hiểu rõ nghiệp vụ kế toán SME theo Thông tư 133 và thiết kế kiến trúc domain trước khi code.

### Các bước đã làm
1. **Nghiên cứu Thông tư 133/2016/TT-BTC**
   - Tập trung vào:
     - Hệ thống tài khoản (Phụ lục 1)
     - Mẫu B01-DNN, B02-DNN (Phụ lục 4)
     - Nguyên tắc ghi sổ kép, kết chuyển cuối năm
   - Link: [Thông tư 133 - Bộ Tài chính](https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Thong-tu-133-2016-TT-BTC-che-do-ke-toan-doanh-nghiep-nho-va-vua-330375.aspx)

2. **Xác định phạm vi MVP**
   - Chỉ hỗ trợ:
     - 1 công ty
     - 1 đơn vị tiền tệ (VND)
     - Không multi-currency, không multi-branch
     - Chỉ báo cáo theo quý/năm theo TT 133

3. **Thiết kế Domain Model**
   - Các thực thể chính:
     - `Account`
     - `JournalEntry` / `JournalLine`
     - `Ledger`
     - `TrialBalance`
   - → Vẽ sơ đồ class (dù bằng tay hoặc [draw.io](https://draw.io))

4. **Chuẩn bị cấu hình mẫu**
   - Tạo file `tt133_coa.yaml` chứa toàn bộ tài khoản theo TT 133
   - Tạo file `b01_dnn.yaml`, `b02_dnn.yaml` cho mapping báo cáo

### Ý nghĩa:
> **Đừng code khi chưa hiểu nghiệp vụ**. Giai đoạn này giúp bạn **tránh sai lầm kiến trúc** sau này (ví dụ: thiết kế tài khoản không hỗ trợ kết chuyển).

---

## ⚙️ Giai đoạn 1: Xây dựng GL cốt lõi

### Mục tiêu
Hệ thống có thể **ghi sổ kép hợp lệ** và **theo dõi số dư từng tài khoản** (in-memory).

### Các bước đã làm (theo thứ tự)

1. **Xây dựng `Account` và `AccountChart`**
   - Load COA từ YAML → tạo dict `{code: Account}`
   - Hỗ trợ tra cứu tài khoản theo mã

2. **Xây dựng `JournalLine` và `JournalEntry`**
   - Mỗi dòng chỉ có **Nợ hoặc Có**
   - Entry chứa nhiều dòng

3. **Viết validator cho nguyên tắc kép**
   - Tổng Nợ = Tổng Có
   - Tất cả tài khoản phải tồn tại trong COA

4. **Xây dựng `Ledger`**
   - Lưu số dư: `{account_code: {debit: ..., credit: ...}}`
   - Phương thức `.post(entry)` → cập nhật số dư nếu hợp lệ

5. **Viết unit test cho từng chức năng**
   - Test giao dịch hợp lệ → pass
   - Test giao dịch không cân bằng → raise error
   - Test tài khoản không tồn tại → raise error

### Ý nghĩa:
> Đây là **trái tim của hệ thống**. Nếu GL core không đúng, mọi báo cáo sau đều sai.  
> **Không cần DB ở giai đoạn này** — dùng in-memory dict là đủ.

---

## 📊 Giai đoạn 2: Sinh báo cáo tài chính

### Mục tiêu
Từ số dư trong `Ledger`, tự động tạo **Bảng cân đối kế toán (B01-DNN)** và **Kết quả HĐKD (B02-DNN)** theo quý/năm.

### Các bước đã làm

1. **Xây dựng `TrialBalance`**
   - Tổng hợp số dư tất cả tài khoản tại một thời điểm

2. **Thiết kế cơ chế mapping báo cáo**
   - Dùng file YAML để định nghĩa:
     - Dòng báo cáo nào gồm những tài khoản nào
     - Dấu (+/-) dựa trên `normal_balance`

3. **Viết hàm `generate_balance_sheet()` và `generate_income_statement()`**
   - Input: `Ledger`, `period` (ví dụ: "2025-Q2")
   - Output: dict hoặc object báo cáo

4. **Hỗ trợ lọc theo kỳ**
   - Viết helper: `get_quarter(date) → "2025-Q2"`
   - (Tạm thời: giả sử tất cả journal đều thuộc kỳ cần báo cáo)

5. **Xuất báo cáo ra JSON / dict**
   - Chưa cần PDF — tập trung vào **dữ liệu đúng trước**

### Ý nghĩa:
> **Báo cáo tài chính là đầu ra cuối cùng** của GL. Nếu mapping sai, dù số liệu đúng → báo cáo vẫn sai.  
> Dùng **cấu hình (YAML)** thay vì hard-code → dễ điều chỉnh theo quy định mới.

---

## 📦 Giai đoạn 3: Đóng gói & mở rộng

### Mục tiêu
Biến thư viện thành **sản phẩm có thể dùng được** trong thực tế.

### Các bước đã làm

1. **Xử lý kỳ kế toán & số dư đầu kỳ**
   - Lưu `balances` theo kỳ (thay vì toàn bộ)
   - Hỗ trợ tính **số dư đầu kỳ** = số dư cuối kỳ trước

2. **Kết chuyển cuối năm**
   - Tự động tạo journal kết chuyển:
     - Doanh thu (511...) → Có 421
     - Chi phí (632, 641...) → Nợ 421
   - Cập nhật lại `Ledger`

3. **Khóa kỳ kế toán (Period Locking)**
   - Ngăn ghi sổ vào kỳ đã chốt
   - (Cập nhật trong `Ledger.post` để kiểm tra trạng thái kỳ)

4. **Xây dựng CLI tool đơn giản**
   ```bash
   gl-cli post --file sale.json
   gl-cli report --type B01-DNN --period 2025-Q2

   ## 🔐 Giai đoạn 4: Tính năng kế toán nâng cao (Theo phân tích PSE & Chuyên gia kế toán)

### Mục tiêu
Đáp ứng **đầy đủ yêu cầu pháp lý và thực tế vận hành** của doanh nghiệp SME Việt Nam.

### Thứ tự ưu tiên (theo phân tích chuyên gia tài chính/kế toán)

| Mức độ | Tên tính năng | Lý do | Trạng thái |
|--------|----------------|-------|------------|
| 🔴 **Bắt buộc** | Khoá kỳ kế toán | Yêu cầu kiểm toán, pháp lý | ✅ **ĐÃ HOÀN THÀNH** (Giai đoạn 4.1) |
| 🔴 **Bắt buộc** | Số dư đầu kỳ | Báo cáo tài chính yêu cầu | 📋 Lên kế hoạch |
| 🔴 **Bắt buộc** | B03-DNN (Lưu chuyển tiền tệ) | Theo TT 133 | 📋 Lên kế hoạch |
| 🔴 **Bắt buộc** | B09-DNN (Thuyết minh) | Báo cáo cuối năm | 📋 Lên kế hoạch |
| 🔴 **Bắt buộc** | Hạch toán chi tiết theo đối tượng | Theo dõi công nợ, hàng tồn kho | 📋 Lên kế hoạch |
| 🟠 **Bắt buộc** | Phân loại theo loại hình | Áp dụng đúng tài khoản | 📋 Lên kế hoạch |
| 🟡 **Ưu tiên cao** | Tự động tính thuế | Hỗ trợ kê khai | 📋 Lên kế hoạch |
| 🟡 **Ưu tiên cao** | Kiểm tra đối chiếu | Yêu cầu kiểm toán | 📋 Lên kế hoạch |
| 🟡 **Ưu tiên trung bình** | Multi-currency | Doanh nghiệp có ngoại tệ | 📋 Lên kế hoạch |
| 🟡 **Ưu tiên trung bình** | Multi-company | Tập đoàn | 📋 Lên kế hoạch |
| 🟡 **Ưu tiên thấp** | Nhập bank statement | Tự động hóa | 📋 Lên kế hoạch |
| 🟡 **Ưu tiên thấp** | Xuất XML/Excel chuẩn | Nộp hồ sơ | 📋 Lên kế hoạch |

### Các bước tiếp theo (theo thứ tự ưu tiên)

#### 🔴 1. Số dư đầu kỳ (Opening Balance)
- **Mục tiêu**: Cho phép nhập số dư đầu kỳ cho từng tài khoản.
- **Cách làm**:
  - Thêm phương thức `set_opening_balance(account_code, debit, credit)` vào `Ledger`.
  - Khi tính số dư cuối kỳ, cộng số dư đầu kỳ + phát sinh trong kỳ.
- **Tác động**: Cần cập nhật `Ledger`, `TrialBalance`, `Report`.

#### 🔴 2. Báo cáo B03-DNN (Lưu chuyển tiền tệ)
- **Mục tiêu**: Tự động sinh báo cáo lưu chuyển tiền tệ theo mẫu TT 133.
- **Cách làm**:
  - Tạo `b03_dnn.yaml` với cấu trúc đúng mẫu.
  - Viết `generate_cash_flow_statement(ledger, config_path, period)` trong `services/reporting.py`.
- **Tác động**: Thêm module báo cáo, thêm test.

#### 🔴 3. Báo cáo B09-DNN (Thuyết minh)
- **Mục tiêu**: Tự động sinh thuyết minh báo cáo tài chính.
- **Cách làm**:
  - Tạo `b09_dnn.yaml`.
  - Viết `generate_explanatory_notes(ledger, config_path, period)`.
- **Tác động**: Thêm module báo cáo, thêm test.

#### 🟡 4. Hạch toán chi tiết theo đối tượng (Sub-ledger)
- **Mục tiêu**: Theo dõi công nợ, hàng tồn kho theo khách hàng, lô hàng...
- **Cách làm**:
  - Thêm `reference` hoặc `dimension` vào `JournalLine`.
  - Ví dụ: `JournalLine("131", debit=10M, reference={"customer": "C001"})`
- **Tác động**: Thay đổi `JournalLine`, `Ledger`, `Report`.