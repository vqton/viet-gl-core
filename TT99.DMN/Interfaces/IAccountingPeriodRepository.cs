// File: D:\tt99acct\TT99.DMN\Interfaces\IAccountingPeriodRepository.cs
using System;
using System.Threading;
using System.Threading.Tasks;
using TT99.DMN.Ents;

namespace TT99.DMN.Interfaces
{
    /// <summary>
    /// Interface định nghĩa các phương thức truy cập dữ liệu cho kỳ kế toán.
    /// </summary>
    public interface IAccountingPeriodRepository
    {
        /// <summary>
        /// Lấy kỳ kế toán hiện tại (thường là kỳ chưa khóa gần nhất chứa ngày hiện tại).
        /// </summary>
        /// <param name="cancellationToken">Token hủy bỏ.</param>
        /// <returns>Kỳ kế toán hiện tại, hoặc null nếu không tìm thấy.</returns>
        Task<AccountingPeriod?> GetCurrentPeriodAsync(CancellationToken cancellationToken);

        /// <summary>
        /// Lấy kỳ kế toán theo ngày giao dịch.
        /// </summary>
        /// <param name="transactionDate">Ngày giao dịch.</param>
        /// <param name="cancellationToken">Token hủy bỏ.</param>
        /// <returns>Kỳ kế toán chứa ngày giao dịch, hoặc null nếu không tìm thấy.</returns>
        Task<AccountingPeriod?> GetPeriodByDateAsync(DateTime transactionDate, CancellationToken cancellationToken);

        /// <summary>
        /// Thêm một kỳ kế toán mới vào cơ sở dữ liệu.
        /// </summary>
        /// <param name="period">Kỳ kế toán cần thêm.</param>
        /// <param name="cancellationToken">Token hủy bỏ.</param>
        /// <returns>Task.</returns>
        Task AddAsync(AccountingPeriod period, CancellationToken cancellationToken);

        /// <summary>
        /// Cập nhật một kỳ kế toán trong cơ sở dữ liệu (dùng để khóa/mở kỳ).
        /// </summary>
        /// <param name="period">Kỳ kế toán cần cập nhật.</param>
        /// <param name="cancellationToken">Token hủy bỏ.</param>
        /// <returns>Task.</returns>
        Task UpdateAsync(AccountingPeriod period, CancellationToken cancellationToken);


        /// <summary>
        /// Lấy kỳ kế toán theo ID.
        /// </summary>
        /// <param name="id">ID của kỳ kế toán.</param>
        /// <param name="cancellationToken">Token hủy bỏ.</param>
        /// <returns>Kỳ kế toán, hoặc null nếu không tìm thấy.</returns>
        Task<AccountingPeriod?> GetByIdAsync(Guid id, CancellationToken cancellationToken); // <-- Thêm dòng này
    }
}