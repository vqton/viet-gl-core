using AIErp.Domain.Enums;

namespace AIErp.Domain.Entities;

public class Account
{
    public Guid Id { get; private set; }
    public string Code { get; private set; } = string.Empty;
    public string Name { get; private set; } = string.Empty;
    public AccountType Type { get; private set; }
    public NormalBalance NormalBalance { get; private set; }
    public bool IsDetail { get; private set; }
    public Guid? ParentId { get; private set; }
    public bool IsActive { get; private set; }
    public bool IsSystem { get; private set; }
    public string? Description { get; private set; }
    
    public DateTime CreatedAt { get; private set; }
    public string CreatedBy { get; private set; } = string.Empty;
    public DateTime LastModifiedAt { get; private set; }
    public string LastModifiedBy { get; private set; } = string.Empty;

    public Account? Parent { get; private set; }
    public ICollection<Account> Children { get; private set; } = new List<Account>();

    private Account() { }

    public static Account Create(
        string code,
        string name,
        AccountType type,
        NormalBalance normalBalance,
        bool isDetail,
        Guid? parentId,
        string createdBy,
        string? description = null,
        bool isSystem = false)
    {
        if (string.IsNullOrWhiteSpace(code))
            throw new ArgumentException("Code is required", nameof(code));
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Name is required", nameof(name));

        var account = new Account
        {
            Id = Guid.NewGuid(),
            Code = code.Trim(),
            Name = name.Trim(),
            Type = type,
            NormalBalance = normalBalance,
            IsDetail = isDetail,
            ParentId = parentId,
            IsActive = true,
            IsSystem = isSystem,
            Description = description?.Trim(),
            CreatedAt = DateTime.UtcNow,
            CreatedBy = createdBy,
            LastModifiedAt = DateTime.UtcNow,
            LastModifiedBy = createdBy
        };

        return account;
    }

    public void Update(string name, string? description, string modifiedBy)
    {
        if (IsSystem)
            throw new InvalidOperationException($"Cannot modify system account {Code} ({Name}).");

        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Name is required", nameof(name));

        Name = name.Trim();
        Description = description?.Trim();
        LastModifiedAt = DateTime.UtcNow;
        LastModifiedBy = modifiedBy;
    }

    public void Deactivate(string modifiedBy)
    {
        if (IsSystem)
            throw new InvalidOperationException($"Cannot deactivate system account {Code} ({Name}).");

        IsActive = false;
        LastModifiedAt = DateTime.UtcNow;
        LastModifiedBy = modifiedBy;
    }

    public void Activate(string modifiedBy)
    {
        if (IsSystem)
            throw new InvalidOperationException($"Cannot activate system account {Code} ({Name}).");

        IsActive = true;
        LastModifiedAt = DateTime.UtcNow;
        LastModifiedBy = modifiedBy;
    }

    public bool IsLeaf => !IsDetail && !Children.Any();

    public bool CanPost()
    {
        if (!IsActive)
            return false;
        if (!IsDetail)
            return false;
        return true;
    }

    public void ValidateForPosting()
    {
        if (!CanPost())
            throw new InvalidOperationException($"Account {Code} ({Name}) is a parent account and cannot be posted to directly.");
    }

    public static void ValidateCode(string code)
    {
        if (string.IsNullOrWhiteSpace(code))
            throw new ArgumentException("Account code is required", nameof(code));

        code = code.Trim();

        if (code.Length < 3 || code.Length > 10)
            throw new ArgumentException("Account code must be between 3 and 10 characters", nameof(code));

        if (!code.All(c => char.IsDigit(c)))
            throw new ArgumentException("Account code must contain only digits", nameof(code));
    }
}
