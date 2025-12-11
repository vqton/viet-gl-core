# main.py (đã bổ sung comments giải thích then chốt)

import logging
import os

from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError(
        "Biến môi trường DATABASE_URL chưa được thiết lập trong file .env"
    )

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Cơ sở hạ tầng & báo cáo
from app.infrastructure.database import create_tables
from app.presentation.api.v1.accounting.reports import (
    router as reporting_router,
)

# Cấu hình ứng dụng FastAPI — tuân thủ TT99/2025/TT-BTC
app = FastAPI(
    title="Hệ thống Kế toán TT99",
    version="1.0.0",
    description="API tuân thủ Thông tư 99/2025/TT-BTC của Bộ Tài chính",
    contact={
        "name": "Đội phát triển hệ thống kế toán",
        "email": "support@tt99-accounting.vn",
    },
    license_info={"name": "MIT"},
)

# CORS: Cho phép frontend gọi API (nếu có)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký router báo cáo — nơi triển khai B01, B02, B03, B09 theo Phụ lục IV TT99
app.include_router(reporting_router, prefix="/api/v1")


# ---
# XỬ LÝ NGOẠI LỆ TOÀN CỤC
# [TT99 Điều 3] Yêu cầu kiểm soát nội bộ nghiêm ngặt → Không để lộ thông tin hệ thống ra client
# ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    logging.warning(
        f"Dữ liệu đầu vào không hợp lệ từ {request.url}: {exc.errors()}"
    )
    return JSONResponse(
        status_code=400,
        content={
            "detail": "Dữ liệu đầu vào không hợp lệ",
            "errors": exc.errors(),
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
):
    logging.warning(
        f"Lỗi HTTP {exc.status_code} tại {request.url}: {exc.detail}"
    )
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Ghi log lỗi hệ thống — phục vụ audit nội bộ (TT99 Điều 3)
    logging.error(
        f"Lỗi hệ thống không mong muốn tại {request.url}: {exc}", exc_info=True
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Lỗi hệ thống. Vui lòng liên hệ quản trị viên."},
    )


# ---
# KHỞI TẠO ỨNG DỤNG
# [TT99 Điều 13] Yêu cầu mở sổ kế toán đầu kỳ → Tạo bảng DB nếu chưa tồn tại
# ---
@app.on_event("startup")
def on_startup():
    """
    Khởi tạo cơ sở dữ liệu khi ứng dụng chạy.
    - Tạo các bảng nếu chưa tồn tại (mô phỏng 'mở sổ kế toán' đầu kỳ theo TT99 Điều 13).
    - Dừng ứng dụng nếu không thể kết nối DB — đảm bảo tính toàn vẹn dữ liệu báo cáo.
    """
    try:
        logging.info("Đang khởi tạo cơ sở dữ liệu (mở sổ kế toán đầu kỳ)...")
        create_tables()
        logging.info("Khởi tạo thành công.")
    except OperationalError as e:
        logging.error(f"Không thể kết nối cơ sở dữ liệu: {e}")
        raise RuntimeError(
            "Lỗi khởi tạo cơ sở dữ liệu. Vui lòng kiểm tra DATABASE_URL."
        )


# ---
# HEALTH CHECK
# Dùng để giám sát hệ thống báo cáo tài chính — đảm bảo sẵn sàng khi đến kỳ khóa sổ.
# ---
@app.get("/health", summary="Kiểm tra trạng thái hệ thống")
def health_check():
    return {"status": "OK", "service": "Hệ thống Kế toán TT99"}


@app.get("/", include_in_schema=False)
def read_root():
    return {"message": "Chào mừng đến với Hệ thống Kế toán TT99"}
