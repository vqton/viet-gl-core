-- ===================================================================
-- COA SETUP SCRIPT - Phụ lục II TT99/2025/TT-BTC
-- File: coa_setup_v1.0_tt99_2025.sql
-- Version: 1.0
-- Ngày: 2025-12-09
-- Tác giả: DBA Team
-- Mô tả: Tạo ENUM, bảng accounts, insert COA chuẩn TT99/2025/TT-BTC
-- Yêu cầu: PostgreSQL 12+
-- ===================================================================

-- Bắt đầu transaction toàn cục
BEGIN;

-- ===================================================================
-- BƯỚC 1: DỌN SẠCH DỮ LIỆU CŨ (an toàn với CASCADE)
-- ===================================================================
DROP TABLE IF EXISTS "JournalEntryLines" CASCADE;
DROP TABLE IF EXISTS "JournalEntries" CASCADE;
DROP TABLE IF EXISTS "KyKeToan" CASCADE;
DROP TABLE IF EXISTS accounts CASCADE;
DROP TYPE IF EXISTS loaitaikhoan CASCADE;

-- ===================================================================
-- BƯỚC 2: TẠO ENUM LOẠI TÀI KHOẢN
-- ===================================================================
CREATE TYPE loaitaikhoan AS ENUM (
    'TAI_SAN',
    'NGUON_VON',
    'DOANH_THU',
    'CHI_PHI',
    'KHAC'
);

-- ===================================================================
-- BƯỚC 3: TẠO BẢNG accounts
-- ===================================================================
CREATE TABLE IF NOT EXISTS accounts (
    so_tai_khoan VARCHAR(20) PRIMARY KEY,
    ten_tai_khoan VARCHAR(256) NOT NULL,
    loai_tai_khoan loaitaikhoan NOT NULL,
    cap_tai_khoan INTEGER NOT NULL 
        DEFAULT 1 
        CHECK (cap_tai_khoan BETWEEN 1 AND 5),
    so_tai_khoan_cha VARCHAR(20),
    la_tai_khoan_tong_hop BOOLEAN NOT NULL DEFAULT TRUE,

    -- FK tự tham chiếu, deferrable để insert an toàn
    CONSTRAINT fk_parent 
        FOREIGN KEY (so_tai_khoan_cha) 
        REFERENCES accounts(so_tai_khoan)
        DEFERRABLE INITIALLY DEFERRED
);

