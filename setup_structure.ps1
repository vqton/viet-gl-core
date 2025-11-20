# Bắt đầu từ thư mục tt99acct (giả sử script được chạy từ thư mục cha tt99acct)

Write-Host "Starting setup of DDD folder structure in tt99acct..." -ForegroundColor Green

# Tạo thư mục app và các file bên trong
Write-Host "Creating app directory and files..."
New-Item -ItemType Directory -Path "app" -Force
Set-Location -Path "app"
New-Item -ItemType File -Path "__init__.py" -Force
New-Item -ItemType File -Path "main.py" -Force
New-Item -ItemType File -Path "config.py" -Force

# Tạo thư mục domain và cấu trúc con
Write-Host "Creating domain directory and substructure..."
New-Item -ItemType Directory -Path "domain" -Force
Set-Location -Path "domain"
New-Item -ItemType File -Path "__init__.py" -Force
New-Item -ItemType Directory -Path "models" -Force
Set-Location -Path "models"
New-Item -ItemType File -Path "__init__.py" -Force
# (File account.py sẽ được tạo trong Step 1)
Set-Location -Path ".." # Quay lại app/domain
Set-Location -Path ".." # Quay lại app

# Tạo thư mục application và cấu trúc con
Write-Host "Creating application directory and substructure..."
New-Item -ItemType Directory -Path "application" -Force
Set-Location -Path "application"
New-Item -ItemType File -Path "__init__.py" -Force
New-Item -ItemType Directory -Path "services" -Force
Set-Location -Path "services"
New-Item -ItemType File -Path "__init__.py" -Force
New-Item -ItemType File -Path "journaling_service.py" -Force # (File này sẽ được tạo trong Step 2, nhưng tạo thư mục cấu trúc trước)
Set-Location -Path ".." # Quay lại app/application
Set-Location -Path ".." # Quay lại app

# Tạo thư mục infrastructure và cấu trúc con
Write-Host "Creating infrastructure directory and substructure..."
New-Item -ItemType Directory -Path "infrastructure" -Force
Set-Location -Path "infrastructure"
New-Item -ItemType File -Path "__init__.py" -Force
New-Item -ItemType File -Path "database.py" -Force
New-Item -ItemType Directory -Path "models" -Force
Set-Location -Path "models"
New-Item -ItemType File -Path "__init__.py" -Force
New-Item -ItemType File -Path "sql_account.py" -Force # (File này sẽ được tạo trong Step 1, nhưng tạo thư mục cấu trúc trước)
Set-Location -Path ".." # Quay lại app/infrastructure
Set-Location -Path ".." # Quay lại app

# Tạo thư mục presentation và cấu trúc con
Write-Host "Creating presentation directory and substructure..."
New-Item -ItemType Directory -Path "presentation" -Force
Set-Location -Path "presentation"
New-Item -ItemType File -Path "__init__.py" -Force
New-Item -ItemType Directory -Path "api" -Force
Set-Location -Path "api"
New-Item -ItemType File -Path "__init__.py" -Force
New-Item -ItemType Directory -Path "v1" -Force
Set-Location -Path "v1"
New-Item -ItemType File -Path "__init__.py" -Force
New-Item -ItemType File -Path "accounting.py" -Force # (File này sẽ được tạo trong Step 3, nhưng tạo thư mục cấu trúc trước)
# Có thể tạo journaling.py, reports.py sau
Set-Location -Path "../../../.." # Quay lại tt99acct gốc

# Tạo thư mục tests và file bên trong
Write-Host "Creating tests directory and files..."
New-Item -ItemType Directory -Path "tests" -Force
Set-Location -Path "tests"
New-Item -ItemType File -Path "__init__.py" -Force
New-Item -ItemType File -Path "test_account.py" -Force # (File này sẽ được tạo trong Step 1)
Set-Location -Path ".." # Quay lại tt99acct gốc

Write-Host "DDD folder structure setup completed in tt99acct using PowerShell script." -ForegroundColor Green
Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")