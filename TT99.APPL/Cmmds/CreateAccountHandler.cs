// File: D:\tt99acct\TT99.APPL\Cmmds\CreateAccountHandler.cs
using MediatR;
using System;
using System.Threading;
using System.Threading.Tasks;
using TT99.DMN.Ents;
using TT99.DMN.Interfaces;  // Inject interface, not DbContext


namespace TT99.APPL.Cmmds
{
    public class CreateAccountHandler : IRequestHandler<CreateAccountCommand, string>
    {
        private readonly IAccountRepository _accountRepo;
        private readonly IUnitOfWork _uow;

        public CreateAccountHandler(IAccountRepository accountRepo, IUnitOfWork uow)
        {
            _accountRepo = accountRepo;
            _uow = uow;
        }

        public async Task<string> Handle(CreateAccountCommand request, CancellationToken cancellationToken)
        {
            // Kiểm tra tồn tại
            if (await _accountRepo.ExistsAsync(request.AccountNumber))
                throw new InvalidOperationException($"Tài khoản '{request.AccountNumber}' đã tồn tại.");

            // Kiểm tra parent
            if (!string.IsNullOrEmpty(request.ParentAccountNumber))
            {
                if (!await _accountRepo.ExistsAsync(request.ParentAccountNumber))
                    throw new InvalidOperationException($"Tài khoản cha '{request.ParentAccountNumber}' không tồn tại.");
            }

            // Tạo entity
            var account = new Account(
                request.AccountNumber,
                request.AccountName,
                request.Type,
                request.Level,
                request.ParentAccountNumber
            );

            await _accountRepo.AddAsync(account, cancellationToken);
            await _uow.SaveChangesAsync(cancellationToken);

            return account.AccountNumber;
        }
    }
}   
