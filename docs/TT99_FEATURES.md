# **TT99 Accounting System: Danh mục Tính năng và Yêu cầu Hệ thống Toàn diện**

Tài liệu này mô tả chi tiết các tính năng (Features) và yêu cầu hệ thống (UR/NFR) nhằm đáp ứng nhu cầu quản trị doanh nghiệp thực tế và tuân thủ Thông tư 99/2025/TT-BTC.

## **1\. Phân hệ Quản trị Hệ thống & Danh mục (System & Master Data)**

Đây là nền tảng dữ liệu dùng chung cho toàn bộ hệ thống.

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ (User Requirement) |
| :---- | :---- | :---- |
| **SYS-01** | **Đa Chi nhánh/Đơn vị** | Hỗ trợ mô hình Tổng công ty \- Chi nhánh. Dữ liệu có thể hạch toán độc lập hoặc hợp nhất. |
| **SYS-02** | **Phân quyền Chi tiết** | Phân quyền đến từng chức năng (Thêm/Sửa/Xóa/Xem/In) và phạm vi dữ liệu (chỉ xem chứng từ của mình hoặc của cả phòng). |
| **SYS-03** | **Nhật ký Truy cập (Audit Log)** | Ghi lại lịch sử thay đổi dữ liệu: Ai làm? Lúc nào? Giá trị cũ/mới? (Bắt buộc cho kiểm toán). |
| **MST-01** | **Đối tượng Pháp nhân** | Quản lý Khách hàng/Nhà cung cấp: Tự động lấy thông tin từ Mã số thuế. Phân loại theo Nhóm, Khu vực. |
| **MST-02** | **Vật tư Hàng hóa** | Quản lý Mã hàng, Mã vạch, Đơn vị tính quy đổi (Thùng \-\> Hộp \-\> Cái), Thuế suất VAT ngầm định. |
| **MST-03** | **Danh mục Tài khoản** | Tuân thủ Phụ lục 1 TT99. Hỗ trợ Tài khoản theo dõi chi tiết theo: Đối tượng, Công trình, Hợp đồng, Khoản mục chi phí. |

## **2\. Phân hệ Kế toán Tổng hợp (General Ledger \- GL)**

Trái tim của hệ thống, nơi tập hợp số liệu để lên Báo cáo Tài chính.

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ |
| :---- | :---- | :---- |
| **GL-01** | **Phiếu Kế toán Khác** | Dùng cho các bút toán điều chỉnh, phân bổ lương, trích trước chi phí. |
| **GL-02** | **Phân bổ Chi phí Trả trước** | Tự động phân bổ chi phí (TK 242\) cho nhiều kỳ, nhiều đối tượng tập hợp chi phí. |
| **GL-03** | **Đánh giá Chênh lệch Tỷ giá** | Tự động đánh giá lại số dư các khoản mục tiền tệ có gốc ngoại tệ cuối kỳ theo tỷ giá thực tế/bình quân (TT99). |
| **GL-04** | **Kết chuyển Tự động** | Định nghĩa sẵn các cặp tài khoản kết chuyển (Doanh thu \-\> 911 \-\> Lợi nhuận) để chạy tự động cuối kỳ. |
| **GL-05** | **Khóa sổ/Mở sổ** | Chức năng "Khóa sổ" ngăn chặn sửa đổi dữ liệu trước ngày khóa. Cho phép "Mở sổ" có điều kiện (chỉ Admin). |
| **GL-RPT** | **Báo cáo Bắt buộc** | Sổ Nhật ký chung, Sổ Cái, Bảng Cân đối số phát sinh, Nhật ký \- Sổ Cái. |

## **3\. Phân hệ Tiền mặt & Tiền gửi (Cash & Bank)**