-- ===================================================================
-- BƯỚC 4: CHÈN DỮ LIỆU COA – PHỤ LỤC II TT99/2025/TT-BTC
-- ===================================================================
INSERT INTO accounts (
    so_tai_khoan, 
    ten_tai_khoan, 
    loai_tai_khoan, 
    cap_tai_khoan, 
    so_tai_khoan_cha, 
    la_tai_khoan_tong_hop
) VALUES
-- ===================================================================
-- TÀI SẢN NGẮN HẠN (1xx)
-- ===================================================================
('111', 'Tiền mặt', 'TAI_SAN', 1, NULL, TRUE),
('1111', 'Tiền Việt Nam', 'TAI_SAN', 2, '111', FALSE),
('1112', 'Ngoại tệ', 'TAI_SAN', 2, '111', FALSE),
('112', 'Tiền gửi Ngân hàng', 'TAI_SAN', 1, NULL, TRUE),
('1121', 'Tiền Việt Nam', 'TAI_SAN', 2, '112', FALSE),
('1122', 'Ngoại tệ', 'TAI_SAN', 2, '112', FALSE),
('113', 'Vàng, bạc, kim khí quý, đá quý', 'TAI_SAN', 1, NULL, FALSE),
('121', 'Chứng khoán kinh doanh', 'TAI_SAN', 1, NULL, FALSE),
('128', 'Đầu tư tài chính ngắn hạn khác', 'TAI_SAN', 1, NULL, FALSE),
('131', 'Phải thu của khách hàng', 'TAI_SAN', 1, NULL, FALSE),
('132', 'Phải thu nội bộ ngắn hạn', 'TAI_SAN', 1, NULL, FALSE),
('133', 'Thuế GTGT được khấu trừ', 'TAI_SAN', 1, NULL, TRUE),
('1331', 'Thuế GTGT được khấu trừ của hàng hóa, dịch vụ', 'TAI_SAN', 2, '133', FALSE),
('1332', 'Thuế GTGT được khấu trừ của TSCĐ', 'TAI_SAN', 2, '133', FALSE),
('136', 'Phải thu nội bộ dài hạn', 'TAI_SAN', 1, NULL, FALSE),
('138', 'Phải thu khác', 'TAI_SAN', 1, NULL, TRUE),
('1381', 'Tài sản thiếu chờ xử lý', 'TAI_SAN', 2, '138', FALSE),
('1388', 'Phải thu khác', 'TAI_SAN', 2, '138', FALSE),
('141', 'Tạm ứng', 'TAI_SAN', 1, NULL, FALSE),
('142', 'Chi phí trả trước ngắn hạn', 'TAI_SAN', 1, NULL, FALSE),
('151', 'Hàng mua đang đi đường', 'TAI_SAN', 1, NULL, FALSE),
('152', 'Nguyên liệu, vật liệu', 'TAI_SAN', 1, NULL, FALSE),
('1521', 'Nguyên liệu, vật liệu chính', 'TAI_SAN', 2, '152', FALSE),
('1522', 'Vật liệu phụ', 'TAI_SAN', 2, '152', FALSE),
('1523', 'Nhiên liệu', 'TAI_SAN', 2, '152', FALSE),
('153', 'Công cụ, dụng cụ', 'TAI_SAN', 1, NULL, FALSE),
('154', 'Chi phí sản xuất, kinh doanh dở dang', 'TAI_SAN', 1, NULL, FALSE),
('155', 'Thành phẩm', 'TAI_SAN', 1, NULL, FALSE),
('156', 'Hàng hóa', 'TAI_SAN', 1, NULL, FALSE),
('157', 'Hàng gửi đi bán', 'TAI_SAN', 1, NULL, FALSE),
('158', 'Hàng hóa kho bảo thuế', 'TAI_SAN', 1, NULL, FALSE),

-- ===================================================================
-- TÀI SẢN DÀI HẠN (2xx)
-- ===================================================================
('211', 'Tài sản cố định hữu hình', 'TAI_SAN', 1, NULL, TRUE),
('2111', 'Nhà cửa, vật kiến trúc', 'TAI_SAN', 2, '211', FALSE),
('2112', 'Máy móc, thiết bị', 'TAI_SAN', 2, '211', FALSE),
('2113', 'Phương tiện vận tải, truyền dẫn', 'TAI_SAN', 2, '211', FALSE),
('2114', 'Thiết bị, dụng cụ quản lý', 'TAI_SAN', 2, '211', FALSE),
('2115', 'Cây lâu năm, súc vật làm việc và cho sản phẩm', 'TAI_SAN', 2, '211', FALSE),
('2118', 'TSCĐHH khác', 'TAI_SAN', 2, '211', FALSE),
('212', 'Tài sản cố định thuê tài chính', 'TAI_SAN', 1, NULL, FALSE),
('213', 'Tài sản cố định vô hình', 'TAI_SAN', 1, NULL, TRUE),
('2131', 'Quyền sử dụng đất', 'TAI_SAN', 2, '213', FALSE),
('2132', 'Bằng phát minh, sáng chế', 'TAI_SAN', 2, '213', FALSE),
('2133', 'Nhãn hiệu hàng hóa', 'TAI_SAN', 2, '213', FALSE),
('2134', 'Quyền tác giả', 'TAI_SAN', 2, '213', FALSE),
('2135', 'Phần mềm máy tính', 'TAI_SAN', 2, '213', FALSE),
('2136', 'Giấy phép, giấy nh phép khác', 'TAI_SAN', 2, '213', FALSE),
('2137', 'Chi phí nghiên cứu, phát triển', 'TAI_SAN', 2, '213', FALSE),
('2138', 'Lợi thế thương mại', 'TAI_SAN', 2, '213', FALSE),
('214', 'Hao mòn tài sản cố định', 'TAI_SAN', 1, NULL, TRUE),
('2141', 'Hao mòn TSCĐ hữu hình', 'TAI_SAN', 2, '214', FALSE),
('2142', 'Hao mòn TSCĐ thuê tài chính', 'TAI_SAN', 2, '214', FALSE),
('2143', 'Hao mòn TSCĐ vô hình', 'TAI_SAN', 2, '214', FALSE),
('221', 'Đầu tư vào công ty con', 'TAI_SAN', 1, NULL, FALSE),
('222', 'Đầu tư vào công ty liên kết, liên doanh', 'TAI_SAN', 1, NULL, FALSE),
('228', 'Đầu tư khác', 'TAI_SAN', 1, NULL, FALSE),
('229', 'Dự phòng tổn thất tài sản', 'TAI_SAN', 1, NULL, FALSE),
('241', 'Xây dựng cơ bản dở dang', 'TAI_SAN', 1, NULL, FALSE),
('242', 'Chi phí trả trước dài hạn', 'TAI_SAN', 1, NULL, FALSE),
('243', 'Chi phí chờ xử lý', 'TAI_SAN', 1, NULL, FALSE),
('244', 'Ký quỹ, ký cược dài hạn', 'TAI_SAN', 1, NULL, FALSE),

