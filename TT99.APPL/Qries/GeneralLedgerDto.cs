using System;

namespace TT99.APPL.Qries
{
    /// <summary>
    /// Data Transfer Object cho mỗi dòng dữ liệu trong Báo cáo Sổ Cái (General Ledger).
    /// </summary>
    public class GeneralLedgerDto
    {
        public DateTime Date { get; set; }
        public Guid ReferenceId { get; set; }
        public string AccountNumber { get; set; } = string.Empty;
        public string AccountName { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public decimal Debit { get; set; }
        public decimal Credit { get; set; }
    }
}