// File: D:\tt99acct\TT99.APPL\Cmmds\CreateAccountingPeriodCommand.cs
using MediatR;
using System;
using System.ComponentModel.DataAnnotations;

namespace TT99.APPL.Cmmds
{
    public class CreateAccountingPeriodCommand : IRequest<Guid> // Trả về ID của kỳ vừa tạo
    {
        [Required]
        public required string Name { get; set; }
        
        public required DateTime StartDate { get; set; }
        
        public required DateTime EndDate { get; set; }
    }
}