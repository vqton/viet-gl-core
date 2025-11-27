from fastapi import FastAPI
from app.presentation.api.v1.accounting import router as accounting_router # Import router mới

app = FastAPI(title="Hệ thống kế toán TT99", version="0.1.0")

# Include the new router
# [Nghiệp vụ] Tích hợp tất cả các API endpoint liên quan đến kế toán vào ứng dụng chính.
app.include_router(accounting_router)

@app.get("/")
def read_root():
    """
    Endpoint mặc định để kiểm tra trạng thái hoạt động của API.
    """
    return {"message": "Chào mừng đến với hệ thống kế toán tuân thủ TT99/2025/TT-BTC!"}

# (Có thể thêm các routers khác ở đây sau)