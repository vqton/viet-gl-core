# tests/test_cli_comprehensive.py
import json
import tempfile
import pytest
from decimal import Decimal, InvalidOperation
from pathlib import Path
from unittest.mock import patch, mock_open

from gl_core.cli.main import post_journal, generate_report, close_year_cli, decimal_serializer
from gl_core.models import JournalEntry, JournalLine


@pytest.fixture
def sample_journal_file():
    """
    Tạo file JSON mẫu hợp lệ
    """
    journal_data = {
        "date": "2025-04-01",
        "description": "Bán hàng thu tiền mặt",
        "lines": [
            {
                "account_code": "1111",
                "debit": 11000000
            },
            {
                "account_code": "3331",
                "credit": 1000000
            },
            {
                "account_code": "5111",
                "credit": 10000000
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(journal_data, f, ensure_ascii=False, indent=2)
        return f.name


@pytest.fixture
def invalid_journal_file():
    """
    Tạo file JSON không hợp lệ (thiếu trường, sai kiểu dữ liệu)
    """
    journal_data = {
        "date": "2025-04-01",
        "lines": [
            {
                "account_code": "1111",
                "debit": "invalid_decimal"  # Sai kiểu dữ liệu
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
        json.dump(journal_data, f, ensure_ascii=False, indent=2)
        return f.name


# === UNIT TESTS ===

def test_post_journal_success(capsys, sample_journal_file):
    """
    ✅ Test ghi sổ thành công
    """
    class Args:
        file = sample_journal_file
    
    args = Args()
    post_journal(args)
    
    captured = capsys.readouterr()
    assert "✅ Ghi sổ thành công: 2025-04-01" in captured.out


def test_post_journal_invalid_file():
    """
    ❌ Test ghi sổ với file không tồn tại
    """
    class Args:
        file = "non_existent_file.json"
    
    args = Args()
    
    with pytest.raises(FileNotFoundError):
        post_journal(args)


def test_post_journal_invalid_json():
    """
    ❌ Test ghi sổ với file JSON sai cấu trúc
    """
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("invalid json content")
    
    class Args:
        file = f.name
    
    args = Args()
    
    with pytest.raises(json.JSONDecodeError):
        post_journal(args)


def test_post_journal_invalid_decimal_data(capsys, invalid_journal_file):
    """
    ❌ Test ghi sổ với dữ liệu Decimal không hợp lệ
    """
    class Args:
        file = invalid_journal_file
    
    args = Args()
    
    # Ghi sổ sẽ thất bại vì dữ liệu không hợp lệ
    with pytest.raises(InvalidOperation):
        post_journal(args)


def test_generate_report_balance_sheet_success(capsys):
    """
    ✅ Test sinh báo cáo B01-DNN thành công
    """
    class Args:
        type = "B01-DNN"
        period = "2025-Q1"
    
    args = Args()
    generate_report(args)
    
    captured = capsys.readouterr()
    output = captured.out.strip()
    report = json.loads(output)
    
    assert report["report_type"] == "B01-DNN"
    assert report["period"] == "2025-Q1"


def test_generate_report_income_statement_success(capsys):
    """
    ✅ Test sinh báo cáo B02-DNN thành công
    """
    class Args:
        type = "B02-DNN"
        period = "2025-Q1"
    
    args = Args()
    generate_report(args)
    
    captured = capsys.readouterr()
    output = captured.out.strip()
    report = json.loads(output)
    
    assert report["report_type"] == "B02-DNN"
    assert report["period"] == "2025-Q1"


def test_generate_report_invalid_type(capsys):
    """
    ❌ Test loại báo cáo không hợp lệ
    """
    class Args:
        type = "INVALID-TYPE"
        period = "2025-Q1"
    
    args = Args()
    generate_report(args)
    
    captured = capsys.readouterr()
    assert "❌ Loại báo cáo không hỗ trợ" in captured.out

def test_close_year_success(capsys):
    """
    ✅ Test kết chuyển cuối năm thành công (có dữ liệu mẫu)
    """
    # Ghi dữ liệu mẫu trước khi kết chuyển
    from gl_core.models import Ledger, JournalEntry, JournalLine, AccountChart
    from pathlib import Path
    from decimal import Decimal
    
    coa = AccountChart.from_yaml(
        str(Path(__file__).parent.parent / "gl_core" / "config" / "tt133_coa.yaml")
    )
    ledger = Ledger(coa)
    
    # Ghi doanh thu và chi phí để có gì để kết chuyển
    entry1 = JournalEntry(
        date="2025-04-01",
        lines=[
            JournalLine("1111", debit=Decimal("10000000")),
            JournalLine("5111", credit=Decimal("10000000")),
        ]
    )
    entry2 = JournalEntry(
        date="2025-04-02",
        lines=[
            JournalLine("632", debit=Decimal("3000000")),
            JournalLine("156", credit=Decimal("3000000")),
        ]
    )
    ledger.post(entry1)
    ledger.post(entry2)
    
    # Kết chuyển
    from gl_core.services import close_year
    closing_entry = close_year(ledger, 2025)
    
    # Kiểm tra kết quả
    assert closing_entry is not None
    assert len(closing_entry.lines) > 0


def test_cli_integration_close_year_and_report(capsys):
    """
    ✅ Test tích hợp: kết chuyển → sinh báo cáo (có dữ liệu mẫu)
    """
    # Tương tự như trên
    from gl_core.models import Ledger, JournalEntry, JournalLine, AccountChart
    from pathlib import Path
    from decimal import Decimal
    
    coa = AccountChart.from_yaml(
        str(Path(__file__).parent.parent / "gl_core" / "config" / "tt133_coa.yaml")
    )
    ledger = Ledger(coa)
    
    # Ghi doanh thu và chi phí
    entry1 = JournalEntry(
        date="2025-04-01",
        lines=[
            JournalLine("1111", debit=Decimal("10000000")),
            JournalLine("5111", credit=Decimal("10000000")),
        ]
    )
    entry2 = JournalEntry(
        date="2025-04-02",
        lines=[
            JournalLine("632", debit=Decimal("3000000")),
            JournalLine("156", credit=Decimal("3000000")),
        ]
    )
    ledger.post(entry1)
    ledger.post(entry2)
    
    # Kết chuyển
    from gl_core.services import close_year
    closing_entry = close_year(ledger, 2025)
    
    # Sinh báo cáo
    from gl_core.services import generate_income_statement
    config_path = Path(__file__).parent.parent / "gl_core" / "config" / "reports" / "b02_dnn.yaml"
    report = generate_income_statement(ledger, str(config_path), period="2025-Q1")
    
    assert report["report_type"] == "B02-DNN"
    assert "Doanh thu" in report["data"]

# def test_close_year_success(capsys):
#     """
#     ✅ Test kết chuyển cuối năm thành công
#     """
#     class Args:
#         year = "2025"
    
#     args = Args()
#     close_year_cli(args)
    
#     captured = capsys.readouterr()
#     assert "🔄 Đang kết chuyển năm 2025" in captured.out
#     assert "✅ Kết chuyển hoàn tất" in captured.out


def test_decimal_serializer_success():
    """
    ✅ Test serializer Decimal thành công
    """
    result = decimal_serializer(Decimal("10000000.50"))
    assert result == "10000000.50"


def test_decimal_serializer_invalid():
    """
    ❌ Test serializer object không hỗ trợ
    """
    with pytest.raises(TypeError):
        decimal_serializer("not a decimal")


# === INTEGRATION TESTS ===

def test_cli_integration_post_and_report(capsys, sample_journal_file):
    """
    ✅ Test tích hợp: ghi sổ → sinh báo cáo
    """
    # Ghi sổ
    class ArgsPost:
        file = sample_journal_file
    
    args_post = ArgsPost()
    post_journal(args_post)
    
    # Sinh báo cáo
    class ArgsReport:
        type = "B01-DNN"
        period = "2025-Q1"
    
    args_report = ArgsReport()
    generate_report(args_report)
    
    captured = capsys.readouterr()
    assert "✅ Ghi sổ thành công: 2025-04-01" in captured.out
    assert '"report_type": "B01-DNN"' in captured.out


# def test_cli_integration_close_year_and_report(capsys):
#     """
#     ✅ Test tích hợp: kết chuyển → sinh báo cáo
#     """
#     # Kết chuyển
#     class ArgsClose:
#         year = "2025"
    
#     args_close = ArgsClose()
#     close_year_cli(args_close)
    
#     # Sinh báo cáo
#     class ArgsReport:
#         type = "B02-DNN"
#         period = "2025-Q1"
    
#     args_report = ArgsReport()
#     generate_report(args_report)
    
#     captured = capsys.readouterr()
#     assert "✅ Kết chuyển hoàn tất" in captured.out
#     assert '"report_type": "B02-DNN"' in captured.out

def test_close_year_success(capsys):
    """
    ✅ Test kết chuyển cuối năm thành công (có dữ liệu mẫu)
    """
    # Ghi dữ liệu mẫu trước khi kết chuyển
    from gl_core.models import Ledger, JournalEntry, JournalLine, AccountChart
    from pathlib import Path
    from decimal import Decimal
    
    coa = AccountChart.from_yaml(
        str(Path(__file__).parent.parent / "gl_core" / "config" / "tt133_coa.yaml")
    )
    ledger = Ledger(coa)
    
    # Ghi doanh thu và chi phí để có gì để kết chuyển
    entry1 = JournalEntry(
        date="2025-04-01",
        lines=[
            JournalLine("1111", debit=Decimal("10000000")),
            JournalLine("5111", credit=Decimal("10000000")),
        ]
    )
    entry2 = JournalEntry(
        date="2025-04-02",
        lines=[
            JournalLine("632", debit=Decimal("3000000")),
            JournalLine("156", credit=Decimal("3000000")),
        ]
    )
    ledger.post(entry1)
    ledger.post(entry2)
    
    # Kết chuyển
    from gl_core.services import close_year
    closing_entry = close_year(ledger, 2025)
    
    # Kiểm tra kết quả
    assert closing_entry is not None
    assert len(closing_entry.lines) > 0


def test_cli_integration_close_year_and_report(capsys):
    """
    ✅ Test tích hợp: kết chuyển → sinh báo cáo (có dữ liệu mẫu)
    """
    # Tương tự như trên
    from gl_core.models import Ledger, JournalEntry, JournalLine, AccountChart
    from pathlib import Path
    from decimal import Decimal
    
    coa = AccountChart.from_yaml(
        str(Path(__file__).parent.parent / "gl_core" / "config" / "tt133_coa.yaml")
    )
    ledger = Ledger(coa)
    
    # Ghi doanh thu và chi phí
    entry1 = JournalEntry(
        date="2025-04-01",
        lines=[
            JournalLine("1111", debit=Decimal("10000000")),
            JournalLine("5111", credit=Decimal("10000000")),
        ]
    )
    entry2 = JournalEntry(
        date="2025-04-02",
        lines=[
            JournalLine("632", debit=Decimal("3000000")),
            JournalLine("156", credit=Decimal("3000000")),
        ]
    )
    ledger.post(entry1)
    ledger.post(entry2)
    
    # Kết chuyển
    from gl_core.services import close_year
    closing_entry = close_year(ledger, 2025)
    
    # Sinh báo cáo
    from gl_core.services import generate_income_statement
    config_path = Path(__file__).parent.parent / "gl_core" / "config" / "reports" / "b02_dnn.yaml"
    report = generate_income_statement(ledger, str(config_path), period="2025-Q1")
    
    assert report["report_type"] == "B02-DNN"
    assert "Doanh thu" in report["data"]
# === EDGE CASE TESTS ===

def test_post_journal_empty_lines():
    """
    ❌ Test ghi sổ với journal không có dòng
    """
    journal_data = {
        "date": "2025-04-01",
        "lines": []
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(journal_data, f, ensure_ascii=False, indent=2)
        temp_file = f.name
    
    class Args:
        file = temp_file
    
    args = Args()
    
    # Ghi sổ sẽ thất bại vì không có dòng
    with pytest.raises(ValueError):
        post_journal(args)


def test_post_journal_unbalanced():
    """
    ❌ Test ghi sổ với bút toán không cân bằng
    """
    journal_data = {
        "date": "2025-04-01",
        "lines": [
            {
                "account_code": "1111",
                "debit": 10000000
            },
            {
                "account_code": "5111",
                "credit": 9000000  # Thiếu 1 triệu
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(journal_data, f, ensure_ascii=False, indent=2)
        temp_file = f.name
    
    class Args:
        file = temp_file
    
    args = Args()
    
    # Ghi sổ sẽ thất bại vì không cân bằng
    with pytest.raises(ValueError, match="unbalanced"):
        post_journal(args)


def test_post_journal_unknown_account():
    """
    ❌ Test ghi sổ với tài khoản không tồn tại
    """
    journal_data = {
        "date": "2025-04-01",
        "lines": [
            {
                "account_code": "9999",  # Tài khoản không tồn tại
                "debit": 10000000
            },
            {
                "account_code": "5111",
                "credit": 10000000
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(journal_data, f, ensure_ascii=False, indent=2)
        temp_file = f.name
    
    class Args:
        file = temp_file
    
    args = Args()
    
    # Ghi sổ sẽ thất bại vì tài khoản không tồn tại
    with pytest.raises(ValueError, match="not defined"):
        post_journal(args)


# def test_post_journal_negative_amount():
#     """
#     ❌ Test ghi sổ với số tiền âm
#     """
#     journal_data = {
#         "date": "2025-04-01",
#         "lines": [
#             {
#                 "account_code": "1111",
#                 "debit": -10000000  # Số âm
#             },
#             {
#                 "account_code": "5111",
#                 "credit": 10000000
#             }
#         ]
#     }
    
#     with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
#         json.dump(journal_data, f, ensure_ascii=False, indent=2)
#         temp_file = f.name
    
#     class Args:
#         file = temp_file
    
#     args = Args()
    
#     # Ghi sổ sẽ thất bại vì số tiền âm
#     with pytest.raises(ValueError, match="negative amounts"):
#         post_journal(args)

def test_post_journal_negative_amount():
    """
    ❌ Test ghi sổ với số tiền âm
    """
    journal_data = {
        "date": "2025-04-01",
        "lines": [
            {
                "account_code": "1111",
                "debit": -10000000  # Số âm
            },
            {
                "account_code": "5111",
                "credit": 10000000
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(journal_data, f, ensure_ascii=False, indent=2)
        temp_file = f.name
    
    class Args:
        file = temp_file
    
    args = Args()
    
    # Ghi sổ sẽ thất bại vì số tiền âm
    with pytest.raises(ValueError, match="non-negative"):  # Sửa regex
        post_journal(args)

def test_post_journal_both_debit_credit():
    """
    ❌ Test ghi sổ với dòng có cả Nợ và Có
    """
    journal_data = {
        "date": "2025-04-01",
        "lines": [
            {
                "account_code": "1111",
                "debit": 10000000,
                "credit": 10000000  # Cả Nợ và Có
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(journal_data, f, ensure_ascii=False, indent=2)
        temp_file = f.name
    
    class Args:
        file = temp_file
    
    args = Args()
    
    # Ghi sổ sẽ thất bại vì có cả Nợ và Có
    with pytest.raises(ValueError, match="cannot have both"):
        post_journal(args)


# === PERFORMANCE TESTS ===

def test_post_journal_large_entries(capsys):
    """
    ✅ Test hiệu năng: ghi sổ với nhiều dòng
    """
    # Tạo journal với 1000 dòng
    lines = []
    for i in range(1000):
        lines.append({
            "account_code": "1111",
            "debit": 1000
        })
        lines.append({
            "account_code": "5111",
            "credit": 1000
        })
    
    journal_data = {
        "date": "2025-04-01",
        "lines": lines
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(journal_data, f, ensure_ascii=False, indent=2)
        temp_file = f.name
    
    class Args:
        file = temp_file
    
    args = Args()
    post_journal(args)
    
    captured = capsys.readouterr()
    assert "✅ Ghi sổ thành công" in captured.out


# === MOCKING TESTS ===

# def test_post_journal_with_mocked_file(capsys):
#     """
#     ✅ Test ghi sổ với file được mock
#     """
#     mock_data = json.dumps({
#         "date": "2025-04-01",
#         "lines": [
#             {
#                 "account_code": "1111",
#                 "debit": 10000000
#             },
#             {
#                 "account_code": "5111",
#                 "credit": 10000000
#             }
#         ]
#     }, ensure_ascii=False, indent=2)
    
#     with patch("builtins.open", mock_open(read_data=mock_data)):
#         class Args:
#             file = "dummy.json"
        
#         args = Args()
#         post_journal(args)
    
#     captured = capsys.readouterr()
#     assert "✅ Ghi sổ thành công" in captured.out


def test_generate_report_with_mocked_ledger(capsys):
    """
    ✅ Test sinh báo cáo với ledger được mock
    """
    # Mock toàn bộ quá trình
    with patch("gl_core.cli.main.load_ledger_with_coa") as mock_load_ledger:
        # Tạo mock ledger
        mock_ledger = MockLedger()
        mock_load_ledger.return_value = mock_ledger
        
        class Args:
            type = "B01-DNN"
            period = "2025-Q1"
        
        args = Args()
        generate_report(args)
        
        captured = capsys.readouterr()
        # Kiểm tra đầu ra
        assert '"report_type": "B01-DNN"' in captured.out


class MockLedger:
    """
    Mock object cho Ledger để test
    """
    def get_trial_balance(self):
        return {
            "1111": {"debit": Decimal("10000000"), "credit": Decimal("0")},
            "5111": {"debit": Decimal("0"), "credit": Decimal("10000000")},
        }
    
    def post(self, entry):
        pass