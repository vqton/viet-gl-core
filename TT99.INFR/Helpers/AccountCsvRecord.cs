// File: D:\tt99acct\TT99.INFR\Helpers\SeedData\AccountCsvRecord.cs
namespace TT99.INFR.Helpers.SeedData
{
    public class AccountCsvRecord
    {
        public string AccountNumber { get; set; } = string.Empty;
        public string AccountName { get; set; } = string.Empty;
        public string Type { get; set; } = string.Empty; // This will be parsed into AccountType
    }
}