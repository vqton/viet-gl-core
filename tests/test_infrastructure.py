# tests/test_infrastructure.py
import pytest

from app.domain.models.account import LoaiTaiKhoan, TaiKhoan
from app.infrastructure.repositories.account_repository import (
    AccountRepository,
)
from tests.test_db import TestingSessionLocal


def test_account_repository_add_and_get():
    db = TestingSessionLocal()
    try:
        repo = AccountRepository(db)
        new_account = TaiKhoan(
            so_tai_khoan="131",
            ten_tai_khoan="Phải thu KH",
            loai_tai_khoan=LoaiTaiKhoan.TAI_SAN,
        )
        added = repo.add(new_account)
        retrieved = repo.get_by_id("131")
        assert retrieved.ten_tai_khoan == "Phải thu KH"
    finally:
        db.rollback()
        db.close()
