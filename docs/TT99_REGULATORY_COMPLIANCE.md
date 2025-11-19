# TT99_REGULATORY_COMPLIANCE.md

## Tổng quan

Tài liệu này mô tả các quy tắc bắt buộc theo luật định áp dụng cho phần mềm kế toán theo **Thông tư 99/2025/TT-BTC** ngày 27 tháng 10 năm 2025 của Bộ Tài chính hướng dẫn chế độ kế toán doanh nghiệp (sau đây gọi tắt là TT99/2025).

Phần mềm kế toán cần đảm bảo tuân thủ các quy định này để đảm bảo tính chính xác, minh bạch và phù hợp với pháp luật kế toán Việt Nam hiện hành kể từ ngày 01/01/2026, khi TT99/2025 chính thức có hiệu lực thay thế cho TT200/2014 và TT133/2016.

## Mục lục

1.  [Hệ thống tài khoản kế toán](#hệ-thống-tài-khoản-kế-toán)
2.  [Ghi sổ kép](#ghi-sổ-kép)
3.  [Chứng từ kế toán](#chứng-từ-kế-toán)
4.  [Sổ kế toán](#sổ-kế-toán)
5.  [Báo cáo tài chính](#báo-cáo-tài-chính)
6.  [Nguyên tắc kế toán](#nguyên-tắc-kế-toán)
7.  [Chuyển đổi từ Chế độ kế toán cũ (TT200/133)](#chuyển-đổi-từ-chế-độ-kế-toán-cũ-tt200133)
8.  [Quản trị và Kiểm soát nội bộ](#quản-trị-và-kiểm-soát-nội-bộ)

## 1. Hệ thống tài khoản kế toán

### 1.1. Bắt buộc sử dụng hệ thống tài khoản theo Phụ lục II của TT99/2025

*   **Quy định:** Doanh nghiệp phải sử dụng hệ thống tài khoản kế toán được quy định trong Phụ lục II của TT99/2025 làm cơ sở để ghi chép các nghiệp vụ kinh tế, tài chính phát sinh kể từ ngày 01/01/2026.
*   **Yêu cầu phần mềm:**
    *   Cung cấp danh mục tài khoản kế toán chuẩn theo Phụ lục II của TT99/2025.
    *   Cho phép phân loại tài khoản theo đúng quy định (Tài sản, Nợ phải trả, Vốn chủ sở hữu, Doanh thu, Chi phí, Thu nhập khác, Chi phí khác, Xác định kết quả kinh doanh, Thuế TNDN, và các tài khoản khác theo cấu trúc mới).
    *   Hỗ trợ tài khoản cấp 1, cấp 2, cấp 3 (và có thể cấp chi tiết hơn nếu cần thiết theo quy định hoặc yêu cầu quản lý nội bộ, nhưng phải đảm bảo tuân thủ cấp 1, 2, 3 theo Phụ lục II).
    *   Đảm bảo các tài khoản được sử dụng trong các bút toán kế toán là hợp lệ theo hệ thống tài khoản mới.
    *   Hỗ trợ các tài khoản loại trừ như Hao mòn TSCĐ (TK 214), Dự phòng (TK 229, 352), Các khoản giảm trừ doanh thu (TK 521), v.v.

### 1.2. Tùy chỉnh tài khoản

*   **Quy định:** Doanh nghiệp có thể mở rộng tài khoản cấp 3 hoặc chi tiết hơn nếu cần để phù hợp với đặc điểm hoạt động và yêu cầu quản lý, nhưng không được làm thay đổi kết cấu và nội dung phản ánh của tài khoản cấp 1 và cấp 2 theo Phụ lục II của TT99/2025.
*   **Yêu cầu phần mềm:**
    *   Cho phép tạo tài khoản cấp 3 và cấp chi tiết hơn dưới tài khoản cấp 2, đảm bảo tính phân cấp theo quy định mới.
    *   Có cơ chế kiểm tra và đảm bảo rằng việc thêm tài khoản mới không vi phạm cấu trúc và mối quan hệ cha-con được thiết lập theo TT99/2025.
    *   Ghi nhận rõ tài khoản là cấp mấy và có tài khoản cha (nếu có) như đã cấu trúc trong `Account.cs` trước đây.

## 2. Ghi sổ kép

### 2.1. Nguyên tắc

*   **Quy định:** Mỗi nghiệp vụ kinh tế, tài chính phát sinh phải được ghi trên ít nhất hai tài khoản, trong đó có một tài khoản ghi Nợ và một tài khoản ghi Có với số tiền bằng nhau, theo nguyên tắc ghi sổ kép.
*   **Yêu cầu phần mềm:**
    *   Thực hiện kiểm tra tính cân bằng (Tổng Nợ = Tổng Có) cho mỗi bút toán kế toán trước khi cho phép ghi sổ.
    *   Không cho phép ghi sổ (Post) một bút toán không cân bằng.
    *   Ghi nhận và lưu trữ cả dòng Nợ và dòng Có trong một bút toán.
    *   Hỗ trợ việc ghi Nợ, ghi Có vào đúng tài khoản theo quy định (ví dụ, tài khoản tài sản tăng ghi Nợ, giảm ghi Có; tài khoản nợ phải trả tăng ghi Có, giảm ghi Nợ, v.v.).

## 3. Chứng từ kế toán

### 3.1. Căn cứ ghi sổ

*   **Quy định:** Việc ghi sổ kế toán phải dựa trên chứng từ kế toán hợp pháp, đã được xử lý và duyệt theo quy định.
*   **Yêu cầu phần mềm:**
    *   Mỗi bút toán kế toán (Journal Entry) cần có thông tin liên kết hoặc mô tả về chứng từ gốc (Số chứng từ, ngày chứng từ, người lập, người duyệt).
    *   Hỗ trợ lưu trữ hoặc liên kết với hình ảnh/chứng từ điện tử nếu quy định yêu cầu hoặc doanh nghiệp có nhu cầu.
    *   Áp dụng các mẫu chứng từ hướng dẫn tại Phụ lục I của TT99/2025 hoặc các mẫu được thiết kế thêm/sửa đổi theo Điều 16 của Luật Kế toán (mà doanh nghiệp tự ban hành), đảm bảo đầy đủ nội dung bắt buộc.

## 4. Sổ kế toán

### 4.1. Loại sổ

*   **Quy định:** Doanh nghiệp phải sử dụng các loại sổ kế toán phù hợp để phản ánh đầy đủ, kịp thời, trung thực, minh bạch các nghiệp vụ kinh tế, tài chính phát sinh. TT99/2025 không quy định cứng nhắc các mẫu sổ cụ thể như trước, mà nhấn mạnh vào việc tổ chức hệ thống thông tin kế toán.
*   **Yêu cầu phần mềm:**
    *   Có thể cung cấp các báo cáo tương ứng như Sổ nhật ký, Sổ cái, Sổ chi tiết theo từng tài khoản, theo đối tượng.
    *   Dữ liệu được lưu trữ và tổ chức để dễ dàng truy xuất theo yêu cầu của các loại sổ này, đảm bảo nguyên tắc kế toán và phục vụ lập Báo cáo tài chính.
    *   Hỗ trợ truy vết (traceability) từ chứng từ gốc đến bút toán kế toán và đến số dư cuối kỳ.

## 5. Báo cáo tài chính

### 5.1. Bắt buộc

*   **Quy định:** Doanh nghiệp phải lập các Báo cáo tài chính theo mẫu và nội dung quy định tại Phụ lục III của TT99/2025 và các văn bản hướng dẫn liên quan, bắt đầu từ kỳ báo cáo áp dụng TT99/2025 (kỳ đầu tiên tính theo ngày hiệu lực 01/01/2026).
*   **Yêu cầu phần mềm:**
    *   Dữ liệu được ghi nhận theo hệ thống tài khoản TT99/2025 phải có thể tổng hợp để tạo ra các Báo cáo tài chính theo đúng mẫu quy định mới (Báo cáo tình hình tài chính - Mẫu B 01 - DN, Báo cáo kết quả hoạt động kinh doanh - Mẫu B 02 - DN, Báo cáo lưu chuyển tiền tệ - Mẫu B 03 - DN, Bản thuyết minh Báo cáo tài chính - Mẫu B 09 - DN và các mẫu khác nếu có).
    *   Hỗ trợ truy vấn dữ liệu theo tài khoản, theo kỳ kế toán, theo đối tượng để phục vụ lập báo cáo theo quy định mới.
    *   Hỗ trợ lập báo cáo giữa niên độ (nếu cần) theo mẫu quy định (B 01a - DN, B 02a - DN, B 03a - DN, B 09a - DN, B 01b - DN, B 02b - DN, B 03b - DN).

## 6. Nguyên tắc kế toán

### 6.1. Nhất quán

*   **Quy định:** Phương pháp kế toán được áp dụng phải được thực hiện nhất quán từ năm này sang năm khác, trừ khi có quy định mới hoặc lý do chính đáng được chấp thuận.
*   **Yêu cầu phần mềm:** Cấu hình hệ thống tài khoản, phương pháp tính giá, khấu hao, dự phòng... cần được thiết lập rõ ràng và ổn định, chỉ thay đổi khi có thay đổi theo TT99/2025 hoặc được phê duyệt theo quy định.

### 6.2. Cơ sở ghi nhận (Dồn tích)

*   **Quy định:** Kế toán ghi nhận nghiệp vụ theo cơ sở dồn tích (accrual basis), không theo cơ sở tiền tệ (cash basis), trừ khi có quy định cụ thể khác.
*   **Yêu cầu phần mềm:** Hỗ trợ ghi nhận doanh thu, chi phí khi phát sinh quyền, nghĩa vụ, bất kể thời điểm thu, chi tiền, theo quy định của TT99/2025.

### 6.3. Trọng yếu

*   **Quy định:** Các thông tin trọng yếu phải được trình bày đầy đủ, rõ ràng trong Báo cáo tài chính theo TT99/2025.
*   **Yêu cầu phần mềm:** Có thể cần tính năng phân loại hoặc đánh dấu các nghiệp vụ trọng yếu để phục vụ lập báo cáo và thuyết minh theo quy định mới.

### 6.4. Hoạt động liên tục

*   **Quy định:** Báo cáo tài chính được lập trên cơ sở giả định doanh nghiệp là hoạt động liên tục, trừ khi doanh nghiệp có kế hoạch đóng cửa hoặc bị chia, tách, hợp nhất, sáp nhập (trong những trường hợp này, vẫn có quy định riêng về lập và trình bày BCTC).
*   **Yêu cầu phần mềm:** Hệ thống ghi nhận và xử lý dữ liệu phải phù hợp với giả định hoạt động liên tục, trừ khi có sự kiện đặc biệt được xác định rõ ràng.

### 6.5. Đơn vị tiền tệ trong kế toán

*   **Quy định:** Đơn vị tiền tệ trong kế toán là Đồng Việt Nam (VND). Trường hợp doanh nghiệp chủ yếu thu, chi bằng ngoại tệ, đáp ứng các điều kiện cụ thể, thì được chọn một loại ngoại tệ làm đơn vị tiền tệ trong kế toán.
*   **Yêu cầu phần mềm:**
    *   Hỗ trợ ghi sổ và lập BCTC bằng VND theo mặc định.
    *   Hỗ trợ (nếu cần) việc chọn và sử dụng một ngoại tệ khác làm đơn vị tiền tệ trong kế toán, bao gồm việc chuyển đổi tỷ giá và quản lý chênh lệch tỷ giá hối đoái theo quy định.

## 7. Chuyển đổi từ Chế độ kế toán cũ (TT200/133)

### 7.1. Chốt số dư đầu kỳ theo TT99/2025

*   **Quy định:** Khi chuyển sang áp dụng TT99/2025 từ ngày 01/01/2026, doanh nghiệp phải thực hiện chốt số dư đầu kỳ theo hệ thống tài khoản mới dựa trên số liệu cuối kỳ theo chế độ kế toán cũ (TT200/2014 và TT133/2016). TT99/2025 có hướng dẫn cụ thể về việc điều chỉnh số liệu (ví dụ: chuyển số dư một số tài khoản như 441, 466 sang 4118; chuyển chi tiết sửa chữa lớn chưa hoàn thành từ 2413 sang 2414; chuyển chi tiết tài khoản 338 về cổ tức sang 332; v.v.).
*   **Yêu cầu phần mềm:**
    *   Có chức năng hỗ trợ chuyển đổi số dư đầu kỳ (Opening Balance) từ hệ thống tài khoản cũ sang hệ thống tài khoản mới theo quy định chuyển đổi cụ thể trong TT99/2025.
    *   Ghi nhận và lưu trữ đầy đủ quá trình và lý do điều chỉnh (nếu có) trong hệ thống để đảm bảo tính minh bạch và kiểm tra được.

## 8. Quản trị và Kiểm soát nội bộ

### 8.1. Tạo lập và quản lý giao dịch

*   **Quy định:** Việc tạo lập, thực hiện, quản lý và kiểm soát các giao dịch kinh tế phát sinh của doanh nghiệp phải tuân thủ quy định của pháp luật, cơ chế chính sách có liên quan (Điều 3 TT99/2025).
*   **Yêu cầu phần mềm:**
    *   Hỗ trợ thiết lập các luồng công việc (workflow) và phân quyền truy cập, xử lý dữ liệu phù hợp với quy trình kiểm soát nội bộ của doanh nghiệp.
    *   Ghi nhận lịch sử thay đổi (audit trail) đối với các giao dịch, bút toán quan trọng.

---

*Ghi chú: Tài liệu này dựa trên nội dung của Thông tư 99/2025/TT-BTC. Việc tuân thủ đầy đủ các quy định pháp luật kế toán cần được đảm bảo bởi các chuyên gia kế toán và pháp lý có chuyên môn, dựa trên văn bản chính thức của Bộ Tài chính. Phần mềm cung cấp công cụ để hỗ trợ việc tuân thủ theo TT99/2025.*