Quản lý chặt chẽ dòng tiền vào ra.

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ |
| :---- | :---- | :---- |
| **CSH-01** | **Phiếu Thu/Chi** | In phiếu trực tiếp từ phần mềm theo mẫu **01-TT, 02-TT**. Hỗ trợ in hàng loạt. |
| **CSH-02** | **Ủy nhiệm chi** | In Ủy nhiệm chi theo mẫu của các ngân hàng phổ biến tại Việt Nam (VCB, ACB, BIDV...). |
| **CSH-03** | **Đối chiếu Ngân hàng** | Nhập sao kê ngân hàng (Excel) và tự động đối chiếu với sổ kế toán để phát hiện chênh lệch. |
| **CSH-04** | **Theo dõi Tạm ứng** | Quản lý tạm ứng theo từng nhân viên, từng vụ việc. Kiểm soát thanh toán tạm ứng. |
| **CSH-RPT** | **Báo cáo** | Sổ Quỹ tiền mặt (Mẫu S07-DN), Sổ Tiền gửi ngân hàng (S08-DN), Báo cáo lưu chuyển tiền tệ (Dự báo). |

## **4\. Phân hệ Mua hàng & Công nợ Phải trả (Purchase & AP)**

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ |
| :---- | :---- | :---- |
| **PUR-01** | **Quy trình Mua hàng** | Đơn đặt hàng (PO) \-\> Phiếu nhập mua \-\> Hóa đơn mua hàng \-\> Thanh toán. |
| **PUR-02** | **Phân bổ Chi phí Mua** | Tự động phân bổ chi phí vận chuyển, bốc xếp, hải quan vào giá vốn hàng nhập (theo Giá trị hoặc Số lượng). |
| **PUR-03** | **Hàng về trước HĐ về sau** | Cho phép nhập kho ghi nhận nợ (TK 335), khi hóa đơn về thực hiện đối trừ. |
| **PUR-04** | **Quản lý Công nợ** | Theo dõi công nợ theo Hóa đơn, theo Hạn thanh toán. Cảnh báo nợ đến hạn. |
| **PUR-RPT** | **Báo cáo** | Bảng kê mua vào, Tổng hợp công nợ phải trả, Chi tiết công nợ theo hóa đơn, Phân tích tuổi nợ. |

## **5\. Phân hệ Bán hàng & Công nợ Phải thu (Sales & AR)**

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ |
| :---- | :---- | :---- |
| **SAL-01** | **Chính sách Giá** | Thiết lập bảng giá theo nhóm khách hàng, theo khoảng thời gian khuyến mãi. |
| **SAL-02** | **Chiết khấu** | Tự động tính chiết khấu thương mại, chiết khấu thanh toán trên hóa đơn. |
| **SAL-03** | **Hóa đơn Điện tử (E-Invoice)** | **(Critical)** Kết nối trực tiếp (API) với các nhà cung cấp (Viettel, VNPT, MISA, BKAV, SoftDreams) để phát hành, hủy, điều chỉnh hóa đơn. |
| **SAL-04** | **Hàng bán trả lại** | Xử lý nghiệp vụ khách trả lại hàng: Giảm trừ công nợ, Nhập lại kho. |
| **SAL-RPT** | **Báo cáo** | Bảng kê bán ra, Doanh số theo nhân viên/mặt hàng, Phân tích lãi gộp từng đơn hàng. |

## **6\. Phân hệ Kho (Inventory)**

Đây là phân hệ phức tạp nhất đối với doanh nghiệp thương mại/sản xuất.

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ |
| :---- | :---- | :---- |
| **INV-01** | **Nhập/Xuất Khác** | Xuất sử dụng nội bộ, Xuất lắp ráp, Nhập thừa, Xuất thiếu. |
| **INV-02** | **Chuyển Kho** | Chuyển hàng giữa các kho nội bộ (Có lệnh điều chuyển). |
| **INV-03** | **Kiểm kê Kho** | Tạo phiếu kiểm kê \-\> Nhập số thực tế \-\> Tự động tạo phiếu Nhập/Xuất chênh lệch. |
| **INV-04** | **Tính giá Xuất kho** | Tính giá vốn tự động theo phương pháp: **Bình quân gia quyền** (Tháng/Di động), **Nhập trước Xuất trước (FIFO)**, **Đích danh**. |
| **INV-05** | **Quản lý Lô/Date/Serial** | Theo dõi hạn sử dụng (Expiry Date) và Số Serial (bảo hành) cho từng mặt hàng. |
| **INV-RPT** | **Báo cáo** | Thẻ kho, Sổ chi tiết vật tư, Báo cáo Tổng hợp Nhập-Xuất-Tồn, Báo cáo hàng tồn kho dưới định mức. |

