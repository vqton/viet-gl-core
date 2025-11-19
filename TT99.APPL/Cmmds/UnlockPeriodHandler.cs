// File: D:\tt99acct\TT99.APPL\Cmmds\UnlockPeriodHandler.cs
using MediatR;
using System;
using System.Threading;
using System.Threading.Tasks;
using TT99.DMN.Interfaces;

namespace TT99.APPL.Cmmds
{
    // Handler sẽ tự động nhận ra TResponse là Unit từ Command
    public class UnlockPeriodHandler : IRequestHandler<UnlockPeriodCommand, Unit> // Cập nhật interface
    {
        private readonly IAccountingPeriodRepository _periodRepository;

        public UnlockPeriodHandler(IAccountingPeriodRepository periodRepository)
        {
            _periodRepository = periodRepository;
        }

        // Cập nhật phương thức Handle để trả về Task<Unit>
        public async Task<Unit> Handle(UnlockPeriodCommand request, CancellationToken cancellationToken)
        {
            var period = await _periodRepository.GetByIdAsync(request.PeriodId, cancellationToken);

            if (period == null)
            {
                throw new InvalidOperationException($"Kỳ kế toán với ID {request.PeriodId} không tồn tại.");
            }

            period.Unlock(); // Gọi phương thức trong Entity

            await _periodRepository.UpdateAsync(period, cancellationToken);

            return Unit.Value; // Trả về Unit.Value
        }
    }
}