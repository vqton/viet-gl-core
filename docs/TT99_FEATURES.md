```markdown
# TT99_FEATURES.md

## Tổng quan

Tài liệu này mô tả chi tiết các tính năng (Features) và yêu cầu hệ thống (UR/NFR) cho một hệ thống phần mềm kế toán doanh nghiệp nhằm đáp ứng nhu cầu quản trị thực tế và *tuân thủ đầy đủ* các quy định trong **Thông tư 99/2025/TT-BTC** ngày 27/10/2025 của Bộ Tài chính, có hiệu lực từ ngày 01/01/2026.

## Mục lục

1.  [Phân hệ Quản trị Hệ thống & Danh mục](#1-phân-hệ-quản-trị-hệ-thống--danh-mục-system--master-data)
2.  [Phân hệ Kế toán Tổng hợp](#2-phân-hệ-kế-toán-tổng-hợp-general-ledger--gl)
3.  [Phân hệ Tiền mặt & Tiền gửi](#3-phân-hệ-tiền-mặt--tiền-gửi-cash--bank)
4.  [Phân hệ Mua hàng & Công nợ Phải trả](#4-phân-hệ-mua-hàng--công-nợ-phải-trả-purchase--ap)
5.  [Phân hệ Bán hàng & Công nợ Phải thu](#5-phân-hệ-bán-hàng--công-nợ-phải-thu-sales--ar)
6.  [Phân hệ Kho](#6-phân-hệ-kho-inventory)
7.  [Phân hệ Tài sản Cố định & CCDC](#7-phân-hệ-tài-sản-cố-định--ccdc-fixed-assets)
8.  [Phân hệ Giá thành Sản xuất (Nâng cao)](#8-phân-hệ-giá-thành-sản-xuất-nâng-cao-costing-)
9.  [Phân hệ Thuế](#9-phân-hệ-thuế-tax)
10. [Yêu cầu Phi Chức năng (NFR)](#10-yêu-cầu-phi-chức-năng-nfr)
11. [Chuyển đổi dữ liệu](#11-chuyển-đổi-dữ-liệu-data-migrationconversion)
12. [UI/UX & Tiện ích Người dùng](#12-uiux--tiện-ích-người-dùng-uiux--user-utilities)

---

## 1. Phân hệ Quản trị Hệ thống & Danh mục (System & Master Data)

Đây là nền tảng dữ liệu dùng chung cho toàn bộ hệ thống.

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ (User Requirement) | Ghi chú (TT99 / Cạnh tranh) |
| :--- | :--- | :--- | :--- |
| **SYS-01** | **Đa Chi nhánh/Đơn vị** | Hỗ trợ mô hình Tổng công ty - Chi nhánh. Dữ liệu có thể hạch toán độc lập hoặc hợp nhất. | TT99 không cấm, nhiều DN lớn cần. |
| **SYS-02** | **Phân quyền Chi tiết** | Phân quyền đến từng chức năng (Thêm/Sửa/Xóa/Xem/In) và phạm vi dữ liệu (chỉ xem chứng từ của mình hoặc của cả phòng). | TT99 yêu cầu kiểm soát. |
| **SYS-03** | **Nhật ký Truy cập (Audit Log)** | Ghi lại lịch sử thay đổi dữ liệu: Ai làm? Lúc nào? Giá trị cũ/mới? (Bắt buộc cho kiểm toán). **Phải đảm bảo tính toàn vẹn dữ liệu, truy vết được nguồn gốc giao dịch, kiểm toán được. Nhật ký phải *không thể sửa/xóa* (chỉ ghi thêm), và có thể *kiểm tra định kỳ*.** | *TT99: Yêu cầu hệ thống thông tin kế toán phải đảm bảo tính chính xác, minh bạch, kiểm tra, kiểm soát.* |
| **SYS-04** | **Hỗ trợ Đa tiền tệ (Multi-currency)** | Hệ thống hỗ trợ ghi nhận giao dịch, số dư, báo cáo bằng nhiều loại tiền tệ. Tự động đánh giá chênh lệch tỷ giá. | *TT99: Yêu cầu ghi nhận và đánh giá tài sản, công nợ bằng ngoại tệ theo tỷ giá quy định.* |
| **SYS-05** | **Định kỳ Kế toán (Accounting Periods)** | Cho phép thiết lập và quản lý các kỳ kế toán (quý, năm), đảm bảo việc khóa/mở kỳ. | *TT99: Quy định rõ kỳ lập BCTC.* |
| **MST-01** | **Đối tượng Pháp nhân** | Quản lý Khách hàng/Nhà cung cấp: Tự động lấy thông tin từ Mã số thuế. Phân loại theo Nhóm, Khu vực. | |
| **MST-02** | **Vật tư Hàng hóa** | Quản lý Mã hàng, Mã vạch, Đơn vị tính quy đổi (Thùng -> Hộp -> Cái), Thuế suất VAT ngầm định. | |
| **MST-03** | **Danh mục Tài khoản** | **Tuân thủ Phụ lục II TT99/2025. Hỗ trợ Tài khoản theo dõi chi tiết theo: Đối tượng, Công trình, Hợp đồng, Khoản mục chi phí. Hỗ trợ tài khoản *loại trừ* (contra accounts) như Hao mòn (214), Dự phòng (229, 352), Giảm trừ doanh thu (521). Hỗ trợ tài khoản cấp 1, 2, 3 theo Phụ lục II.** | *TT99: Phụ lục II quy định hệ thống tài khoản kế toán.* |
| **MST-04** | **Chính sách Kế toán (Accounting Policies)** | Cho phép thiết lập các chính sách như: Phương pháp tính giá thành, Phương pháp khấu hao TSCĐ, Phương pháp tính giá xuất kho. | *TT99: Yêu cầu áp dụng các nguyên tắc và phương pháp kế toán nhất quán. Hệ thống cần ghi nhận và có thể in ra các chính sách này (liên quan đến BCTC).* |

---

## 2. Phân hệ Kế toán Tổng hợp (General Ledger - GL)

Trái tim của hệ thống, nơi tập hợp số liệu để lên Báo cáo Tài chính.

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ | Ghi chú (TT99 / Cạnh tranh) |
| :--- | :--- | :--- | :--- |
| **GL-01** | **Phiếu Kế toán Khác** | Dùng cho các bút toán điều chỉnh, phân bổ lương, trích trước chi phí. **Phải đảm bảo *tất cả* các bút toán đều tuân thủ nguyên tắc *ghi sổ kép* (Tổng Nợ = Tổng Có) như TT99 quy định.** | |
| **GL-02** | **Phân bổ Chi phí Trả trước** | Tự động phân bổ chi phí (TK 242) cho nhiều kỳ, nhiều đối tượng tập hợp chi phí. | |
| **GL-03** | **Đánh giá Chênh lệch Tỷ giá** | Tự động đánh giá lại số dư các khoản mục tiền tệ có gốc ngoại tệ cuối kỳ theo tỷ giá thực tế/bình quân (TT99). | |
| **GL-04** | **Kết chuyển Tự động** | Định nghĩa sẵn các cặp tài khoản kết chuyển (Doanh thu -> 911 -> Lợi nhuận) để chạy tự động cuối kỳ. **Các bút toán kết chuyển phải phản ánh đúng *nội dung kinh tế* và *cấu trúc báo cáo* theo *Phụ lục III* của TT99/2025.** | |
| **GL-05** | **Khóa sổ/Mở sổ** | Chức năng "Khóa sổ" ngăn chặn sửa đổi dữ liệu trước ngày khóa. Cho phép "Mở sổ" có điều kiện (chỉ Admin). **Việc khóa sổ là bắt buộc tại *thời điểm kết thúc kỳ kế toán* để lập Báo cáo tài chính. Quy trình mở sổ lại (nếu cần) phải có *kiểm soát chặt chẽ* và *lý do chính đáng*, ghi nhận đầy đủ.** | *TT99: Yêu cầu đảm bảo tính chính xác, minh bạch của thông tin kế toán.* |
| **GL-06** | **Tự động tạo Bút toán** | Tự động tạo bút toán kế toán từ các chứng từ đầu vào khác (nhập mua, bán hàng, nhập kho, khấu hao...). | *Tính năng phổ biến, tăng hiệu suất và giảm sai sót.* |
| **GL-07** | **Hạch toán theo nhiều kỳ** | Cho phép hạch toán bút toán vào kỳ trước nếu chưa khóa sổ. | *Tính năng phổ biến, cần thiết khi phát hiện sai sót.* |
| **GL-08** | **Đối chiếu tài khoản** | So sánh số dư và phát sinh giữa các tài khoản nội bộ (ví dụ: 131 với sổ chi tiết khách hàng) hoặc với bên ngoài (ngân hàng). | *Tăng độ tin cậy dữ liệu.* |
| **GL-RPT** | **Báo cáo Bắt buộc** | Sổ Nhật ký chung, Sổ Cái, Bảng Cân đối số phát sinh, Nhật ký - Sổ Cái. **PHẢI BAO GỒM: Các Báo cáo tài chính theo *Phụ lục III* của TT99/2025: *Báo cáo tình hình tài chính (B 01 - DN)*, *Báo cáo kết quả hoạt động kinh doanh (B 02 - DN)*, *Báo cáo lưu chuyển tiền tệ (B 03 - DN)*, và *Bản thuyết minh Báo cáo tài chính (B 09 - DN)*. Hỗ trợ các mẫu báo cáo giữa niên độ (B 01a, B 02a, B 03a, B 09a, B 01b, B 02b, B 03b).** | *TT99: Phụ lục III quy định mẫu Báo cáo tài chính.* |
| **GL-RPT-01** | **Báo cáo Tuỳ chỉnh (Custom Reports)** | Cho phép người dùng tự thiết kế báo cáo theo nhu cầu quản trị nội bộ. | *Tính năng cạnh tranh cao.* |

---

## 3. Phân hệ Tiền mặt & Tiền gửi (Cash & Bank)

Quản lý chặt chẽ dòng tiền vào ra.

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ | Ghi chú (TT99 / Cạnh tranh) |
| :--- | :--- | :--- | :--- |
| **CSH-01** | **Phiếu Thu/Chi** | In phiếu trực tiếp từ phần mềm theo mẫu **01-TT, 02-TT**. Hỗ trợ in hàng loạt. | *TT99: Phụ lục I quy định mẫu chứng từ.* |
| **CSH-02** | **Ủy nhiệm chi** | In Ủy nhiệm chi theo mẫu của các ngân hàng phổ biến tại Việt Nam (VCB, ACB, BIDV...). | |
| **CSH-03** | **Đối chiếu Ngân hàng** | Nhập sao kê ngân hàng (Excel) và tự động đối chiếu với sổ kế toán để phát hiện chênh lệch. | |
| **CSH-04** | **Theo dõi Tạm ứng** | Quản lý tạm ứng theo từng nhân viên, từng vụ việc. Kiểm soát thanh toán tạm ứng. | |
| **CSH-05** | **Tích hợp Ngân hàng (Bank Feeds)** | (Nâng cao) Kết nối trực tiếp với ngân hàng để đồng bộ giao dịch vào phần mềm. | *Tính năng cạnh tranh cao, giảm thao tác thủ công.* |
| **CSH-RPT** | **Báo cáo** | Sổ Quỹ tiền mặt (Mẫu S07-DN), Sổ Tiền gửi ngân hàng (S08-DN), Báo cáo lưu chuyển tiền tệ (Dự báo). | |

---

## 4. Phân hệ Mua hàng & Công nợ Phải trả (Purchase & AP)

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ | Ghi chú (TT99 / Cạnh tranh) |
| :--- | :--- | :--- | :--- |
| **PUR-01** | **Quy trình Mua hàng** | Đơn đặt hàng (PO) -> Phiếu nhập mua -> Hóa đơn mua hàng -> Thanh toán. | |
| **PUR-02** | **Phân bổ Chi phí Mua** | Tự động phân bổ chi phí vận chuyển, bốc xếp, hải quan vào giá vốn hàng nhập (theo Giá trị hoặc Số lượng). | |
| **PUR-03** | **Hàng về trước HĐ về sau** | Cho phép nhập kho ghi nhận nợ (TK 335), khi hóa đơn về thực hiện đối trừ. | |
| **PUR-04** | **Quản lý Công nợ** | Theo dõi công nợ theo Hóa đơn, theo Hạn thanh toán. Cảnh báo nợ đến hạn. | |
| **PUR-05** | **Tích hợp Hóa đơn điện tử (E-Invoice)** | Kết nối API với các nhà cung cấp HĐĐT để nhận hóa đơn mua vào. | *Bắt buộc theo quy định hiện hành.* |
| **PUR-06** | **So sánh giá nhà cung cấp** | So sánh giá mua từ các nhà cung cấp khác nhau cho cùng một mặt hàng. | *Tính năng hỗ trợ quản trị mua hàng.* |
| **PUR-RPT** | **Báo cáo** | Bảng kê mua vào, Tổng hợp công nợ phải trả, Chi tiết công nợ theo hóa đơn, Phân tích tuổi nợ. | |

---

## 5. Phân hệ Bán hàng & Công nợ Phải thu (Sales & AR)

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ | Ghi chú (TT99 / Cạnh tranh) |
| :--- | :--- | :--- | :--- |
| **SAL-01** | **Chính sách Giá** | Thiết lập bảng giá theo nhóm khách hàng, theo khoảng thời gian khuyến mãi. | |
| **SAL-02** | **Chiết khấu** | Tự động tính chiết khấu thương mại, chiết khấu thanh toán trên hóa đơn. | |
| **SAL-03** | **Hóa đơn Điện tử (E-Invoice)** | **(Critical)** Kết nối trực tiếp (API) với các nhà cung cấp (Viettel, VNPT, MISA, BKAV, SoftDreams) để phát hành, hủy, điều chỉnh hóa đơn. | |
| **SAL-04** | **Hàng bán trả lại** | Xử lý nghiệp vụ khách trả lại hàng: Giảm trừ công nợ, Nhập lại kho. | |
| **SAL-05** | **CRM Cơ bản** | (Nâng cao) Quản lý thông tin liên hệ, lịch sử giao dịch, cơ hội bán hàng. | *Tính năng cạnh tranh, tích hợp.* |
| **SAL-06** | **Tích hợp Sàn TMĐT** | (Nâng cao) Đồng bộ đơn hàng từ các sàn như Shopee, Lazada, Tiki. | *Phổ biến cho DN thương mại điện tử.* |
| **SAL-RPT** | **Báo cáo** | Bảng kê bán ra, Doanh số theo nhân viên/mặt hàng, Phân tích lãi gộp từng đơn hàng. | |

---

## 6. Phân hệ Kho (Inventory)

Đây là phân hệ phức tạp nhất đối với doanh nghiệp thương mại/sản xuất.

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ | Ghi chú (TT99 / Cạnh tranh) |
| :--- | :--- | :--- | :--- |
| **INV-01** | **Nhập/Xuất Khác** | Xuất sử dụng nội bộ, Xuất lắp ráp, Nhập thừa, Xuất thiếu. | |
| **INV-02** | **Chuyển Kho** | Chuyển hàng giữa các kho nội bộ (Có lệnh điều chuyển). | |
| **INV-03** | **Kiểm kê Kho** | Tạo phiếu kiểm kê -> Nhập số thực tế -> Tự động tạo phiếu Nhập/Xuất chênh lệch. | |
| **INV-04** | **Tính giá Xuất kho** | Tính giá vốn tự động theo phương pháp: **Bình quân gia quyền** (Tháng/Di động), **Nhập trước Xuất trước (FIFO)**, **Đích danh**. | |
| **INV-05** | **Quản lý Lô/Date/Serial** | Theo dõi hạn sử dụng (Expiry Date) và Số Serial (bảo hành) cho từng mặt hàng. | |
| **INV-06** | **Tự động cập nhật tồn kho** | Tồn kho thay đổi theo thời gian thực hoặc gần thời gian thực dựa trên các giao dịch nhập/xuất. | *Tính năng cơ bản, đảm bảo độ chính xác.* |
| **INV-07** | **Cảnh báo tồn kho** | Cảnh báo tồn kho dưới mức tối thiểu, tồn kho quá hạn, hàng sắp hết hạn sử dụng. | *Tính năng hỗ trợ quản lý.* |
| **INV-RPT** | **Báo cáo** | Thẻ kho, Sổ chi tiết vật tư, Báo cáo Tổng hợp Nhập-Xuất-Tồn, Báo cáo hàng tồn kho dưới định mức. | |

---

## 7. Phân hệ Tài sản Cố định & CCDC (Fixed Assets)

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ | Ghi chú (TT99 / Cạnh tranh) |
| :--- | :--- | :--- | :--- |
| **AST-01** | **Ghi tăng TSCĐ** | Khai báo: Nguyên giá, Ngày đưa vào sử dụng, Thời gian khấu hao, Bộ phận sử dụng, TK chi phí. | |
| **AST-02** | **Khấu hao/Phân bổ** | Tự động tính khấu hao (TK 214) và phân bổ CCDC (TK 242) hàng tháng. Hỗ trợ sửa đổi mức khấu hao. **TT99 có hướng dẫn cụ thể về khấu hao (Phụ lục III, IV), cần đảm bảo phương pháp tính và ghi nhận phù hợp. Không sử dụng TK 214 theo kiểu tích lũy riêng biệt nếu không tuân thủ quy định mới (xem tài liệu TT99).** | |
| **AST-03** | **Điều chỉnh/Thanh lý** | Ghi giảm tài sản (Thanh lý, nhượng bán, mất mát). Đánh giá lại tài sản (Nâng cấp, sửa chữa lớn). | |
| **AST-04** | **Đánh giá lại TSCĐ** | Thực hiện đánh giá lại giá trị TSCĐ theo yêu cầu (ví dụ: để góp vốn, bán, thế chấp). | *Theo TT99, việc đánh giá lại có thể ảnh hưởng đến BCTC.* |
| **AST-RPT** | **Báo cáo** | Sổ TSCĐ, Bảng tính khấu hao TSCĐ, Bảng phân bổ CCDC, Thẻ tài sản cố định. | |

---

## 8. Phân hệ Giá thành Sản xuất (Costing) - *Nâng cao*

Dành cho doanh nghiệp sản xuất, xây lắp.

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ | Ghi chú (TT99 / Cạnh tranh) |
| :--- | :--- | :--- | :--- |
| **CST-01** | **Định mức (BOM)** | Khai báo định mức nguyên vật liệu cho từng thành phẩm. | |
| **CST-02** | **Tập hợp Chi phí** | Tập hợp chi phí trực tiếp (NVL, Nhân công) và chi phí chung (Sản xuất chung) theo Đối tượng tập hợp chi phí (Sản phẩm, Lệnh sản xuất, Công trình). | |
| **CST-03** | **Phân bổ Chi phí** | Phân bổ chi phí chung (TK 627) theo tiêu thức: Nguyên vật liệu trực tiếp, Nhân công trực tiếp, hoặc Định mức. | |
| **CST-04** | **Đánh giá Dở dang** | Đánh giá sản phẩm dở dang cuối kỳ (WIP) theo NVL chính hoặc mức độ hoàn thành. | |
| **CST-05** | **Tính giá thành** | Tự động tính giá thành đơn vị sản phẩm nhập kho -> Cập nhật giá vốn kho thành phẩm. | |
| **CST-06** | **Phân tích giá thành** | So sánh giá thành thực tế với định mức, phân tích chênh lệch. | *Tính năng hỗ trợ quản trị chi phí.* |

---

## 9. Phân hệ Thuế (Tax)

Đảm bảo nghĩa vụ với nhà nước.

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ | Ghi chú (TT99 / Cạnh tranh) |
| :--- | :--- | :--- | :--- |
| **TAX-01** | **Tờ khai VAT** | Tự động lên tờ khai thuế GTGT khấu trừ (Mẫu 01/GTGT). | |
| **TAX-02** | **Kết xuất XML** | Xuất dữ liệu ra định dạng XML chuẩn để nộp vào phần mềm **HTKK** (Hỗ trợ kê khai) của Tổng cục Thuế. | |
| **TAX-03** | **Quyết toán Thuế** | **Hỗ trợ tính toán Thuế TNDN tạm tính quý, Quyết toán năm. PHẢI DỰA TRÊN SỐ LIỆU TỪ BÁO CÁO TÀI CHÍNH THEO TT99. TK 821 trong hệ thống tài khoản TT99 phản ánh chi phí thuế TNDN.** | *TT99: TK 821 - Chi phí thuế thu nhập doanh nghiệp.* |
| **TAX-04** | **Tích hợp với Cổng thông tin Thuế** | (Nâng cao) Gửi tờ khai điện tử trực tiếp từ phần mềm. | *Tính năng cạnh tranh, thuận tiện.* |

---

## 10. Yêu cầu Phi Chức năng (NFR)

| ID | Yêu cầu | Chi tiết | Ghi chú (TT99 / Cạnh tranh) |
| :--- | :--- | :--- | :--- |
| **NFR-UX01** | **Nhập liệu nhanh** | Hỗ trợ phím tắt (F2: Thêm, F3: Sửa, F8: Lưu, ESC: Thoát) để kế toán thao tác nhanh không cần chuột. | |
| **NFR-UX02** | **Tìm kiếm thông minh** | Tìm kiếm chứng từ theo mọi tiêu chí (Số phiếu, Ngày, Số tiền, Nội dung, Đối tượng). | |
| **NFR-P01** | **Xử lý dữ liệu lớn** | Hệ thống phải chịu tải được dữ liệu > 1 triệu chứng từ/năm mà không bị chậm khi truy xuất báo cáo. **Phải đảm bảo *truy xuất và hiển thị báo cáo tài chính (đặc biệt cuối năm) nhanh chóng*.** | *TT99: Yêu cầu thông tin phải kịp thời.* |
| **NFR-S01** | **Sao lưu tự động** | Cơ chế sao lưu định kỳ (Schedule Backup) để đảm bảo an toàn dữ liệu. **Phải đảm bảo *tính bảo mật dữ liệu*.** | *TT99: Yêu cầu hệ thống thông tin kế toán đảm bảo tính bảo mật.* |
| **NFR-S02** | **Bảo mật người dùng** | Xác thực mạnh (2FA nếu có), phân quyền chặt chẽ. | *TT99: Yêu cầu hệ thống thông tin kế toán đảm bảo tính bảo mật.* |
| **NFR-S03** | **An toàn hệ thống** | Hệ thống có khả năng phát hiện và ngăn chặn truy cập trái phép, thay đổi dữ liệu đã ghi sổ. | *TT99: Yêu cầu hệ thống thông tin kế toán đảm bảo tính bảo mật, toàn vẹn dữ liệu.* |
| **NFR-C01** | **Hỗ trợ nền tảng** | (Nếu áp dụng) Hỗ trợ Web, Mobile (iOS, Android). | *Tính năng cạnh tranh.* |
| **NFR-C02** | **Tích hợp hệ sinh thái** | (Nếu áp dụng) Dễ dàng tích hợp với các phần mềm khác (Hóa đơn điện tử, Chữ ký số, TMĐT, Kho, Nhân sự...). | *Tính năng cạnh tranh.* |

---

## 11. Chuyển đổi dữ liệu (Data Migration/Conversion)

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ | Ghi chú (TT99 / Cạnh tranh) |
| :--- | :--- | :--- | :--- |
| **MIG-01** | **Hướng dẫn & Công cụ chuyển đổi** | Cung cấp công cụ và hướng dẫn để chuyển dữ liệu từ hệ thống kế toán cũ (TT200/133) sang hệ thống mới theo TT99/2025. | *Bắt buộc khi áp dụng TT99 từ 01/01/2026. TT99 có hướng dẫn cụ thể về điều chỉnh số dư đầu kỳ.* |
| **MIG-02** | **Điều chỉnh số dư đầu kỳ** | Tự động hoặc bán tự động điều chỉnh số dư tài khoản theo hướng dẫn trong TT99/2025 (ví dụ: chuyển 441, 466 -> 4118; 338 -> 332...). | *Yêu cầu cụ thể trong TT99/2025.* |

---

## 12. UI/UX & Tiện ích Người dùng (UI/UX & User Utilities)

| ID | Nhóm | Tên Tiện ích / Yêu cầu UI/UX | Mô tả & Mối liên hệ với TT99 |
| :--- | :--- | :--- | :--- |
| **UX-01** | **Hiệu quả Thao tác** | **Phím tắt & Điều hướng nhanh** | Hỗ trợ phím tắt (F2: Thêm, F3: Sửa, F8: Lưu, ESC: Thoát, Ctrl+O: Mở chứng từ, Tab: chuyển trường) giúp người dùng thao tác nhanh, giảm thời gian, tăng hiệu suất. Phù hợp với NFR-UX01. |
| **UX-02** | **Hiệu quả Thao tác** | **Tìm kiếm Thông minh** | Cho phép tìm kiếm nhanh chứng từ, khách hàng, nhà cung cấp, tài khoản theo nhiều tiêu chí (số, tên, ngày, số tiền...). Phù hợp với NFR-UX02. |
| **UX-03** | **Hiệu quả Thao tác** | **Tự động hoàn tất (Auto-complete)** | Khi nhập tên khách hàng, nhà cung cấp, tài khoản, hệ thống gợi ý và tự động điền. Giảm sai sót và tăng tốc độ nhập liệu. |
| **UX-04** | **Hiệu quả Thao tác** | **Chèn dòng / Sao chép dòng nhanh trong bút toán** | Khi lập phiếu kế toán hoặc các chứng từ nhiều dòng (nhập/xuất kho), cho phép chèn nhanh hoặc sao chép dòng hiện tại giúp nhập liệu nhanh hơn. |
| **UX-05** | **Hiệu quả Thao tác** | **Nhập liệu theo lưới (Grid Input)** | Cho phép nhập nhiều dòng dữ liệu (ví dụ: chi tiết phiếu nhập mua, chi tiết bút toán kế toán) trong một lưới dữ liệu trực quan, dễ quản lý. |
| **UI-01** | **Giao diện** | **Giao diện trực quan, rõ ràng** | Màn hình được bố trí hợp lý, phân nhóm thông tin rõ ràng (Đầu phiếu, Chi tiết, Tổng cộng, Ký duyệt). Sử dụng biểu tượng, màu sắc hợp lý để phân biệt trạng thái (Đã duyệt, Chưa duyệt, Đã khóa sổ...). |
| **UI-02** | **Giao diện** | **Phản hồi thời gian thực** | Khi người dùng nhập liệu (ví dụ: chọn tài khoản, nhập số lượng/đơn giá), hệ thống tự động tính toán và cập nhật các trường liên quan (thành tiền, tổng cộng, tài khoản đối ứng mặc định) ngay lập tức. |
| **UI-03** | **Giao diện** | **Hiển thị cảnh báo / lỗi rõ ràng** | Khi người dùng nhập sai (ví dụ: bút toán không cân bằng, tài khoản không tồn tại), hệ thống hiển thị thông báo lỗi cụ thể, rõ ràng, gần vị trí sai, giúp sửa lỗi nhanh. |
| **UI-04** | **Giao diện** | **Tùy chỉnh giao diện (nếu cần)** | Cho phép người dùng lưu cấu hình cột hiển thị trên các danh sách (ví dụ: danh sách khách hàng, danh sách phiếu thu...), hoặc lưu các bộ lọc thường dùng. |
| **UTL-01** | **Tiện ích** | **Xem trước khi in (Print Preview)** | Cho phép xem trước báo cáo, chứng từ trước khi in, có thể chọn mẫu in, cỡ giấy, hướng giấy. |
| **UTL-02** | **Tiện ích** | **Xuất dữ liệu (Export)** | Cho phép xuất báo cáo, danh sách, chứng từ ra các định dạng phổ biến như Excel, PDF. Hữu ích cho lưu trữ, chia sẻ, phân tích bên ngoài. |
| **UTL-03** | **Tiện ích** | **Nhập dữ liệu từ Excel (Import)** | (Đặc biệt cho danh mục, số dư đầu kỳ, hoặc sao kê ngân hàng). Giảm thời gian nhập tay. |
| **UTL-04** | **Tiện ích** | **Lịch sử & Ưa thích** | Ghi nhớ các trang/màn hình người dùng truy cập gần đây hoặc cho phép đánh dấu các trang/màn hình ưa thích để truy cập nhanh. |
| **UTL-05** | **Tiện ích** | **Công cụ hỗ trợ kế toán (Calculator tích hợp)** | Một máy tính nhỏ tích hợp sẵn trong giao diện giúp người dùng tính toán nhanh khi nhập liệu mà không cần chuyển ứng dụng. |
| **UTL-06** | **Tiện ích** | **Gửi email trực tiếp từ hệ thống** | Cho phép đính kèm báo cáo hoặc chứng từ và gửi qua email ngay từ giao diện phần mềm (nếu được cấu hình SMTP). |
| **SEC-01** | **Bảo mật & Kiểm soát** | **Xác thực 2 lớp (2FA) (Nếu dùng Web/Mobile)** | Tăng cường bảo mật đăng nhập. |
| **SEC-02** | **Bảo mật & Kiểm soát** | **Nhật ký thao tác người dùng (User Action Log)** | Ghi lại các hành động cụ thể của người dùng (Ví dụ: "Người dùng A đã sửa phiếu chi số 001 vào lúc 10:30"). Bổ sung cho SYS-03 (Audit Log), phục vụ kiểm toán nội bộ và bên ngoài. |
| **SEC-03** | **Bảo mật & Kiểm soát** | **Cảnh báo & Ghi nhận thay đổi dữ liệu quan trọng** | Khi một người dùng có quyền sửa đổi dữ liệu quan trọng (ví dụ: bút toán đã duyệt, số dư đầu kỳ), hệ thống nên cảnh báo và ghi nhận rõ ràng hành động này, có thể yêu cầu xác nhận. |

---
```