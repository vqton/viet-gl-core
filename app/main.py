from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

# Import cơ sở hạ tầng
from app.infrastructure.database import create_tables
from app.presentation.api.v1.reporting import router as reporting_router # Dùng router Báo cáo

app = FastAPI(title="Hệ thống Kế toán TT99", version="1.0.0")

# --- Đăng ký Router ---
# Đăng ký router báo cáo
app.include_router(reporting_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    """
    Hàm này được chạy khi ứng dụng khởi động.
    Sử dụng để tạo các bảng DB nếu chúng chưa tồn tại.
    """
    try:
        print("Đang cố gắng tạo các bảng cơ sở dữ liệu...")
        # Đảm bảo tất cả các model đã được import trong database.py trước khi gọi create_tables()
        create_tables()
        print("Khởi động thành công và các bảng đã được tạo (hoặc đã tồn tại).")
    except OperationalError as e:
        # Điều này có thể xảy ra nếu engine không thể kết nối ngay lập tức
        print(f"Cảnh báo: Không thể kết nối hoặc tạo bảng khi khởi động. Lỗi: {e}")
        print("Vui lòng kiểm tra lại DATABASE_URL trong app/config.py")


@app.get("/")
def read_root():
    return {"message": "Chào mừng đến với Hệ thống Kế toán TT99"}