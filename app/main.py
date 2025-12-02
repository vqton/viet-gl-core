from fastapi import FastAPI

from app.presentation.api.v1.accounting import router as accounting_router

# Khởi tạo ứng dụng FastAPI với metadata tuân thủ TT99
app = FastAPI(
    title="Hệ thống kế toán tuân thủ TT99/2025/TT-BTC",
    description="""
    API phục vụ nghiệp vụ kế toán doanh nghiệp theo **Thông tư 99/2025/TT-BTC** của Bộ Tài chính.
    
    Bao gồm các chức năng:
    - Quản lý tài khoản kế toán (theo Phụ lục II)
    - Ghi nhận bút toán (chứng từ kế toán theo Phụ lục I)
    - Lập báo cáo tài chính (theo Phụ lục IV: B01-DN, B02-DN, B03-DN, B09-DN)
    - Khóa sổ cuối kỳ
    """,
    version="0.1.0",
    contact={"name": "Bộ phận Kế toán", "email": "accounting@example.com"},
    license_info={"name": "MIT License"},
)

# Đăng ký router kế toán với tiền tố /accounting
# ✅ Đảm bảo các endpoint như /accounting/accounts/ hoạt động đúng
app.include_router(accounting_router)


@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint mặc định để kiểm tra trạng thái hoạt động của API.
    """
    return {
        "message": "Chào mừng đến với hệ thống kế toán tuân thủ TT99/2025/TT-BTC!",
        "docs": "/docs",
        "redoc": "/redoc",
    }
