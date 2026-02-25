# Domain Logic - Circular 99/2025/TT-BTC

## 1. Core Principles

### 1.1 Double-Entry System
- Every transaction has two sides: **Debit** and **Credit**
- **Golden Rule**: Sum(Debit) = Sum(Credit) for every voucher
- Imbalance = Sum(Debit) - Sum(Credit) must be ZERO

### 1.2 Circular 99/2025/TT-BTC Compliance
- Standard: **Thông tư 99/2025/TT-BTC** (Hộ kinh doanh & DN siêu nhỏ)
- **PROHIBITED**: Không sử dụng Thông tư 133, 200 trừ khi có yêu cầu cụ thể

### 1.3 Immutability
- Once **POSTED**, a voucher becomes **IMMUTABLE**
- No editing, deletion, or modification allowed after posting
- Only **VOID** action is permitted (creates reversal trail)

---

## 2. Chart of Accounts (Circular 99/2025)

### TÀI SẢN NGẮN HẠN (1xx)
| Code | Name | Type |
|------|------|------|
| 111 | Tiền | Asset |
| 112 | Tiền gửi không kỳ hạn | Asset |
| 121 | Chứng khoán kinh doanh | Asset |
| 128 | Tiền gửi có kỳ hạn | Asset |
| 131 | Phải thu của khách hàng | Asset |
| 133 | Thuế GTGT được khấu trừ | Asset |
| 136 | Phải thu nội bộ | Asset |
| 138 | Phải thu khác | Asset |
| 141 | Tạm ứng | Asset |
| 151 | Hàng mua đang đi đường | Asset |
| 152 | Nguyên liệu, vật liệu | Asset |
| 153 | Công cụ, dụng cụ | Asset |
| 154 | Chi phí sản xuất KD dở dang | Asset |
| 155 | Sản phẩm | Asset |
| 156 | Hàng hóa | Asset |
| 157 | Hàng gửi bán | Asset |
| 158 | Hàng hóa kho bảo thuế | Asset |

### TÀI SẢN DÀI HẠN (2xx)
| Code | Name | Type |
|------|------|------|
| 211 | Tài sản cố định hữu hình | Asset |
| 213 | Tài sản cố định vô hình | Asset |
| 214 | Hao mòn và khấu hao TSCĐ | Asset |
| 217 | Bất động sản đầu tư | Asset |
| 221 | Đầu tư vào công ty con | Asset |
| 222 | Đầu tư vào công ty liên kết | Asset |
| 228 | Đầu tư khác | Asset |
| 241 | Xây dựng cơ bản dở dang | Asset |
| 242 | Chi phí trả trước dài hạn | Asset |
| 244 | Chênh lệch tỷ giá hối đoái | Asset |
| 251 | Tài sản thuế thu nhập hoãn lại | Asset |

### NGUỒN VỐN (3xx)
| Code | Name | Type |
|------|------|------|
| 311 | Phải trả người bán | Liability |
| 312 | Người mua trả tiền trước | Liability |
| 313 | Thuế và các khoản phải nộp NN | Liability |
| 314 | Phải trả người lao động | Liability |
| 315 | Chi phí phải trả | Liability |
| 316 | Phải trả nội bộ | Liability |
| 317 | Phải trả khác | Liability |
| 318 | Vay và nợ thuê tài chính | Liability |
| 319 | Dự phòng phải trả | Liability |
| 320 | Doanh thu chưa thực hiện | Liability |
| 321 | Chênh lệch tỷ giá hối đoái | Liability |
| 322 | Thuế thu nhập hoãn lại phải trả | Liability |
| 331 | Quỹ của doanh nghiệp | Equity |
| 333 | Phải trả cổ tức, lợi nhuận | Liability |
| 411 | Vốn đầu tư của chủ sở hữu | Equity |
| 412 | Chênh lệch tỷ giá hối đoái | Equity |
| 413 | Chênh lệch đánh giá lại tài sản | Equity |
| 421 | Lợi nhuận sau thuế CP | Equity |

### DOANH THU (5xx)
| Code | Name | Type |
|------|------|------|
| 511 | Doanh thu bán hàng | Revenue |
| 515 | Doanh thu tài chính | Revenue |
| 516 | Doanh thu hoạt động khác | Revenue |

### CHI PHÍ (6xx)
| Code | Name | Type |
|------|------|------|
| 611 | Mua hàng | Expense |
| 621 | Chi phí NVL, VL trực tiếp | Expense |
| 622 | Chi phí nhân công trực tiếp | Expense |
| 623 | Chi phí sử dụng máy thi công | Expense |
| 627 | Chi phí sản xuất chung | Expense |
| 632 | Giá vốn hàng bán | Expense |
| 635 | Chi phí tài chính | Expense |
| 641 | Chi phí bán hàng | Expense |
| 642 | Chi phí quản lý DN | Expense |
| 643 | Chi phí hoạt động khác | Expense |
| 644 | Chi phí thuế TNDN | Expense |

### TÀI KHOẢN XÁC ĐỊNH KẾT QUẢ (9xx)
| Code | Name | Type |
|------|------|------|
| 911 | Xác định kết quả KD | Expense |

---

## 3. Voucher Lifecycle

```
[DRAFT] ──────► [POSTED] ──────► [VOID]
```

### 3.1 DRAFT
- Initial state when created
- Can be edited
- Can be POSTED or VOIDED

### 3.2 POSTED
- **Locked state** - IMMUTABLE
- Ledger entries created
- Contains: PostedAt, PostedBy timestamps

### 3.3 VOID
- Terminal state
- Original voucher preserved (audit trail)
- Contains: VoidedAt, VoidedBy timestamps

---

## 4. Validation Rules

### 4.1 Balance Check
- Sum(Debit) - Sum(Credit) = 0 (strict equality)

### 4.2 Account Validation
- Only **Leaf Accounts** (IsDetail = true) can be posted to
- Parent accounts cannot be used for posting

### 4.3 Fiscal Period Check
- Voucher.Date must be within an OPEN fiscal period

### 4.4 Line Rules
| Rule | Description |
|------|-------------|
| Mutually Exclusive | A line must have either Debit OR Credit |
| Non-Zero | Either Debit or Credit must be > 0 |
| Valid Account | Account must exist and be a leaf account |

---

## 5. Business Rules Summary

| Rule | Description |
|------|-------------|
| Double-Entry | Sum(Debit) = Sum(Credit) |
| Immutability | POSTED vouchers cannot be modified |
| One-Way Flow | DRAFT → POSTED → VOID |
| Fiscal Period | Must post within open period |
| Leaf Account Only | Only leaf accounts can be posted to |
| Audit Trail | All actions timestamped and user-tracked |

---

## 6. Notes

- Circular 99 allows businesses to voluntarily open sub-accounts (Level 2, Level 3)
- Account 215 (Biological Assets) available for Agricultural sector
- Account 332 (Dividends payable) added per TT99
