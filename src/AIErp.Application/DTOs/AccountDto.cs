namespace AIErp.Application.DTOs;

using AIErp.Domain.Enums;

public class AccountDto
{
    public Guid Id { get; set; }
    public string Code { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public AccountType Type { get; set; }
    public NormalBalance NormalBalance { get; set; }
    public bool IsDetail { get; set; }
    public Guid? ParentId { get; set; }
    public bool IsActive { get; set; }
    public string? Description { get; set; }
}

public class AccountTreeDto : AccountDto
{
    public List<AccountTreeDto> Children { get; set; } = new();
}

public class CreateAccountDto
{
    public string Code { get; set; } = string.Empty;
    public string Name { get; set; } = string.Empty;
    public AccountType Type { get; set; }
    public NormalBalance NormalBalance { get; set; }
    public bool IsDetail { get; set; }
    public Guid? ParentId { get; set; }
    public string? Description { get; set; }
}

public class UpdateAccountDto
{
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
}