## **7\. Phân hệ Tài sản Cố định & CCDC (Fixed Assets)**

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ |
| :---- | :---- | :---- |
| **AST-01** | **Ghi tăng TSCĐ** | Khai báo: Nguyên giá, Ngày đưa vào sử dụng, Thời gian khấu hao, Bộ phận sử dụng, TK chi phí. |
| **AST-02** | **Khấu hao/Phân bổ** | Tự động tính khấu hao (TK 214\) và phân bổ CCDC (TK 242\) hàng tháng. Hỗ trợ sửa đổi mức khấu hao. |
| **AST-03** | **Điều chỉnh/Thanh lý** | Ghi giảm tài sản (Thanh lý, nhượng bán, mất mát). Đánh giá lại tài sản (Nâng cấp, sửa chữa lớn). |
| **AST-RPT** | **Báo cáo** | Sổ TSCĐ, Bảng tính khấu hao TSCĐ, Bảng phân bổ CCDC, Thẻ tài sản cố định. |

## **8\. Phân hệ Giá thành Sản xuất (Costing) \- *Nâng cao***

Dành cho doanh nghiệp sản xuất, xây lắp.

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ |
| :---- | :---- | :---- |
| **CST-01** | **Định mức (BOM)** | Khai báo định mức nguyên vật liệu cho từng thành phẩm. |
| **CST-02** | **Tập hợp Chi phí** | Tập hợp chi phí trực tiếp (NVL, Nhân công) và chi phí chung (Sản xuất chung) theo Đối tượng tập hợp chi phí (Sản phẩm, Lệnh sản xuất, Công trình). |
| **CST-03** | **Phân bổ Chi phí** | Phân bổ chi phí chung (TK 627\) theo tiêu thức: Nguyên vật liệu trực tiếp, Nhân công trực tiếp, hoặc Định mức. |
| **CST-04** | **Đánh giá Dở dang** | Đánh giá sản phẩm dở dang cuối kỳ (WIP) theo NVL chính hoặc mức độ hoàn thành. |
| **CST-05** | **Tính giá thành** | Tự động tính giá thành đơn vị sản phẩm nhập kho \-\> Cập nhật giá vốn kho thành phẩm. |

## **9\. Phân hệ Thuế (Tax)**

Đảm bảo nghĩa vụ với nhà nước.

| ID | Tính năng Chi tiết | Yêu cầu Nghiệp vụ |
| :---- | :---- | :---- |
| **TAX-01** | **Tờ khai VAT** | Tự động lên tờ khai thuế GTGT khấu trừ (Mẫu 01/GTGT). |
| **TAX-02** | **Kết xuất XML** | Xuất dữ liệu ra định dạng XML chuẩn để nộp vào phần mềm **HTKK** (Hỗ trợ kê khai) của Tổng cục Thuế. |
| **TAX-03** | **Quyết toán Thuế** | Hỗ trợ tính toán Thuế TNDN tạm tính quý, Quyết toán năm. |

## **10\. Yêu cầu Phi Chức năng (NFR)**

| ID | Yêu cầu | Chi tiết |
| :---- | :---- | :---- |
| **NFR-UX01** | **Nhập liệu nhanh** | Hỗ trợ phím tắt (F2: Thêm, F3: Sửa, F8: Lưu, ESC: Thoát) để kế toán thao tác nhanh không cần chuột. |
| **NFR-UX02** | **Tìm kiếm thông minh** | Tìm kiếm chứng từ theo mọi tiêu chí (Số phiếu, Ngày, Số tiền, Nội dung, Đối tượng). |
| **NFR-P01** | **Xử lý dữ liệu lớn** | Hệ thống phải chịu tải được dữ liệu \> 1 triệu chứng từ/năm mà không bị chậm khi truy xuất báo cáo. |
| **NFR-S01** | **Sao lưu tự động** | Cơ chế sao lưu định kỳ (Schedule Backup) để đảm bảo an toàn dữ liệu. |

