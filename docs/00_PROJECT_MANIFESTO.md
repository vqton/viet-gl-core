# AIErp - Project Manifesto

## 1. Luật Nghiệp vụ Tối thượng (Core Business Rules)
- **Standard**: Tuân thủ nghiêm ngặt **Thông tư 99/2025/TT-BTC** (Hộ kinh doanh & DN siêu nhỏ). 
- **Strictly Prohibited**: Không sử dụng Thông tư 133, 200 trừ khi có yêu cầu cụ thể.
- **Accounting Principle**: 
    - Bút toán luôn luôn phải Cân bằng (Debit = Credit).
    - Chỉ được hạch toán vào tài khoản CẤP CUỐI (Leaf Account). Không hạch toán vào tài khoản tổng hợp (Parent).

## 2. Tiêu chuẩn Kỹ thuật (Technical Standards)
- **Architecture**: Clean Lite (Domain -> Application <- Infrastructure/WebAPI).
- **Database**: Primary là **SQLite** (file: `AIErp.db`).
- **Language**: C# 13, .NET 9.
- **Testing**: Mọi logic nghiệp vụ trong Domain và Application PHẢI có Unit Test đi kèm.

## 3. Quy tắc AI Agent
- Trước khi tạo bất kỳ Entity hay Service nào, phải đối chiếu với `docs/01_DOMAIN_LOGIC.md` và `docs/03_DATA_DICTIONARY.md`.
- Nếu phát hiện mâu thuẫn giữa yêu cầu của người dùng và Manifesto, AI phải cảnh báo ngay lập tức.