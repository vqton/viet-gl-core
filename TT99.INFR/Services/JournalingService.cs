// File: D:\tt99acct\TT99.INFR\Services\JournalingService.cs
using MediatR;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using TT99.DMN.Ents;
using TT99.DMN.Interfaces;
using TT99.INFR.Data;

namespace TT99.INFR.Services
{
    /// <summary>
    /// Triển khai IJournalingService, chứa các quy tắc nghiệp vụ Kế toán phức tạp.
    /// Toàn bộ quy trình được thực hiện bất đồng bộ (async) để tránh deadlock.
    /// </summary>
    public class JournalingService : IJournalingService
    {
        private readonly TT99DbContext _context;
        private readonly IAccountingPeriodRepository _periodRepository;
        private readonly ILogger<JournalingService> _logger; // <-- Thêm ILogger

        public JournalingService(TT99DbContext context, IAccountingPeriodRepository periodRepository, ILogger<JournalingService> logger) // <-- Thêm vào Constructor
        {
            _context = context;
            _periodRepository = periodRepository;
            _logger = logger; // <-- Gán
        }
        
        /// <summary>
        /// Xử lý, xác thực, ghi sổ và lưu trữ một bút toán mới.
        /// Đây là phương thức chính được Command Handler gọi.
        /// </summary>
        /// <returns>ID (Guid) của bút toán đã được ghi sổ.</returns>
        public async Task<Guid> CreateJournalEntryAsync(JournalEntry entry, CancellationToken cancellationToken)
        {
            _logger.LogInformation("Bắt đầu tạo bút toán: {VoucherNumber}", entry.VoucherNumber);

            // 1. Kiểm tra kỳ kế toán trước khi gọi ValidateAndPostEntryAsync
            await ValidatePeriodAsync(entry.TransactionDate, cancellationToken);

            // 2. Xác thực và ghi sổ (Bất đồng bộ)
            await ValidateAndPostEntryAsync(entry);

            // 3. Thêm vào Context
            _context.JournalEntries.Add(entry);
            
            // 4. Lưu thay đổi vào cơ sở dữ liệu (Async)
            await _context.SaveChangesAsync(cancellationToken);

            _logger.LogInformation("Tạo bút toán thành công: {VoucherNumber}, ID: {Id}", entry.VoucherNumber, entry.Id);

            // Giả sử JournalEntry có thuộc tính Id
            return entry.Id; 
        }

        /// <summary>
        /// Xác thực và thực hiện ghi sổ bút toán (Async).
        /// </summary>
        /// <param name="entry">Bút toán cần được kiểm tra và ghi sổ.</param>
        public async Task ValidateAndPostEntryAsync(JournalEntry entry)
        {
            _logger.LogDebug("Bắt đầu xác thực bút toán: {VoucherNumber}", entry.VoucherNumber);

            // 1. Kiểm tra tính cân bằng của bút toán (Tổng Nợ = Tổng Có)
            if (!entry.IsBalanced())
            {
                var errorMsg = $"Bút toán {entry.VoucherNumber} không cân bằng. Vui lòng kiểm tra lại tổng Nợ và tổng Có.";
                _logger.LogError(errorMsg);
                throw new InvalidOperationException(errorMsg);
            }
            _logger.LogDebug("Bút toán {VoucherNumber} cân bằng.", entry.VoucherNumber);

            // 2. Kiểm tra sự tồn tại của Tài khoản (Bất đồng bộ)
            await CheckAccountExistenceAsync(entry); 
            _logger.LogDebug("Kiểm tra tài khoản tồn tại cho bút toán {VoucherNumber} thành công.", entry.VoucherNumber);

            // 3. Kiểm tra các quy tắc hạch toán phức tạp
            CheckSpecificAccountingRules(entry);
            _logger.LogDebug("Kiểm tra quy tắc hạch toán cho bút toán {VoucherNumber} thành công.", entry.VoucherNumber);

            // 4. Nếu mọi thứ hợp lệ, đánh dấu là đã ghi sổ (Post)
            entry.Post();
            _logger.LogInformation("Bút toán {VoucherNumber} đã được ghi sổ (Posted).", entry.VoucherNumber);
        }