-- ===================================================================
-- NỢ PHẢI TRẢ + VỐN CSH (3xx, 4xx) → NGUON_VON
-- ===================================================================
('311', 'Vay ngắn hạn', 'NGUON_VON', 1, NULL, FALSE),
('315', 'Nợ dài hạn đến hạn trả', 'NGUON_VON', 1, NULL, FALSE),
('331', 'Phải trả cho người bán', 'NGUON_VON', 1, NULL, FALSE),
('333', 'Thuế và các khoản phải nộp Nhà nước', 'NGUON_VON', 1, NULL, TRUE),
('3331', 'Thuế giá trị gia tăng phải nộp', 'NGUON_VON', 2, '333', TRUE),
('33311', 'Thuế GTGT đầu ra', 'NGUON_VON', 3, '3331', FALSE),
('33312', 'Thuế GTGT hàng nhập khẩu', 'NGUON_VON', 3, '3331', FALSE),
('3332', 'Thuế tiêu thụ đặc biệt', 'NGUON_VON', 2, '333', FALSE),
('3333', 'Thuế thu nhập cá nhân', 'NGUON_VON', 2, '333', FALSE),
('3334', 'Thuế thu nhập doanh nghiệp', 'NGUON_VON', 2, '333', FALSE),
('3335', 'Thuế tài nguyên', 'NGUON_VON', 2, '333', FALSE),
('3337', 'Thuế nhà đất, tiền thuê đất', 'NGUON_VON', 2, '333', FALSE),
('3338', 'Các loại thuế khác', 'NGUON_VON', 2, '333', FALSE),
('334', 'Phải trả người lao động', 'NGUON_VON', 1, NULL, TRUE),
('3341', 'Lương, phụ cấp', 'NGUON_VON', 2, '334', FALSE),
('3342', 'Trợ cấp, trợ giúp', 'NGUON_VON', 2, '334', FALSE),
('335', 'Chi phí phải trả', 'NGUON_VON', 1, NULL, FALSE),
('338', 'Phải trả, phải nộp khác', 'NGUON_VON', 1, NULL, TRUE),
('3382', 'Kinh phí công đoàn', 'NGUON_VON', 2, '338', FALSE),
('3383', 'Bảo hiểm xã hội', 'NGUON_VON', 2, '338', FALSE),
('3384', 'Bảo hiểm y tế', 'NGUON_VON', 2, '338', FALSE),
('3386', 'Nhập khẩu ủy thác', 'NGUON_VON', 2, '338', FALSE),
('3387', 'Doanh thu chưa thực hiện', 'NGUON_VON', 2, '338', FALSE),
('3388', 'Phải trả, phải nộp khác', 'NGUON_VON', 2, '338', FALSE),
('341', 'Vay và nợ thuê tài chính', 'NGUON_VON', 1, NULL, FALSE),
('342', 'Nợ dài hạn', 'NGUON_VON', 1, NULL, FALSE),
('343', 'Trái phiếu phát hành', 'NGUON_VON', 1, NULL, FALSE),
('352', 'Dự phòng phải trả', 'NGUON_VON', 1, NULL, FALSE),
('353', 'Quỹ khen thưởng, phúc lợi', 'NGUON_VON', 1, NULL, FALSE),
('356', 'Nhận ký quỹ, ký cược dài hạn', 'NGUON_VON', 1, NULL, FALSE),

