# Thiết lập đường dẫn tuyệt đối theo yêu cầu
$sourcePath = "D:\tt99acct\source"
$rootPath = "D:\tt99acct"

# 1. Danh sách các thư mục cần tạo
$folders = @(
    "$sourcePath/core",
    "$sourcePath/database/models",
    "$sourcePath/services",
    "$sourcePath/master/data",
    "$sourcePath/security"
)

# Tạo thư mục gốc và các thư mục con
foreach ($folder in $folders) {
    if (!(Test-Path $folder)) {
        New-Item -Path $folder -ItemType Directory -Force
        Write-Host "Created folder: $folder" -ForegroundColor Gray
    }
}

# 2. Hàm tạo file .py rỗng (dumb file)
function Create-Dumb-File($path) {
    if (!(Test-Path $path)) {
        $content = "# PATH: $path"
        Set-Content -Path $path -Value $content -Encoding UTF8
        Write-Host "Created file: $path" -ForegroundColor Cyan
    }
}

# 3. Danh sách các file Python cần khởi tạo
$files = @(
    # File tại thư mục gốc dự án
    "$rootPath/main.py",
    
    # Core & Config
    "$sourcePath/__init__.py",
    "$sourcePath/core/__init__.py",
    "$sourcePath/core/db_config.py",
    "$sourcePath/core/logger_config.py",

    # Database & Models
    "$sourcePath/database/__init__.py",
    "$sourcePath/database/base.py",
    "$sourcePath/database/models/__init__.py",
    "$sourcePath/database/models/master_data.py",
    "$sourcePath/database/models/accounting.py",
    "$sourcePath/database/models/entities.py",
    "$sourcePath/database/models/dimensions.py",

    # Services (Tầng xử lý nghiệp vụ)
    "$sourcePath/services/__init__.py",
    "$sourcePath/services/sync_service.py",
    "$sourcePath/services/post_service.py",
    "$sourcePath/services/report_service.py",

    # Security
    "$sourcePath/security/__init__.py"
)

# Thực thi tạo file
foreach ($file in $files) {
    Create-Dumb-File $file
}

Write-Host "`n[SUCCESS] Da khoi tao xong khung file tai: $sourcePath" -ForegroundColor White -BackgroundColor DarkGreen