# File: app/main.py

from fastapi import FastAPI
from app.presentation.api.v1.accounting import router as accounting_router # Import router mới

app = FastAPI(title="Hệ thống kế toán TT99", version="0.1.0")

# Include the new router
app.include_router(accounting_router)

@app.get("/")
def read_root():
    return {"message": "Chào mừng đến với hệ thống kế toán tuân thủ TT99/2025/TT-BTC!"}

# (Có thể thêm các routers khác ở đây sau)