        /// <summary>
        /// Kiểm tra xem ngày giao dịch có thuộc kỳ kế toán *đang mở* nào không.
        /// </summary>
        /// <param name="transactionDate">Ngày giao dịch của bút toán.</param>
        /// <param name="cancellationToken">Token hủy bỏ.</param>
        /// <exception cref="InvalidOperationException">Nếu ngày giao dịch không thuộc kỳ nào hoặc thuộc kỳ đã khóa.</exception>
        private async Task ValidatePeriodAsync(DateTime transactionDate, CancellationToken cancellationToken)
        {
            _logger.LogDebug("Kiểm tra kỳ kế toán cho ngày: {Date}", transactionDate);
            var period = await _periodRepository.GetPeriodByDateAsync(transactionDate, cancellationToken);

            if (period == null)
            {
                var errorMsg = $"Ngày giao dịch {transactionDate:yyyy-MM-dd} không thuộc kỳ kế toán nào đã được thiết lập.";
                _logger.LogError(errorMsg);
                throw new InvalidOperationException(errorMsg);
            }

            if (period.IsLocked)
            {
                var errorMsg = $"Ngày giao dịch {transactionDate:yyyy-MM-dd} thuộc kỳ kế toán '{period.Name}' đã bị khóa. Không thể ghi nhận giao dịch.";
                _logger.LogError(errorMsg);
                throw new InvalidOperationException(errorMsg);
            }
            _logger.LogDebug("Ngày giao dịch {Date} thuộc kỳ kế toán '{PeriodName}' đang mở.", transactionDate, period.Name);
        }


        /// <summary>
        /// Kiểm tra xem tất cả các tài khoản trong bút toán có tồn tại trong hệ thống hay không (Async).
        /// </summary>
        private async Task CheckAccountExistenceAsync(JournalEntry entry)
        {
            var uniqueAccountNumbers = entry.Entries.Select(e => e.AccountNumber).Distinct().ToList();

            foreach (var accountNumber in uniqueAccountNumbers)
            {
                // Sử dụng AnyAsync để kiểm tra không đồng bộ
                var accountExists = await _context.Accounts.AnyAsync(a => a.AccountNumber == accountNumber);
                if (!accountExists)
                {
                    var errorMsg = $"Tài khoản {accountNumber} không tồn tại trong hệ thống. Vui lòng kiểm tra lại cơ cấu tài khoản.";
                    _logger.LogError(errorMsg);
                    throw new InvalidOperationException(errorMsg);
                }
            }
        }

        /// <summary>
        /// Thực hiện kiểm tra các quy tắc hạch toán đặc thù theo TT99 (Có thể mở rộng sau).
        /// </summary>
        private void CheckSpecificAccountingRules(JournalEntry entry)
        {
            // Ví dụ: Ngăn chặn việc ghi Nợ trực tiếp vào TK Vốn 411 mà không qua một quy trình đặc biệt.
            if (entry.Entries.Any(e => e.AccountNumber == "411" && e.IsDebit()))
            {
                 var errorMsg = $"Không được phép ghi Nợ trực tiếp vào TK 411 (Vốn chủ sở hữu) cho bút toán {entry.VoucherNumber}.";
                 _logger.LogWarning(errorMsg); // Hoặc throw exception nếu nghiêm trọng
                 // throw new InvalidOperationException(errorMsg);
            }
        }

        /// <summary>
        /// Triển khai logic đảo ngược bút toán.
        /// </summary>
        public void ReverseEntry(Guid journalEntryId)
        {
            throw new NotImplementedException("Chức năng đảo ngược bút toán chưa được triển khai.");
        }
    }
}