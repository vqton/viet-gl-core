# 🗺️ Roadmap: Vietnam GL Engine cho SME (Theo Thông tư 133/2016/TT-BTC)

> **Mục tiêu**: Xây dựng một **thư viện GL (General Ledger) mở, nhẹ, tuân thủ pháp lý Việt Nam**, dành riêng cho doanh nghiệp nhỏ và vừa (SME).  
> **Nguyên tắc**: Logic nghiệp vụ tách biệt, không phụ thuộc DB/UI, dễ tích hợp, dễ mở rộng.

---

## 🎯 Tổng quan

| Giai đoạn | Tên | Mục tiêu chính | Thời gian ước lượng |
|----------|-----|----------------|----------------------|
| **Giai đoạn 0** | Chuẩn bị nền tảng | Hiểu TT 133, thiết kế domain model | 1–3 ngày |
| **Giai đoạn 1** | GL cốt lõi | Ghi sổ kép, quản lý số dư, validate | 1–2 tuần |
| **Giai đoạn 2** | Báo cáo tài chính | Sinh B01-DNN, B02-DNN theo quý/năm | 1 tuần |
| **Giai đoạn 3** | Đóng gói & mở rộng | CLI, package, kết chuyển, khóa sổ | 1–2 tuần |

> 💡 **MVP Scope**: 1 công ty, 1 tiền tệ (VND), không multi-currency, không multi-branch.

---

## 🧭 Giai đoạn 0: Chuẩn bị nền tảng

### Mục tiêu
Hiểu rõ nghiệp vụ kế toán SME theo Thông tư 133 và thiết kế kiến trúc domain trước khi code.

### Các bước cần làm
1. **Nghiên cứu Thông tư 133/2016/TT-BTC**
   - Tập trung vào:
     - Hệ thống tài khoản (Phụ lục 1)
     - Mẫu báo cáo B01-DNN, B02-DNN (Phụ lục 4)
     - Nguyên tắc ghi sổ kép, kết chuyển cuối năm
   - Link: [Thông tư 133 - Bộ Tài chính](https://thuvienphapluat.vn/van-ban/Thue-Phi-Le-Phi/Thong-tu-133-2016-TT-BTC-che-do-ke-toan-doanh-nghiep-nho-va-vua-330375.aspx)

2. **Xác định phạm vi MVP**
   - Chỉ hỗ trợ:
     - 1 công ty
     - 1 đơn vị tiền tệ (VND)
     - Báo cáo theo quý/năm theo TT 133

3. **Thiết kế Domain Model**
   - Các thực thể chính:
     - `Account`
     - `JournalEntry` / `JournalLine`
     - `Ledger`
     - `TrialBalance`
   - → Vẽ sơ đồ class (dù bằng tay hoặc [draw.io](https://draw.io))

4. **Chuẩn bị cấu hình mẫu**
   - Tạo file `config/tt133_coa.yaml` (toàn bộ tài khoản theo TT 133)
   - Tạo file `config/reports/b01_dnn.yaml`, `b02_dnn.yaml` (mapping báo cáo)

### Cột mốc hoàn thành
- [ ] Có file `tt133_coa.yaml` đầy đủ
- [ ] Có sơ đồ class domain model

---

## ⚙️ Giai đoạn 1: Xây dựng GL cốt lõi

### Mục tiêu
Hệ thống có thể **ghi sổ kép hợp lệ** và **theo dõi số dư từng tài khoản** (in-memory).

### Các bước cần làm (theo thứ tự)

1. **Xây dựng `Account` và `AccountChart`**
   - Load COA từ YAML → dict `{code: Account}`
   - Hỗ trợ tra cứu theo mã

2. **Xây dựng `JournalLine` và `JournalEntry`**
   - Mỗi dòng chỉ có **Nợ hoặc Có**
   - Entry chứa nhiều dòng

3. **Viết validator cho nguyên tắc kép**
   - Tổng Nợ = Tổng Có
   - Tất cả tài khoản phải tồn tại trong COA

4. **Xây dựng `Ledger`**
   - Lưu số dư: `{account_code: {debit: ..., credit: ...}}`
   - Phương thức `.post(entry)` → cập nhật số dư nếu hợp lệ

5. **Viết unit test**
   - Test giao dịch hợp lệ → pass
   - Test giao dịch không cân bằng → raise error
   - Test tài khoản không tồn tại → raise error

### Cột mốc hoàn thành (M1)
- [ ] Ghi được 1 journal hợp lệ và xem số dư tài khoản
- [ ] 100% unit test pass

---

## 📊 Giai đoạn 2: Sinh báo cáo tài chính

### Mục tiêu
Từ số dư trong `Ledger`, tự động tạo **Bảng cân đối kế toán (B01-DNN)** và **Kết quả HĐKD (B02-DNN)** theo quý/năm.

### Các bước cần làm

1. **Xây dựng `TrialBalance`**
   - Tổng hợp số dư tất cả tài khoản tại một thời điểm

2. **Thiết kế cơ chế mapping báo cáo**
   - Dùng file YAML để định nghĩa:
     - Dòng báo cáo ↔ danh sách tài khoản
     - Dấu (+/-) dựa trên `normal_balance`

3. **Viết hàm báo cáo**
   - `generate_balance_sheet(ledger, period)`
   - `generate_income_statement(ledger, period)`

4. **Hỗ trợ lọc theo kỳ**
   - Helper: `get_quarter("2025-04-15") → "2025-Q2"`

5. **Xuất báo cáo ra dict/JSON**
   - Chưa cần PDF — tập trung vào **dữ liệu đúng**

### Cột mốc hoàn thành (M2)
- [ ] Báo cáo B01-DNN hiển thị đúng số tiền (dù chỉ 2 tài khoản)
- [ ] Có thể sinh báo cáo cho quý I, II, III, IV

---

## 📦 Giai đoạn 3: Đóng gói & mở rộng

### Mục tiêu
Biến thư viện thành **sản phẩm có thể dùng được** trong thực tế.

### Các bước cần làm

1. **Xử lý kỳ kế toán & số dư đầu kỳ**
   - Lưu balances theo kỳ
   - Tính số dư đầu kỳ = số dư cuối kỳ trước

2. **Kết chuyển cuối năm**
   - Tự động tạo journal kết chuyển:
     - Doanh thu (511...) → Có 421
     - Chi phí (632, 641...) → Nợ 421

3. **Khóa kỳ kế toán (Period Locking)**
   - Ngăn ghi sổ vào kỳ đã chốt (dù chỉ in-memory)

4. **Xây dựng CLI tool đơn giản**
   ```bash
   gl-cli post --file sale.json
   gl-cli report --type B01-DNN --period 2025-Q2
