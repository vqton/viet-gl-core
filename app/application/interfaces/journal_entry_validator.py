# path: app/application/interfaces/journal_entry_validator.py
from abc import ABC, abstractmethod
from app.domain.models.journal_entry import GhiSoKeToan

class JournalEntryValidatorInterface(ABC):
    """
    Interface định nghĩa các phương thức xác thực bút toán kế toán.
    
    Lớp này dùng để chứa các quy tắc nghiệp vụ phức tạp liên quan đến logic
    hạch toán (ví dụ: Quy tắc đối ứng, tính hợp lệ của cặp Nợ/Có) theo TT99.
    """

    @abstractmethod
    def validate(self, entry: GhiSoKeToan):
        """
        Thực hiện xác thực toàn bộ bút toán.
        
        Args:
            entry: Domain model GhiSoKeToan cần được xác thực.

        Raises:
            ValueError: Nếu bút toán vi phạm bất kỳ quy tắc nghiệp vụ nào.
        """
        pass