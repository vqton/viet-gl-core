// File: D:\tt99acct\TT99.INFR\Helpers\SeedDataHelper.cs
using System.Globalization; // Often needed for CsvHelper
using System.Reflection;   // For getting the assembly location
using CsvHelper;           // <-- Add this line
using TT99.DMN.Ents;

namespace TT99.INFR.Helpers
{
    public static class SeedDataHelper
    {
        public static List<Account> ReadAccountsFromCsv(string csvFilePath)
        {
            var accounts = new List<Account>();

            var assemblyLocation = Assembly.GetExecutingAssembly().Location;
            var assemblyDirectory = Path.GetDirectoryName(assemblyLocation);
            var fullPath = Path.Combine(assemblyDirectory ?? "", csvFilePath);

            using var reader = new StreamReader(fullPath);
            using var csv = new CsvReader(reader, CultureInfo.InvariantCulture); // CsvReader should now be recognized

            // Read the header row
            csv.Read();
            csv.ReadHeader();

            while (csv.Read())
            {
                if (Enum.TryParse<AccountType>(csv.GetField("Type"), ignoreCase: true, out var accountType))
                {
                    var account = new Account(
                        csv.GetField("AccountNumber") ?? throw new InvalidOperationException("AccountNumber cannot be null in CSV."),
                        csv.GetField("AccountName") ?? throw new InvalidOperationException("AccountName cannot be null in CSV."),
                        accountType
                    );
                    accounts.Add(account);
                }
                else
                {
                    Console.WriteLine($"Warning: Invalid AccountType '{csv.GetField("Type")}' in CSV for AccountNumber {csv.GetField("AccountNumber")}. Skipping.");
                }
            }

            return accounts;
        }
    }
}