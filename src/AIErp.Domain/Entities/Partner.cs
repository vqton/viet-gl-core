using AIErp.Domain.Enums;

namespace AIErp.Domain.Entities;

public class Partner
{
    public Guid Id { get; private set; }
    public string Code { get; private set; } = string.Empty;
    public string Name { get; private set; } = string.Empty;
    public PartnerType Type { get; private set; }
    public string? TaxCode { get; private set; }
    public string? Phone { get; private set; }
    public string? Email { get; private set; }
    public string? Address { get; private set; }
    public bool IsActive { get; private set; }
    public bool IsSystem { get; private set; }
    
    public DateTime CreatedAt { get; private set; }
    public string CreatedBy { get; private set; } = string.Empty;
    public DateTime LastModifiedAt { get; private set; }
    public string LastModifiedBy { get; private set; } = string.Empty;

    private Partner() { }

    public static Partner Create(
        string code,
        string name,
        PartnerType type,
        string createdBy,
        string? taxCode = null,
        string? phone = null,
        string? email = null,
        string? address = null,
        bool isSystem = false)
    {
        if (string.IsNullOrWhiteSpace(code))
            throw new ArgumentException("Code is required", nameof(code));
        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Name is required", nameof(name));

        var partner = new Partner
        {
            Id = Guid.NewGuid(),
            Code = code.Trim(),
            Name = name.Trim(),
            Type = type,
            TaxCode = taxCode?.Trim(),
            Phone = phone?.Trim(),
            Email = email?.Trim(),
            Address = address?.Trim(),
            IsActive = true,
            IsSystem = isSystem,
            CreatedAt = DateTime.UtcNow,
            CreatedBy = createdBy,
            LastModifiedAt = DateTime.UtcNow,
            LastModifiedBy = createdBy
        };

        return partner;
    }

    public void Update(
        string name,
        PartnerType type,
        string modifiedBy,
        string? taxCode = null,
        string? phone = null,
        string? email = null,
        string? address = null)
    {
        if (IsSystem)
            throw new InvalidOperationException($"Cannot modify system partner {Code} ({Name}).");

        if (string.IsNullOrWhiteSpace(name))
            throw new ArgumentException("Name is required", nameof(name));

        Name = name.Trim();
        Type = type;
        TaxCode = taxCode?.Trim();
        Phone = phone?.Trim();
        Email = email?.Trim();
        Address = address?.Trim();
        LastModifiedAt = DateTime.UtcNow;
        LastModifiedBy = modifiedBy;
    }

    public void Deactivate(string modifiedBy)
    {
        if (IsSystem)
            throw new InvalidOperationException($"Cannot deactivate system partner {Code} ({Name}).");

        IsActive = false;
        LastModifiedAt = DateTime.UtcNow;
        LastModifiedBy = modifiedBy;
    }

    public void Activate(string modifiedBy)
    {
        if (IsSystem)
            throw new InvalidOperationException($"Cannot activate system partner {Code} ({Name}).");

        IsActive = true;
        LastModifiedAt = DateTime.UtcNow;
        LastModifiedBy = modifiedBy;
    }
}
