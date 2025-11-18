// File: D:\tt99acct\TT99.APPL\Qries\GetGeneralLedgerQuery.cs
using MediatR;
using System;
using System.Collections.Generic;

namespace TT99.APPL.Qries
{
    /// <summary>
    /// Query (Truy vấn) yêu cầu hệ thống xuất Báo cáo Sổ Cái.
    /// IRequest<List<GeneralLedgerDto>> chỉ định rằng Query này sẽ trả về một danh sách các DTO Sổ Cái.
    /// </summary>
    public class GetGeneralLedgerQuery : IRequest<List<GeneralLedgerDto>>
    {
        public DateTime StartDate { get; set; }
        public DateTime EndDate { get; set; }
        public string? AccountNumber { get; set; } // Lọc theo tài khoản cụ thể (Optional) - ĐÃ SỬA: Thêm dấu ?
    }
}