# STANDARDS.md – Tiêu chuẩn phát triển hệ thống kế toán (Python Version)

> **Phiên bản**: 1.0
> **Ngôn ngữ áp dụng**: Python (PEP8 + DDD + Clean Architecture)
> **Mục tiêu**: Chuẩn hóa quy tắc phát triển cho toàn bộ hệ thống kế toán/ERP nhằm đảm bảo nhất quán, dễ bảo trì, dễ mở rộng.

---

# 1. Mục tiêu tài liệu

Tài liệu này quy định toàn bộ tiêu chuẩn phát triển cho hệ thống kế toán, bao gồm:

* Kiến trúc phần mềm chuẩn DDD + Clean Architecture + SOLID
* Quy tắc đặt tên trong Domain, Application, Infrastructure
* Quy tắc thiết kế Domain kế toán
* Quy tắc viết code Python (PEP8 – snake_case – type hints – dataclass)
* Giải thích nghiệp vụ kế toán bằng comment trong domain model
* Quy tắc viết API, Repository, Service
* Quy tắc kiểm thử và logging

---

# 2. Nguyên tắc nền tảng

## 2.1 Clean Architecture

```
Domain → Application → Infrastructure → Presentation (API)
```

* **Domain**: Chỉ chứa logic nghiệp vụ kế toán thuần, không phụ thuộc framework.
* **Application**: Chứa use-case, service, validator.
* **Infrastructure**: Chứa repository, ORM (SQLAlchemy), kết nối DB, file, external services.
* **Presentation**: API (FastAPI / Flask), DTO/schema.

## 2.2 SOLID

* **S**ingle Responsibility: Mỗi lớp đảm nhiệm đúng 1 nghiệp vụ kế toán.
* **O**pen/Closed: Có thể thêm chuẩn mực kế toán mới mà không sửa lõi domain.
* **L**iskov Substitution: Tất cả repository phải tuân thủ interface chuẩn.
* **I**nterface Segregation: Repository tách theo nghiệp vụ (JournalRepository, AccountRepository...).
* **D**ependency Inversion: Use-case phụ thuộc interface, không phụ thuộc ORM.

---

# 3. Quy ước đặt tên

## 3.1 Trong Domain và Application (bắt buộc không dấu)

* Dùng **snake_case** cho tên biến và hàm.
* Dùng **PascalCase** cho tên class.
* Dùng tiếng Việt **không dấu** để giữ “ubiquitous language”.

**Ví dụ đúng:**

```python
class ButToanLine:
    so_tai_khoan: str
    so_tien: Decimal
    loai_giao_dich: LoaiGiaoDich
```

**Ví dụ sai:**

```python
class JournalEntryLine:   # tiếng Anh – ❌
    account: str
```

## 3.2 Infrastructure và API

Có thể dùng tiếng Anh tùy theo chuẩn framework.

---

# 4. Domain kế toán (Python, có comment giải thích)

Domain phải dùng **dataclass(frozen=True)** cho Value Object và Entity bất biến.

```python
from dataclasses import dataclass
from decimal import Decimal
from datetime import date

@dataclass(frozen=True)
class ButToanLine:
    so_tai_khoan: str
    """Mã tài khoản theo chế độ kế toán VN. Ví dụ: 111, 112, 131, 511.
    Dùng để xác định tài khoản chịu ảnh hưởng của bút toán."""

    so_tien: Decimal
    """Số tiền của dòng bút toán. Phải >= 0. Không ghi âm theo chuẩn kế toán."""

    loai_giao_dich: str
    """'No' hoặc 'Co'. Áp dụng nguyên tắc ghi sổ kép (double-entry)."""

    so_chung_tu_goc: str
    """Số chứng từ gốc của giao dịch. Bắt buộc để truy xuất nguồn gốc."""

    ngay_chung_tu_goc: date
    """Ngày chứng từ gốc, dùng để đối chiếu báo cáo và truy vết."""
```

---

# 5. Application Layer (Python Use-case)

## 5.1 Use-case chuẩn

* Mỗi use-case là một class riêng.
* Không được gọi DB trực tiếp, chỉ thông qua repository interface.

Ví dụ — Posting bút toán:

```python
class PostingButToanService:
    def __init__(self, journal_repo):
        self.journal_repo = journal_repo

    def thuc_hien_post(self, but_toan):
        """Kiểm tra cân bằng Nợ = Có, validate rule kế toán và ghi vào sổ."""
        self._kiem_tra_can_bang(but_toan)
        self.journal_repo.luu(but_toan)
```

---

# 6. Infrastructure

## 6.1 Repository pattern

```python
class JournalRepository(Protocol):
    def luu(self, but_toan): ...
    def lay_theo_ngay(self, ngay): ...
```

## 6.2 SQLAlchemy ORM (không đưa logic nghiệp vụ vào ORM model)

```python
class JournalEntryModel(Base):
    __tablename__ = "journal_entries"
```

---

# 7. API Layer

* Dùng Pydantic/FastAPI schema
* Không chứa logic kế toán
* Chỉ nhận request → gọi use-case → trả response

Ví dụ:

```python
@router.post("/but-toan")
def post_but_toan(req: ButToanSchema):
    return posting_service.thuc_hien_post(req.to_domain())
```

---

# 8. Logging

* Bắt buộc dùng `logging` chuẩn Python
* Không dùng print()
* Tên logger theo module

Ví dụ:

```python
logger = logging.getLogger(__name__)
logger.info("Da post but toan thanh cong")
```

---

# 9. Testing Standards

* Dùng pytest
* Mỗi nghiệp vụ kế toán phải có test
* Dùng fake repository để test domain và use-case

Ví dụ test cân bằng Nợ/Có:

```python
def test_but_toan_khong_can_bang():
    with pytest.raises(ValueError):
        service.thuc_hien_post(but_toan_sai)
```

---

# 10. Coding Standards Python

* Tuân thủ PEP8
* snake_case
* Max line length 88
* Bắt buộc type hints
* Ưu tiên dataclass

---

# 11. Comment & Documentation

* Dùng docstring kiểu Google hoặc NumPy
* Comment giải thích **nghiệp vụ kế toán** cho người mới

Ví dụ:

```python
# Theo nguyên tắc kế toán: Tiền mặt tăng thì ghi Nợ 111
```

---

# 12. API Error Rules

* 400 → sai nghiệp vụ
* 422 → thiếu dữ liệu
* 500 → lỗi hệ thống

---

# 13. Versioning

* Dùng format: `vYYYY.MMDD.minor`

---

# 14. Quy tắc cấm

| Hành vi                     | Lý do                          |
| --------------------------- | ------------------------------ |
| Viết logic vào ORM model    | Phá vỡ Clean Architecture      |
| Dùng tiếng Anh trong domain | Mất ngôn ngữ ubiquitous        |
| print()                     | Không phù hợp với hệ thống lớn |

---

# 15. Kết luận

Tài liệu này là chuẩn bắt buộc cho toàn bộ hệ thống kế toán Python-based. Mọi PR vi phạm sẽ bị từ chối cho đến khi tuân thủ đầy đủ.
