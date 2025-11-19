// File: D:\tt99acct\TT99.INFR\Services\ReportQueryService.cs
using TT99.APPL.Qries; // <-- THÊM DÒNG NÀY để "thấy" GeneralLedgerDto
using TT99.APPL.Services; // <-- Đảm bảo namespace chứa IReportQueryService được "thấy"
using TT99.INFR.Data; // Để dùng TT99DbContext
using Microsoft.EntityFrameworkCore; // Để dùng ToListAsync
using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace TT99.INFR.Services
{
    /// <summary>
    /// Triển khai dịch vụ truy vấn báo cáo, giao tiếp với cơ sở dữ liệu thông qua EF Core.
    /// Dịch vụ này thực hiện các truy vấn phức tạp như Sổ Cái, Bảng cân đối Kế toán...
    /// </summary>
    public class ReportQueryService : IReportQueryService // <-- ĐẢM BẢO DÒNG NÀY CÓ: : IReportQueryService
    {
        // Sử dụng TT99DbContext để truy cập cơ sở dữ liệu
        private readonly TT99DbContext _context; 

        public ReportQueryService(TT99DbContext context)
        {
            _context = context;
        }

        /// <summary>
        /// Lấy dữ liệu Sổ Cái (General Ledger) trong một khoảng thời gian cụ thể.
        /// </summary>
        public async Task<List<GeneralLedgerDto>> GetGeneralLedgerEntries(
            DateTime startDate,
            DateTime endDate,
            string? accountNumber, // Tham số lọc tài khoản
            CancellationToken cancellationToken)
        {
            // Bước 1: Xây dựng truy vấn cơ sở
            var query = from entry in _context.JournalEntries // Header (Bút toán)
                        from detail in entry.Entries // Lines (Các dòng Nợ/Có)
                        join account in _context.Accounts // JOIN với Danh mục Tài khoản
                            on detail.AccountNumber equals account.AccountNumber
                        
                        // Lọc theo khoảng ngày (endDate là exclusive, đã được tính toán trong Handler)
                        where entry.TransactionDate >= startDate && entry.TransactionDate < endDate 
                        
                        // Chỉ lấy các bút toán đã được ghi sổ (Posted)
                        where entry.Status == "Posted" 
                        
                        // Ánh xạ trực tiếp sang DTO
                        select new GeneralLedgerDto
                        {
                            Date = entry.TransactionDate, // Ngày giao dịch
                            ReferenceId = entry.Id, 
                            AccountNumber = detail.AccountNumber, 
                            
                            // Lấy tên tài khoản từ bảng Account (Đã JOIN)
                            AccountName = account.AccountName, 
                            
                            Description = entry.Narration, // Diễn giải chung từ Header
                            
                            Debit = detail.DebitAmount,
                            Credit = detail.CreditAmount,
                        };

            // Bước 2: Áp dụng Lọc theo Tài khoản (nếu được cung cấp)
            if (!string.IsNullOrEmpty(accountNumber))
            {
                // Lọc nếu Số tài khoản trong dòng chi tiết khớp với tài khoản được yêu cầu
                query = query.Where(d => d.AccountNumber == accountNumber);
            }

            // Bước 3: Sắp xếp và thực thi truy vấn
            return await query
                .OrderBy(d => d.Date)
                .ThenBy(d => d.ReferenceId)
                .ToListAsync(cancellationToken);
        }
    }
}