('411', 'Vốn đầu tư của chủ sở hữu', 'NGUON_VON', 1, NULL, TRUE),
('4111', 'Vốn góp của chủ sở hữu', 'NGUON_VON', 2, '411', FALSE),
('4112', 'Thặng dư vốn cổ phần', 'NGUON_VON', 2, '411', FALSE),
('412', 'Chênh lệch đánh giá lại tài sản', 'NGUON_VON', 1, NULL, FALSE),
('413', 'Chênh lệch tỷ giá hối đoái', 'NGUON_VON', 1, NULL, FALSE),
('414', 'Quỹ đầu tư phát triển', 'NGUON_VON', 1, NULL, FALSE),
('418', 'Các quỹ khác thuộc vốn chủ sở hữu', 'NGUON_VON', 1, NULL, FALSE),
('421', 'Lợi nhuận sau thuế chưa phân phối', 'NGUON_VON', 1, NULL, TRUE),
('4211', 'LNST chưa phân phối năm trước', 'NGUON_VON', 2, '421', FALSE),
('4212', 'LNST chưa phân phối năm nay', 'NGUON_VON', 2, '421', FALSE),

-- ===================================================================
-- DOANH THU (5xx, 7xx)
-- ===================================================================
('511', 'Doanh thu bán hàng và cung cấp dịch vụ', 'DOANH_THU', 1, NULL, TRUE),
('5111', 'Doanh thu bán hàng hóa', 'DOANH_THU', 2, '511', FALSE),
('5112', 'Doanh thu bán thành phẩm', 'DOANH_THU', 2, '511', FALSE),
('5113', 'Doanh thu cung cấp dịch vụ', 'DOANH_THU', 2, '511', FALSE),
('512', 'Doanh thu nội bộ', 'DOANH_THU', 1, NULL, FALSE),
('515', 'Doanh thu hoạt động tài chính', 'DOANH_THU', 1, NULL, FALSE),
('521', 'Các khoản giảm trừ doanh thu', 'DOANH_THU', 1, NULL, TRUE),
('5211', 'Chiết khấu thương mại', 'DOANH_THU', 2, '521', FALSE),
('5212', 'Hàng bán bị trả lại', 'DOANH_THU', 2, '521', FALSE),
('5213', 'Giảm giá hàng bán', 'DOANH_THU', 2, '521', FALSE),
('711', 'Thu nhập khác', 'DOANH_THU', 1, NULL, FALSE),

