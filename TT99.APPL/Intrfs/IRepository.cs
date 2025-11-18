using System;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace TT99.APPL.Intrfs
{
    /// <summary>
    /// Giao diện Repository chung (Generic Repository) cho các Entity.
    /// Dùng cho việc trừu tượng hóa việc truy cập cơ sở dữ liệu.
    /// </summary>
    /// <typeparam name="TEntity">Loại Entity (ví dụ: JournalEntry, Account).</typeparam>
    public interface IRepository<TEntity> where TEntity : class
    {
        // Thêm một Entity mới vào ngữ cảnh (Chưa lưu vào DB)
        Task AddAsync(TEntity entity);

        // Lấy Entity theo ID (Asynchronous)
        Task<TEntity> GetByIdAsync(Guid id);

        // Lấy tất cả Entity
        Task<IEnumerable<TEntity>> GetAllAsync();

        // Cập nhật Entity
        void Update(TEntity entity);

        // Xóa Entity theo ID
        void Remove(TEntity entity);
    }
}