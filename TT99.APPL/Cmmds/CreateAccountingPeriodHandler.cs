// File: D:\tt99acct\TT99.APPL\Cmmds\CreateAccountingPeriodHandler.cs
using MediatR;
using System;
using System.Threading;
using System.Threading.Tasks;
using TT99.DMN.Ents;
using TT99.DMN.Interfaces;

namespace TT99.APPL.Cmmds
{
    public class CreateAccountingPeriodHandler : IRequestHandler<CreateAccountingPeriodCommand, Guid>
    {
        private readonly IAccountingPeriodRepository _periodRepository;

        public CreateAccountingPeriodHandler(IAccountingPeriodRepository periodRepository)
        {
            _periodRepository = periodRepository;
        }

        public async Task<Guid> Handle(CreateAccountingPeriodCommand request, CancellationToken cancellationToken)
        {
            // (Tùy chọn) Thêm logic kiểm tra trùng lặp ngày với các kỳ khác ở đây nếu cần

            var period = new AccountingPeriod(request.Name, request.StartDate, request.EndDate);

            await _periodRepository.AddAsync(period, cancellationToken);

            // Không cần gọi _context.SaveChangesAsync() ở đây vì MediatR Handler sẽ không trực tiếp xử lý DbContext
            // Việc lưu sẽ do một service hoặc một handler khác (hoặc một pipeline behavior) thực hiện sau.
            // Tuy nhiên, trong kiến trúc hiện tại, Repository có thể phụ thuộc vào DbContext.
            // Cách tiếp cận tốt hơn là có một Application Service riêng cho việc này.
            // Nhưng để đơn giản cho bước hiện tại, ta giả định service sẽ lưu sau.

            return period.Id;
        }
    }
}