-- ===================================================================
-- CHI PHÍ (6xx, 8xx)
-- ===================================================================
('611', 'Mua hàng', 'CHI_PHI', 1, NULL, TRUE),
('6111', 'Mua nguyên liệu, vật liệu', 'CHI_PHI', 2, '611', FALSE),
('6112', 'Mua hàng hóa', 'CHI_PHI', 2, '611', FALSE),
('621', 'Chi phí nguyên liệu, vật liệu trực tiếp', 'CHI_PHI', 1, NULL, FALSE),
('622', 'Chi phí nhân công trực tiếp', 'CHI_PHI', 1, NULL, FALSE),
('623', 'Chi phí sử dụng máy thi công', 'CHI_PHI', 1, NULL, FALSE),
('627', 'Chi phí sản xuất chung', 'CHI_PHI', 1, NULL, FALSE),
('632', 'Giá vốn hàng bán', 'CHI_PHI', 1, NULL, FALSE),
('635', 'Chi phí tài chính', 'CHI_PHI', 1, NULL, FALSE),
('641', 'Chi phí bán hàng', 'CHI_PHI', 1, NULL, TRUE),
('6411', 'Chi phí nhân viên', 'CHI_PHI', 2, '641', FALSE),
('6412', 'Chi phí vật liệu, bao bì', 'CHI_PHI', 2, '641', FALSE),
('6413', 'Chi phí CCDC', 'CHI_PHI', 2, '641', FALSE),
('6414', 'Chi phí khấu hao TSCĐ', 'CHI_PHI', 2, '641', FALSE),
('6415', 'Chi phí bảo hành', 'CHI_PHI', 2, '641', FALSE),
('6417', 'Chi phí dịch vụ mua ngoài', 'CHI_PHI', 2, '641', FALSE),
('6418', 'Chi phí bằng tiền khác', 'CHI_PHI', 2, '641', FALSE),
('642', 'Chi phí quản lý doanh nghiệp', 'CHI_PHI', 1, NULL, TRUE),
('6421', 'Chi phí nhân viên quản lý', 'CHI_PHI', 2, '642', FALSE),
('6422', 'Chi phí vật liệu quản lý', 'CHI_PHI', 2, '642', FALSE),
('6423', 'Chi phí CCDC', 'CHI_PHI', 2, '642', FALSE),
('6424', 'Chi phí khấu hao TSCĐ', 'CHI_PHI', 2, '642', FALSE),
('6425', 'Thuế, phí, lệ phí', 'CHI_PHI', 2, '642', FALSE),
('6426', 'Chi phí dự phòng', 'CHI_PHI', 2, '642', FALSE),
('6427', 'Chi phí dịch vụ mua ngoài', 'CHI_PHI', 2, '642', FALSE),
('6428', 'Chi phí bằng tiền khác', 'CHI_PHI', 2, '642', FALSE),
('811', 'Chi phí khác', 'CHI_PHI', 1, NULL, FALSE),
('821', 'Chi phí thuế thu nhập doanh nghiệp', 'CHI_PHI', 1, NULL, FALSE),

-- ===================================================================
-- TÀI KHOẢN KHÁC (0xx, 9xx)
-- ===================================================================
('001', 'Tài sản thuê ngoài', 'KHAC', 1, NULL, FALSE),
('002', 'Vật tư, tài sản nhận giữ hộ, nhận gia công', 'KHAC', 1, NULL, FALSE),
('003', 'Hàng hóa nhận bán đại lý, ký gửi', 'KHAC', 1, NULL, FALSE),
('004', 'Nợ khó đòi đã xử lý', 'KHAC', 1, NULL, FALSE),
('007', 'Ngoại tệ các loại', 'KHAC', 1, NULL, FALSE),
('911', 'Xác định kết quả kinh doanh', 'KHAC', 1, NULL, FALSE)

ON CONFLICT (so_tai_khoan) DO NOTHING;

-- ===================================================================
-- BƯỚC 5: LOG KẾT QUẢ
-- ===================================================================
DO $$
DECLARE
    total INTEGER;
BEGIN
    SELECT COUNT(*) INTO total FROM accounts;
    RAISE NOTICE 'COA đã được khởi tạo thành công: % tài khoản được đồng bộ.', total;
END $$;

-- Kết thúc transaction
COMMIT;

-- ===================================================================
-- HƯỚNG DẪN KIỂM TRA SAU KHI CHẠY
-- ===================================================================
/*
SELECT COUNT(*) FROM accounts;
SELECT so_tai_khoan, ten_tai_khoan, cap_tai_khoan, so_tai_khoan_cha 
FROM accounts 
WHERE so_tai_khoan LIKE '333%' 
ORDER BY so_tai_khoan;
*/