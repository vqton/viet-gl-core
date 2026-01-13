# 1. Định danh thư mục gốc
$root = "d:/TT99ACCT"

# 2. Danh sách thư mục theo định danh chuẩn hóa quốc tế
$dirs = @(
    "$root/data",
    "$root/config",
    "$root/source/security",      # Bảo mật: Phân quyền, Nhật ký lưu vết
    "$root/source/core",          # Lõi: Engine hạch toán, Kiểm tra khóa sổ
    "$root/source/master",        # Danh mục: Hệ thống tài khoản, Đối tượng, Thuế, Bộ phận
    "$root/source/services",      # Phân hệ: TSCĐ, Hàng tồn kho, Ngoại tệ
    "$root/source/reports",       # Báo cáo: B01-DN, B02-DN, Sổ cái
    "$root/source/api",           # Kết nối: Hóa đơn điện tử, Ngân hàng
    "$root/logs"                  # Nhật ký hệ thống & Audit
)

Write-Host "--- Dang khoi tao he thong TT99ACCT (Master Standardized) ---" -ForegroundColor Cyan

foreach ($dir in $dirs) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "[OK] Da tao thu muc: $dir"
    }
}

# 3. Khởi tạo __init__.py để Python nhận diện các package
Get-ChildItem -Path "$root/source" -Recurse -Directory | ForEach-Object {
    $initFile = Join-Path $_.FullName "__init__.py"
    if (!(Test-Path $initFile)) { New-Item -ItemType File -Path $initFile | Out-Null }
}

# 4. KHOI TAO DU LIEU DANH MUC (Master Data - TT99 Standard)

# File: master/accounts.py
$dmTK = @"
# Danh muc Tai khoan theo Phu luc II Thong tu 99/2025/TT-BTC
CHART_OF_ACCOUNTS = [
    {'code': '111', 'name': 'Tien mat', 'nature': 'Debit'},
    {'code': '112', 'name': 'Tien gui Ngan hang', 'nature': 'Debit'},
    {'code': '131', 'name': 'Phai thu khach hang', 'nature': 'Both'},
    {'code': '211', 'name': 'Tai san co dinh huu hinh', 'nature': 'Debit'},
    {'code': '331', 'name': 'Phai tra nguoi ban', 'nature': 'Both'},
    {'code': '411', 'name': 'Von gop chu so huu', 'nature': 'Credit'},
    {'code': '511', 'name': 'Doanh thu ban hang', 'nature': 'Credit'},
    {'code': '642', 'name': 'Chi phi quan ly doanh nghiep', 'nature': 'Debit'}
]
"@
New-Item -ItemType File -Path "$root/source/master/accounts.py" -Value $dmTK -Force | Out-Null

# File: master/general_data.py (Tax, Departments, Voucher Types)
$dmGeneral = @"
VOUCHER_TYPES = [
    {'code': 'PT', 'name': 'Phieu Thu', 'template': '01-TT'},
    {'code': 'PC', 'name': 'Phieu Chi', 'template': '02-TT'},
    {'code': 'PKT', 'name': 'Phieu Ke Toan', 'template': '01-KT'}
]
TAX_CATEGORIES = [{'code': 'VAT10', 'rate': 0.1}, {'code': 'VAT05', 'rate': 0.05}]
COST_CENTERS = [{'code': 'BH', 'name': 'Bo phan Ban hang'}, {'code': 'QL', 'name': 'Bo phan Quan ly'}]
"@
New-Item -ItemType File -Path "$root/source/master/general_data.py" -Value $dmGeneral -Force | Out-Null

# 5. KHOI TAO LOGIC LOI (Core Accounting Engine)

$logicCore = @"
# Nhân xử lý định khoản kép & Kiểm soát dữ liệu
def validate_accounting_equation(entries):
    total_debit = sum(e['amount'] for e in entries if e['side'] == 'DEBIT')
    total_credit = sum(e['amount'] for e in entries if e['side'] == 'CREDIT')
    return total_debit == total_credit

def post_entry(db, voucher, entries):
    # Kiem tra can doi truoc khi ghi vao so cai
    if not validate_accounting_equation(entries):
        raise ValueError("Loi: But toan khong can doi!")
    # Thuc hien ghi du lieu kem theo Audit Trail
"@
New-Item -ItemType File -Path "$root/source/core/engine.py" -Value $logicCore -Force | Out-Null

# 6. File cau hinh Mapping BCTC
$mappingBCTC = @"
# Cau hinh Mapping so du tai khoan vao chi tieu BCTC (Phu luc IV)
MAPPING_B01_DN = {
    '110': ['111', '112'], # Tien va cac khoan tuong duong tien
    '150': ['152', '156'], # Hang ton kho
    '411': ['411']         # Von chu so huu
}
"@
New-Item -ItemType File -Path "$root/config/mapping_bctc.py" -Value $mappingBCTC -Force | Out-Null

Write-Host "--- SETUP HOAN TAT: TT99ACCT da san sang voi cau truc chuan hoa quoc te! ---" -ForegroundColor Green