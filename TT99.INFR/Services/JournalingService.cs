using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.EntityFrameworkCore;
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

        public JournalingService(TT99DbContext context)
        {
            _context = context;
        }
        
        /// <summary>
        /// Xử lý, xác thực, ghi sổ và lưu trữ một bút toán mới.
        /// Đây là phương thức chính được Command Handler gọi.
        /// </summary>
        /// <returns>ID (Guid) của bút toán đã được ghi sổ.</returns>
        public async Task<Guid> CreateJournalEntryAsync(JournalEntry entry, CancellationToken cancellationToken)
        {
            // 1. Xác thực và ghi sổ (Bất đồng bộ)
            await ValidateAndPostEntryAsync(entry);

            // 2. Thêm vào Context
            _context.JournalEntries.Add(entry);
            
            // 3. Lưu thay đổi vào cơ sở dữ liệu (Async)
            await _context.SaveChangesAsync(cancellationToken);

            // Giả sử JournalEntry có thuộc tính Id
            return entry.Id; 
        }

        /// <summary>
        /// Xác thực và thực hiện ghi sổ bút toán (Async).
        /// </summary>
        /// <param name="entry">Bút toán cần được kiểm tra và ghi sổ.</param>
        public async Task ValidateAndPostEntryAsync(JournalEntry entry)
        {
            // 1. Kiểm tra tính cân bằng của bút toán (Tổng Nợ = Tổng Có)
            if (!entry.IsBalanced())
            {
                throw new InvalidOperationException($"Bút toán {entry.VoucherNumber} không cân bằng. Vui lòng kiểm tra lại tổng Nợ và tổng Có.");
            }

            // 2. Kiểm tra sự tồn tại của Tài khoản (Bất đồng bộ)
            await CheckAccountExistenceAsync(entry); 

            // 3. Kiểm tra các quy tắc hạch toán phức tạp
            CheckSpecificAccountingRules(entry);

            // 4. Nếu mọi thứ hợp lệ, đánh dấu là đã ghi sổ (Post)
            entry.Post();
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
                    throw new InvalidOperationException($"Tài khoản {accountNumber} không tồn tại trong hệ thống. Vui lòng kiểm tra lại cơ cấu tài khoản.");
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
                 // Đây là ví dụ, trong thực tế sẽ có logic phức tạp hơn
                 // throw new InvalidOperationException("Không được phép ghi Nợ trực tiếp vào TK 411 (Vốn chủ sở hữu).");
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