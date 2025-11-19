// File: D:\tt99acct\TT99.APPL\Cmmds\CreateAccountCommand.cs
using MediatR;
using System.ComponentModel.DataAnnotations;
using TT99.DMN.Ents; // Để dùng AccountType

namespace TT99.APPL.Cmmds
{
    public class CreateAccountCommand : IRequest<string> // Trả về AccountNumber của tài khoản vừa tạo
    {
        [Required]
        public required string AccountNumber { get; set; }
        
        [Required]
        public required string AccountName { get; set; }
        
        [Required]
        public required AccountType Type { get; set; }

        public int Level { get; set; } = 1; // Mặc định là cấp 1

        public string? ParentAccountNumber { get; set; } // Có thể null nếu là cấp 1
    }
}