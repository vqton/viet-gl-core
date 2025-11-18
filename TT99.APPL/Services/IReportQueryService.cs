using TT99.APPL.Qries;

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
                        string? accountNumber, // ĐÃ THÊM: tham số lọc tài khoản (nullable string)
            CancellationToken cancellationToken);
    }
}