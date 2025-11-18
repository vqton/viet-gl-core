// File: D:\tt99acct\TT99.APPL\Cmmds\CreateJournalEntryHandler.cs
using MediatR;
using System;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using TT99.DMN.Ents;
using TT99.DMN.Interfaces;

namespace TT99.APPL.Cmmds
{
    /// <summary>
    /// Bộ xử lý (Handler) chịu trách nhiệm thực thi Command CreateJournalEntryCommand.
    /// </summary>
    public class CreateJournalEntryHandler : IRequestHandler<CreateJournalEntryCommand, Guid>
    {
        private readonly IJournalingService _journalingService;

        public CreateJournalEntryHandler(IJournalingService journalingService)
        {
            _journalingService = journalingService;
        }

        public async Task<Guid> Handle(CreateJournalEntryCommand request, CancellationToken cancellationToken)
        {
            // Kiểm tra tính hợp lệ của Request trước khi gọi Service (nếu cần)
            if (request.Entries == null || request.Entries.Count == 0)
            {
                throw new ArgumentException("Danh sách bút toán không được để trống.", nameof(request.Entries));
            }

            // CHUYỂN ĐỔI: Tạo đối tượng JournalEntry từ dữ liệu trong Command
            // Sử dụng constructor công khai
            var journalEntry = new JournalEntry(
                request.VoucherNumber,
                request.TransactionDate,
                request.Narration
            );

            // CHUYỂN ĐỔI: Thêm các dòng bút toán từ Command vào Entity
            foreach (var commandLine in request.Entries)
            {
                // Giả sử LedgerEntry có constructor phù hợp
                var ledgerEntry = new LedgerEntry(
                    commandLine.AccountNumber,
                    commandLine.Description,
                    commandLine.Debit,
                    commandLine.Credit
                );
                
                // Sử dụng phương thức AddEntry để thêm vào JournalEntry
                journalEntry.AddEntry(ledgerEntry);
            }

            // GỌI PHƯƠNG THỨC ASYNC ĐÃ ĐƯỢC TÍCH HỢP TỪ SERVICE
            var entryId = await _journalingService.CreateJournalEntryAsync(
                journalEntry, // ĐÃ SỬA: Truyền đối tượng JournalEntry đã được chuyển đổi và điền đầy đủ
                cancellationToken
            );

            return entryId;
        }
    }
}