"""
PATH: source/schemas/master_schemas.py
STATUS: Production-ready
DESCRIPTION: Định nghĩa màng lọc dữ liệu cho tất cả Master Data.
"""
from pydantic import BaseModel, Field
from typing import Optional

class EntityJSONSchema(BaseModel):
    id: str = Field(..., min_length=1, description="Mã đối tượng (KH001, NCC002)")
    name: str = Field(..., min_length=2)
    tax_code: Optional[str] = None
    address: Optional[str] = None
    entity_type: str = Field(..., description="VÍ dụ: CUSTOMER, VENDOR, EMPLOYEE")

class BudgetSourceJSONSchema(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=2)