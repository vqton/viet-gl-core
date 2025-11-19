// File: D:\tt99acct\TT99.APPL\Cmmds\LockPeriodCommand.cs
using MediatR; // Thêm using này nếu chưa có
using System;
using System.ComponentModel.DataAnnotations;

namespace TT99.APPL.Cmmds
{
    // Sửa: Implement IRequest<Unit> thay vì IRequest
    public class LockPeriodCommand : IRequest<Unit> 
    {
        [Required]
        public required Guid PeriodId { get; set; }
    }
}