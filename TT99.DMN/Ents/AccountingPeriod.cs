// File: D:\tt99acct\TT99.DMN\Ents\AccountingPeriod.cs
using System;

namespace TT99.DMN.Ents
{
    /// <summary>
    /// Entity đại diện cho một Kỳ Kế toán.
    /// </summary>
    public class AccountingPeriod
    {
        // ID duy nhất cho kỳ kế toán
        public Guid Id { get; private set; }

        // Tên kỳ (ví dụ: "Năm tài chính 2025", "Quý 1-2025")
        public string Name { get; private set; } = string.Empty;

        // Ngày bắt đầu của kỳ (bao gồm)
        public DateTime StartDate { get; private set; }

        // Ngày kết thúc của kỳ (bao gồm)
        public DateTime EndDate { get; private set; }

        // Trạng thái: Đang mở (false) hoặc Đã khóa (true)
        public bool IsLocked { get; private set; } = false;

        // Constructor
        public AccountingPeriod(string name, DateTime startDate, DateTime endDate)
        {
            if (string.IsNullOrWhiteSpace(name))
            {
                throw new ArgumentException("Accounting Period name cannot be empty.", nameof(name));
            }

            if (startDate > endDate)
            {
                throw new ArgumentException("Start date cannot be after end date.", nameof(startDate));
            }

            Id = Guid.NewGuid();
            Name = name;
            StartDate = startDate.Date; // Chỉ lưu ngày
            EndDate = endDate.Date;     // Chỉ lưu ngày
        }

        // Phương thức cho phép EF Core tạo đối tượng (private, không khuyến khích dùng trực tiếp)
        private AccountingPeriod() { }

        /// <summary>
        /// Kiểm tra xem một ngày có thuộc kỳ này hay không.
        /// </summary>
        /// <param name="date">Ngày cần kiểm tra.</param>
        /// <returns>True nếu ngày nằm trong khoảng StartDate và EndDate (bao gồm hai đầu).</returns>
        public bool ContainsDate(DateTime date)
        {
            var dateOnly = date.Date;
            return dateOnly >= StartDate && dateOnly <= EndDate;
        }

        /// <summary>
        /// Đánh dấu kỳ là đã khóa.
        /// </summary>
        public void Lock()
        {
            if (IsLocked)
            {
                throw new InvalidOperationException($"Accounting Period '{Name}' is already locked.");
            }
            IsLocked = true;
        }

        /// <summary>
        /// Đánh dấu kỳ là đang mở.
        /// </summary>
        public void Unlock()
        {
            if (!IsLocked)
            {
                throw new InvalidOperationException($"Accounting Period '{Name}' is already unlocked.");
            }
            IsLocked = false;
        }
    }
}