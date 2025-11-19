// File: D:\tt99acct\TT99.APPL\Services\IReportQueryService.cs
using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using TT99.APPL.Qries; // Để dùng GeneralLedgerDto

namespace TT99.APPL.Services
{
    /// <summary>
    /// Giao diện định nghĩa các dịch vụ truy vấn báo cáo nghiệp vụ kế toán.
    /// </summary>
    public interface IReportQueryService
    {
        Task<List<GeneralLedgerDto>> GetGeneralLedgerEntries(
            DateTime startDate,
            DateTime endDate,
            string? accountNumber, // Tham số lọc tài khoản
            CancellationToken cancellationToken);
    }
}