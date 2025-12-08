from datetime import date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

# Domain Models - Đại diện cho các thực thể nghiệp vụ (business entities)
from app.domain.models.journal_entry import JournalEntry as JournalEntryDomain
from app.domain.models.journal_entry import (
    JournalEntryLine as JournalEntryLineDomain,
)

# Infrastructure Models (ORM) - Ánh xạ tới cấu trúc bảng trong CSDL
from app.infrastructure.models.sql_journal_entry import (
    SQLJournalEntry,
    SQLJournalEntryLine,
)

# Repository khác để kiểm tra tính toàn vẹn dữ liệu (data integrity)
from app.infrastructure.repositories.account_repository import (
    AccountRepository,
)


class JournalEntryRepository:
    """
    Repository cho Bút Toán (JournalEntry).

    Chịu trách nhiệm giao tiếp giữa Domain Layer và Database (thông qua SQLAlchemy ORM)
    để thực hiện các thao tác CRUD và truy vấn báo cáo.
    """

    def __init__(self, db_session: Session):
        """
        Khởi tạo Repository.

        Args:
            db_session: Session kết nối CSDL của SQLAlchemy.
        """
        self.db_session = db_session
        # Khởi tạo AccountRepository để thực hiện các kiểm tra liên quan đến tài khoản
        self.account_repository = AccountRepository(db_session)

    def add(
        self, journal_entry_domain: JournalEntryDomain
    ) -> JournalEntryDomain:
        """
        Thêm một bút toán mới (gồm header và lines) vào cơ sở dữ liệu.

        Quy tắc nghiệp vụ:
        1. Phải kiểm tra tất cả các tài khoản trong dòng bút toán có tồn tại không.
        2. Bút toán được thêm vào CSDL với trạng thái ban đầu do người dùng cung cấp.

        Args:
            journal_entry_domain: Đối tượng Domain JournalEntry chứa dữ liệu bút toán.

        Returns:
            JournalEntryDomain: Đối tượng bút toán đã được thêm, bao gồm ID được tạo ra.

        Raises:
            ValueError: Nếu một trong các số tài khoản trong dòng bút toán không tồn tại.
        """
        # Kiểm tra tài khoản tồn tại cho từng dòng để đảm bảo tính toàn vẹn tham chiếu
        for line in journal_entry_domain.lines:
            tai_khoan = self.account_repository.get_by_id(line.so_tai_khoan)
            if not tai_khoan:
                raise ValueError(
                    f"Tài khoản '{line.so_tai_khoan}' trong bút toán không tồn tại."
                )

        # Chuyển đổi từ Domain Entity (JournalEntryDomain) sang ORM Model (SQLJournalEntry)
        sql_journal_entry = SQLJournalEntry(
            ngay_ct=journal_entry_domain.ngay_ct,
            so_phieu=journal_entry_domain.so_phieu,
            mo_ta=journal_entry_domain.mo_ta,
            trang_thai=journal_entry_domain.trang_thai,
            # lines sẽ được thêm sau
        )
        self.db_session.add(sql_journal_entry)
        # Flush để lấy được ID tự sinh (ID) của SQLJournalEntry.
        # ID này cần thiết để gán cho các dòng bút toán (SQLJournalEntryLine.journal_entry_id).
        self.db_session.flush()

        # Thêm các dòng bút toán
        sql_lines = []
        for line in journal_entry_domain.lines:
            sql_line = SQLJournalEntryLine(
                journal_entry_id=sql_journal_entry.id,
                so_tai_khoan=line.so_tai_khoan,
                no=line.no,
                co=line.co,
                mo_ta=line.mo_ta,
            )
            sql_lines.append(sql_line)

        self.db_session.add_all(sql_lines)
        self.db_session.commit()
        # Refresh để đảm bảo lấy được trạng thái mới nhất, bao gồm cả các dòng đã được gán
        self.db_session.refresh(sql_journal_entry)

        # Chuyển đổi lại về Domain Entity để trả về kết quả thành công, bao gồm ID
        lines_domain = [
            JournalEntryLineDomain(
                so_tai_khoan=line.so_tai_khoan,
                no=line.no,
                co=line.co,
                mo_ta=line.mo_ta,
            )
            for line in sql_journal_entry.lines
        ]

        return JournalEntryDomain(
            id=sql_journal_entry.id,
            ngay_ct=sql_journal_entry.ngay_ct,
            so_phieu=sql_journal_entry.so_phieu,
            mo_ta=sql_journal_entry.mo_ta,
            lines=lines_domain,
            trang_thai=sql_journal_entry.trang_thai,
        )

    def get_by_id(self, id: int) -> Optional[JournalEntryDomain]:
        """
        Lấy thông tin bút toán theo ID, bao gồm các dòng chi tiết.

        Args:
            id: ID của bút toán cần lấy.

        Returns:
            Optional[JournalEntryDomain]: Đối tượng bút toán nếu tìm thấy, ngược lại là None.
        """
        # Sử dụng joinedload để tải eager loading (tải đồng thời) các dòng
        # bút toán (lines) trong cùng một truy vấn, tránh N+1 query.
        sql_j = (
            self.db_session.query(SQLJournalEntry)
            .options(joinedload(SQLJournalEntry.lines))
            .filter(SQLJournalEntry.id == id)
            .first()
        )
        if not sql_j:
            return None

        # Chuyển đổi từ ORM Model sang Domain Entity
        lines_domain = [
            JournalEntryLineDomain(
                so_tai_khoan=line.so_tai_khoan,
                no=line.no,
                co=line.co,
                mo_ta=line.mo_ta,
            )
            for line in sql_j.lines
        ]
        return JournalEntryDomain(
            id=sql_j.id,
            ngay_ct=sql_j.ngay_ct,
            so_phieu=sql_j.so_phieu,
            mo_ta=sql_j.mo_ta,
            lines=lines_domain,
            trang_thai=sql_j.trang_thai,
        )

    def get_all(self) -> List[JournalEntryDomain]:
        """
        Lấy danh sách tất cả bút toán, bao gồm các dòng chi tiết.

        Returns:
            List[JournalEntryDomain]: Danh sách tất cả các bút toán.
        """
        sql_journal_entries = (
            self.db_session.query(SQLJournalEntry)
            .options(joinedload(SQLJournalEntry.lines))
            .all()
        )
        journal_entries_domain = []
        # Lặp qua kết quả và chuyển đổi từng ORM Model sang Domain Entity
        for sql_j in sql_journal_entries:
            lines_domain = [
                JournalEntryLineDomain(
                    so_tai_khoan=line.so_tai_khoan,
                    no=line.no,
                    co=line.co,
                    mo_ta=line.mo_ta,
                )
                for line in sql_j.lines
            ]
            journal_entries_domain.append(
                JournalEntryDomain(
                    id=sql_j.id,
                    ngay_ct=sql_j.ngay_ct,
                    so_phieu=sql_j.so_phieu,
                    mo_ta=sql_j.mo_ta,
                    lines=lines_domain,
                    trang_thai=sql_j.trang_thai,
                )
            )
        return journal_entries_domain

    def get_all_by_period(self, period_id: int) -> List[SQLJournalEntry]:
        """
        Lấy tất cả bút toán trong một kỳ kế toán (dùng cho mục đích báo cáo/khóa sổ).

        Lưu ý: Phương thức này trả về SQL ORM Model, không phải Domain Model.

        Args:
            period_id: ID của kỳ kế toán.

        Returns:
            List[SQLJournalEntry]: Danh sách các SQLJournalEntry trong kỳ.
        """
        # Giả định SQLJournalEntry có trường period_id
        # Hiện tại, chỉ trả về tất cả vì mô hình SQLJournalEntry trong snippet chưa có period_id
        # Nếu SQLJournalEntry có period_id, nên dùng:
        # return self.db_session.query(SQLJournalEntry).filter(SQLJournalEntry.period_id == period_id).all()
        return self.db_session.query(SQLJournalEntry).all()

    def update(
        self, id: int, journal_entry_domain_updated: JournalEntryDomain
    ) -> Optional[JournalEntryDomain]:
        """
        Cập nhật thông tin bút toán theo ID.

        Quy tắc nghiệp vụ:
        - Việc cập nhật bút toán thường chỉ được phép nếu bút toán chưa được "Posted"
          hoặc nếu người dùng có quyền đặc biệt.
        - Phương thức này thực hiện thay thế hoàn toàn các dòng bút toán cũ bằng các dòng mới.

        Args:
            id: ID của bút toán cần cập nhật.
            journal_entry_domain_updated: Đối tượng Domain JournalEntry chứa dữ liệu mới.

        Returns:
            Optional[JournalEntryDomain]: Đối tượng bút toán đã được cập nhật, ngược lại là None nếu không tìm thấy ID.

        Raises:
            ValueError: Nếu một trong các số tài khoản trong dòng bút toán cập nhật không tồn tại.
        """
        sql_journal_entry = (
            self.db_session.query(SQLJournalEntry)
            .options(joinedload(SQLJournalEntry.lines))
            .filter(SQLJournalEntry.id == id)
            .first()
        )
        if not sql_journal_entry:
            return None

        # 1. Cập nhật thông tin header (thông tin chính của bút toán)
        sql_journal_entry.ngay_ct = journal_entry_domain_updated.ngay_ct
        sql_journal_entry.so_phieu = journal_entry_domain_updated.so_phieu
        sql_journal_entry.mo_ta = journal_entry_domain_updated.mo_ta
        sql_journal_entry.trang_thai = journal_entry_domain_updated.trang_thai

        # 2. Xóa lines cũ
        # Đây là chiến lược "xóa tất cả, thêm mới tất cả" cho các dòng bút toán
        for line in sql_journal_entry.lines:
            self.db_session.delete(line)

        # 3. Thêm lines mới
        sql_lines = []
        for line_domain in journal_entry_domain_updated.lines:
            # Kiểm tra tài khoản tồn tại cho dòng mới (Đảm bảo tính toàn vẹn)
            tai_khoan = self.account_repository.get_by_id(
                line_domain.so_tai_khoan
            )
            if not tai_khoan:
                raise ValueError(
                    f"Tài khoản '{line_domain.so_tai_khoan}' trong bút toán cập nhật không tồn tại."
                )

            sql_line = SQLJournalEntryLine(
                journal_entry_id=sql_journal_entry.id,
                so_tai_khoan=line_domain.so_tai_khoan,
                no=line_domain.no,
                co=line_domain.co,
                mo_ta=line_domain.mo_ta,
            )
            sql_lines.append(sql_line)

        # Gán lại relationship mới (SQLAlchemy sẽ tự động thêm vào CSDL khi commit)
        sql_journal_entry.lines = sql_lines

        self.db_session.commit()
        self.db_session.refresh(sql_journal_entry)

        # Chuyển đổi lại về Domain Entity để trả về kết quả sau khi cập nhật
        lines_domain_updated = [
            JournalEntryLineDomain(
                so_tai_khoan=line.so_tai_khoan,
                no=line.no,
                co=line.co,
                mo_ta=line.mo_ta,
            )
            for line in sql_journal_entry.lines
        ]
        return JournalEntryDomain(
            id=sql_journal_entry.id,
            ngay_ct=sql_journal_entry.ngay_ct,
            so_phieu=sql_journal_entry.so_phieu,
            mo_ta=sql_journal_entry.mo_ta,
            lines=lines_domain_updated,
            trang_thai=sql_journal_entry.trang_thai,
        )

    def delete(self, id: int) -> bool:
        """
        Xóa một bút toán (header) và các dòng (lines) liên quan.

        Args:
            id: ID của bút toán cần xóa.

        Returns:
            bool: True nếu bút toán được xóa thành công, False nếu không tìm thấy bút toán.
        """
        sql_journal_entry = (
            self.db_session.query(SQLJournalEntry)
            .options(joinedload(SQLJournalEntry.lines))
            .filter(SQLJournalEntry.id == id)
            .first()
        )
        if not sql_journal_entry:
            return False

        # Xóa các dòng trước (dù ORM thường hỗ trợ Cascade Delete, việc xóa thủ công
        # đảm bảo xóa các dòng liên quan trong mọi trường hợp).
        for line in sql_journal_entry.lines:
            self.db_session.delete(line)

        self.db_session.delete(sql_journal_entry)
        self.db_session.commit()
        return True

    def get_posted_lines_by_account_and_date(
        self, so_tai_khoan: str, end_date: date
    ) -> List[JournalEntryLineDomain]:
        """
        Lấy danh sách các dòng bút toán đã được 'Posted' (ghi sổ) cho một tài khoản cụ thể
        và có ngày chứng từ (ngay_ct) nhỏ hơn hoặc bằng end_date.

        Quy tắc nghiệp vụ: Chỉ các bút toán đã được "Posted" mới ảnh hưởng đến sổ cái.

        Args:
            so_tai_khoan: Số tài khoản cần truy vấn.
            end_date: Ngày kết thúc (bao gồm cả ngày này).

        Returns:
            List[JournalEntryLineDomain]: Danh sách các dòng bút toán đã được ghi sổ.
        """
        # 1. Query các dòng bút toán (SQLJournalEntryLine)
        sql_lines = (
            self.db_session.query(SQLJournalEntryLine)
            # 2. Join với bút toán cha (SQLJournalEntry) để lấy thông tin trạng thái và ngày
            .join(
                SQLJournalEntry,
                SQLJournalEntry.id == SQLJournalEntryLine.journal_entry_id,
            )
            # 3. Filter theo số tài khoản
            .filter(SQLJournalEntryLine.so_tai_khoan == so_tai_khoan)
            # 4. Filter theo trạng thái "Posted" (đã ghi sổ)
            .filter(SQLJournalEntry.trang_thai == "Posted")
            # 5. Filter theo ngày chứng từ (phục vụ tính số dư/số phát sinh luỹ kế)
            .filter(SQLJournalEntry.ngay_ct <= end_date).all()
        )

        # Chuyển đổi sang Domain VO (Value Object)
        return [
            JournalEntryLineDomain(
                so_tai_khoan=line.so_tai_khoan,
                no=line.no,
                co=line.co,
                mo_ta=line.mo_ta,
            )
            for line in sql_lines
        ]

    def get_all_posted_in_range(
        self, start: date, end: date
    ) -> List[JournalEntryDomain]:
        """
        Lấy danh sách các bút toán đã được 'Posted' (ghi sổ) trong một khoảng thời gian,
        bao gồm các dòng chi tiết.

        Args:
            start: Ngày bắt đầu của khoảng thời gian (bao gồm).
            end: Ngày kết thúc của khoảng thời gian (bao gồm).

        Returns:
            List[JournalEntryDomain]: Danh sách các bút toán đã được ghi sổ trong phạm vi ngày.
        """
        sql_journal_entries = (
            self.db_session.query(SQLJournalEntry)
            .options(joinedload(SQLJournalEntry.lines))
            .filter(
                SQLJournalEntry.trang_thai == "Posted"
            )  # Lọc theo trạng thái 'Posted'
            .filter(
                SQLJournalEntry.ngay_ct >= start
            )  # Ngày chứng từ >= ngày bắt đầu
            .filter(
                SQLJournalEntry.ngay_ct <= end
            )  # Ngày chứng từ <= ngày kết thúc
            .all()
        )

        # Chuyển đổi từ ORM Model sang Domain Entity
        journal_entries_domain = []
        for sql_j in sql_journal_entries:
            lines_domain = [
                JournalEntryLineDomain(
                    so_tai_khoan=line.so_tai_khoan,
                    no=line.no,
                    co=line.co,
                    mo_ta=line.mo_ta,
                )
                for line in sql_j.lines
            ]
            journal_entries_domain.append(
                JournalEntryDomain(
                    id=sql_j.id,
                    ngay_ct=sql_j.ngay_ct,
                    so_phieu=sql_j.so_phieu,
                    mo_ta=sql_j.mo_ta,
                    lines=lines_domain,
                    trang_thai=sql_j.trang_thai,
                )
            )
        return journal_entries_domain

    def get_draft_entries_by_date_range(
        self, start: date, end: date
    ) -> List[JournalEntryDomain]:
        return (
            self.db_session.query(SQLJournalEntry)
            .options(joinedload(SQLJournalEntry.lines))
            .filter(SQLJournalEntry.ngay_ct.between(start, end))
            .filter(SQLJournalEntry.trang_thai == "Draft")
            .all()
        )

    def get_so_du_dau_ky(self, so_tai_khoan: str, ngay: date) -> Decimal:
        """
        Tính số dư luỹ kế (Dư Nợ hoặc Dư Có) của một tài khoản cụ thể tại thời điểm đầu kỳ.

        Số dư được tính dựa trên tổng phát sinh Nợ và Có của các giao dịch đã "Posted"
        có ngày chứng từ TRƯỚC ngày được cung cấp (ngay_ct < ngay).

        Quy tắc nghiệp vụ:
        - Số dư đầu kỳ chỉ tính các giao dịch đã được "Posted" (ghi sổ).
        - Kết quả là số dương (Dư Nợ > 0 hoặc Dư Có > 0).
        - Logic xử lý sẽ xác định bản chất tài khoản (Debit-natured/Credit-natured)
          để chỉ trả về số dư cùng phía.

        Args:
            so_tai_khoan: Số tài khoản cần tính số dư.
            ngay: Ngày đầu kỳ (chỉ tính các giao dịch trước ngày này).

        Returns:
            Decimal: Số dư đầu kỳ của tài khoản. Giá trị luôn là số dương (hoặc 0)
                     và đại diện cho Dư Nợ hoặc Dư Có (tùy thuộc bản chất tài khoản).
        """

        # 1. Query tổng phát sinh Nợ và Có (luỹ kế) cho tài khoản đó, trước ngày 'ngay'
        subquery = (
            self.db_session.query(
                SQLJournalEntryLine.so_tai_khoan,
                func.sum(SQLJournalEntryLine.no).label("total_no"),
                func.sum(SQLJournalEntryLine.co).label("total_co"),
            )
            # Join với bút toán cha để lọc theo trạng thái và ngày
            .join(
                SQLJournalEntry,
                SQLJournalEntry.id == SQLJournalEntryLine.journal_entry_id,
            )
            # Lọc theo số tài khoản yêu cầu
            .filter(SQLJournalEntryLine.so_tai_khoan == so_tai_khoan)
            # Chỉ tính các bút toán đã "Posted" (ghi sổ)
            .filter(SQLJournalEntry.trang_thai == "Posted")
            # Chỉ tính các giao dịch có ngày chứng từ TRƯỚC ngày đang tính (ngay_ct < ngay)
            .filter(SQLJournalEntry.ngay_ct < ngay)
            .group_by(SQLJournalEntryLine.so_tai_khoan)
            .subquery()
        )

        # Thực thi truy vấn tổng hợp
        result = self.db_session.query(subquery).first()

        if not result:
            return Decimal(0)

        # Lấy tổng Nợ và tổng Có, nếu None thì coi là 0
        total_no = (
            result.total_no if result.total_no is not None else Decimal(0)
        )
        total_co = (
            result.total_co if result.total_co is not None else Decimal(0)
        )

        # 2. Tính Số dư Luỹ kế (Balance)
        # Số dương: Dư Nợ (Debit Balance). Số âm: Dư Có (Credit Balance).
        lu_y_ke = total_no - total_co

        # 3. Xác định bản chất tài khoản theo VAS (Quy tắc chung, cần được tinh chỉnh thực tế):
        # - Tài khoản có số dư NỢ (Debit-natured, VD: Tài sản, Chi phí): 1xx, 2xx, 6xx, 8xx
        # - Tài khoản có số dư CÓ (Credit-natured, VD: Nguồn vốn, Doanh thu): 3xx, 4xx, 5xx, 7xx, 9xx

        first_digit = so_tai_khoan[0]

        # Tài khoản loại Dư Nợ (Debit-natured: 1, 2, 6, 8)
        if first_digit in ['1', '2', '6', '8']:
            # Nếu luỹ kế > 0 (Dư Nợ) -> Trả về giá trị Dư Nợ.
            # Nếu luỹ kế <= 0 (Dư Có hoặc bằng 0) -> Trả về 0 (Giả định không có số dư ngược kỳ đầu)
            return lu_y_ke if lu_y_ke > 0 else Decimal(0)

        # Tài khoản loại Dư Có (Credit-natured: 3, 4, 5, 7, 9)
        elif first_digit in ['3', '4', '5', '7', '9']:
            # Nếu luỹ kế < 0 (Dư Có) -> Trả về giá trị tuyệt đối của nó (-lu_y_ke).
            # Nếu luỹ kế >= 0 (Dư Nợ hoặc bằng 0) -> Trả về 0 (Giả định không có số dư ngược kỳ đầu)
            return -lu_y_ke if lu_y_ke < 0 else Decimal(0)

        # Tài khoản đặc biệt hoặc không rõ bản chất (ví dụ TK 0xx - Ngoại bảng)
        else:
            # Đối với các tài khoản không rõ bản chất, cần thông tin từ AccountRepository
            # nhưng tạm thời trả về giá trị tuyệt đối cho các tài khoản chỉ có số dư đơn.
            return abs(lu_y_ke)
