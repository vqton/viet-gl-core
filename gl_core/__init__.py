# gl_core/__init__.py
from .cli import main

# gl_core/__init__.py
import logging

# Cấu hình logging mặc định
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # In ra console
        # logging.FileHandler("gl.log"),  # Ghi vào file (nếu cần)
    ]
)

__version__ = "0.1.0"