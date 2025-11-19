// File: D:\tt99acct\TT99.APPL\Cmmds\LockPeriodHandler.cs
using MediatR;
using System;
using System.Threading;
using System.Threading.Tasks;
using TT99.DMN.Interfaces;

namespace TT99.APPL.Cmmds
{
    // Cập nhật interface để chỉ định TResponse là Unit
    public class LockPeriodHandler : IRequestHandler<LockPeriodCommand, Unit>
    {
        private readonly IAccountingPeriodRepository _periodRepository;

        public LockPeriodHandler(IAccountingPeriodRepository periodRepository)
        {
            _periodRepository = periodRepository;
        }

        // Cập nhật phương thức Handle để trả về Task<Unit>
        public async Task<Unit> Handle(LockPeriodCommand request, CancellationToken cancellationToken)
        {
            var period = await _periodRepository.GetByIdAsync(request.PeriodId, cancellationToken);

            if (period == null)
            {
                throw new InvalidOperationException($"Kỳ kế toán với ID {request.PeriodId} không tồn tại.");
            }

            period.Lock(); // Gọi phương thức trong Entity

            await _periodRepository.UpdateAsync(period, cancellationToken);

            return Unit.Value; // Trả về Unit.Value
        }
    }
}