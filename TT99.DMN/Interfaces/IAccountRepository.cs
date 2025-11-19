using TT99.DMN.Ents;

public interface IAccountRepository
{
    Task<bool> ExistsAsync(string accountNumber);
    Task AddAsync(Account account, CancellationToken token);
}
