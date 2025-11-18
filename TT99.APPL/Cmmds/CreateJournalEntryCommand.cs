using System;
using System.Collections.Generic;
using MediatR;
using System.ComponentModel.DataAnnotations;

namespace TT99.APPL.Cmmds
{
    // Cấu trúc cho mỗi dòng bút toán (Debit/Credit)
    public class JournalEntryLineCommand
    {
        // Fix warning CS8618 bằng cách dùng 'required'
        [Required]
        public required string AccountNumber { get; set; }
        
        // Fix warning CS8618 bằng cách dùng 'required'
        [Required]
        public required string Description { get; set; }
        
        public decimal Debit { get; set; }
        public decimal Credit { get; set; }
    }

    // Command chính
    public class CreateJournalEntryCommand : IRequest<Guid>
    {
        // Fix warning CS8618 bằng cách dùng 'required'
        [Required]
        public required string VoucherNumber { get; set; }
        
        public required DateTime TransactionDate { get; set; } = DateTime.Now;
        
        // Fix warning CS8618 bằng cách dùng 'required'
        [Required]
        public required string Narration { get; set; }

        // Fix warning CS8618 bằng cách dùng 'required'
        [Required]
        public required List<JournalEntryLineCommand> Entries { get; set; } = new List<JournalEntryLineCommand>();
    }
}