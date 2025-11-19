// File: TT99.APPL/Cmmds/UpdateAccountCommand.cs
using MediatR;
using TT99.DMN.Ents;

namespace TT99.APPL.Cmmds
{
    public class UpdateAccountCommand : IRequest
    {
        public string AccountNumber { get; set; } = string.Empty;
        public string? AccountName { get; set; }
        public AccountType? Type { get; set; }
        public int? Level { get; set; }
        public string? ParentAccountNumber { get; set; }
    }
}
