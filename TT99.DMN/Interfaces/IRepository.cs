using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;

namespace TT99.DMN.Interfaces
{
    /// <summary>
    /// Generic repository interface (async) cho các entity.
    /// </summary>
    public interface IRepository<T> where T : class
    {
        Task AddAsync(T entity, CancellationToken cancellationToken = default);
        Task UpdateAsync(T entity, CancellationToken cancellationToken = default);
        Task RemoveAsync(T entity, CancellationToken cancellationToken = default);
        Task<T?> GetByIdAsync(Guid id, CancellationToken cancellationToken = default);
        Task<IEnumerable<T>> GetAllAsync(CancellationToken cancellationToken = default);
    }
}
