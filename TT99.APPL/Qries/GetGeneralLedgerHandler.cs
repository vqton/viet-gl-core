using MediatR;
using TT99.APPL.Services;
using System.Threading;
using System.Threading.Tasks;
using System.Collections.Generic;
using System;

namespace TT99.APPL.Qries
{
    /// <summary>
    /// Handler MediatR cho việc xử lý truy vấn lấy Sổ Cái (General Ledger).
    /// Nó gọi IReportQueryService với các tham số lọc được cung cấp.
    /// </summary>
    public class GetGeneralLedgerHandler : IRequestHandler<GetGeneralLedgerQuery, List<GeneralLedgerDto>>
    {
        private readonly IReportQueryService _queryService;

        /// <summary>
        /// Khởi tạo Handler với dịch vụ truy vấn báo cáo.
        /// </summary>
        /// <param name="queryService">Dịch vụ truy vấn thực hiện logic truy cập dữ liệu.</param>
        public GetGeneralLedgerHandler(IReportQueryService queryService)
        {
            _queryService = queryService;
        }

        /// <summary>
        /// Xử lý request GetGeneralLedgerQuery.
        /// </summary>
        public async Task<List<GeneralLedgerDto>> Handle(
            GetGeneralLedgerQuery request,
            CancellationToken cancellationToken)
        {
            // Chuyển đổi các ngày đầu vào sang UTC để xử lý thống nhất.
            var startDateUtc = request.StartDate.ToUniversalTime();
            var endDateUtc = request.EndDate.ToUniversalTime();

            // Tính toán ngày kết thúc độc quyền (exclusiveEndDate) để đảm bảo 
            // truy vấn bao gồm toàn bộ ngày cuối cùng được người dùng chọn.
            // Ví dụ: Nếu EndDate là 2025-11-30, exclusiveEndDate sẽ là 2025-12-01 00:00:00 UTC.
            var exclusiveEndDateUtc = endDateUtc.Date.AddDays(1);

            // Gọi dịch vụ truy vấn, truyền các tham số lọc (bao gồm AccountNumber)
            var result = await _queryService.GetGeneralLedgerEntries(
                startDateUtc, 
                exclusiveEndDateUtc,
                request.AccountNumber, 
                cancellationToken);

            return result;
        }
    }
}