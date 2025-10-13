# 🇻🇳 Vietnam GL Core  
> **General Ledger Engine cho Doanh nghiệp Nhỏ và Vừa (SME) tại Việt Nam — Tuân thủ Thông tư 133/2016/TT-BTC**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.9%2B-blue)]()
[![Open Source](https://img.shields.io/badge/open--source-yes-green)]()

---

## 🎯 Mục tiêu

`viet-gl-core` là một **thư viện kế toán thuần Python**, giúp doanh nghiệp SME tại Việt Nam:

- Ghi sổ kế toán theo **nguyên tắc kép**
- Tự động sinh **báo cáo tài chính theo Thông tư 133**
- Tuân thủ pháp lý khi **nộp báo cáo thuế theo quý/năm**
- Dễ tích hợp vào bất kỳ hệ thống nào (ERP, web app, CLI, script...)

✅ **Không cần database**  
✅ **Không phụ thuộc framework**  
✅ **Mã nguồn mở – dễ tùy chỉnh – dễ training**

---

## 📦 Tính năng

- [x] Ghi sổ kép (Double-entry accounting)
- [x] Validate giao dịch (cân bằng Nợ/Có, tài khoản hợp lệ)
- [x] Quản lý số dư tài khoản theo thời gian thực
- [x] Sinh báo cáo:
  - `B01-DNN`: Bảng cân đối kế toán
  - `B02-DNN`: Báo cáo kết quả hoạt động kinh doanh
- [ ] Kết chuyển cuối năm (đang phát triển)
- [ ] CLI tool (đang phát triển)
- [ ] Đóng gói PyPI (sắp tới)

> 📌 Dữ liệu cấu hình (COA, mapping báo cáo) được lưu dưới dạng **YAML** → dễ chỉnh sửa, không cần code.

---

## 🚀 Bắt đầu nhanh

### Yêu cầu
- Python 3.9+
- `pip`

### Cài đặt (development mode)

```bash
git clone https://github.com/<your-username>/viet-gl-core.git
cd viet-gl-core
pip install -e .