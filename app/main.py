from fastapi import FastAPI

from app.presentation.api.v1.accounting import router as accounting_router

app = FastAPI(title="Hệ thống kế toán TT99", version="1.0.0")

app.include_router(accounting_router)
