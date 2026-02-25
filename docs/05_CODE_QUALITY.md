# Code Quality Standards - AIErp

## Overview
- This document defines code quality standards for the AIErp project.
- Target: .NET 9, C# 13, PostgreSQL, Clean Lite Architecture.
- Goal: Maintainability, security, and financial accuracy.

---

## 1. Naming Conventions

### 1.1 General Rules

| Element | Convention | Example |
|---------|------------|---------|
| Classes/Interfaces | PascalCase | `JournalEntry`, `IVoucherRepository` |
| Methods/Properties | PascalCase | `CheckBalance()`, `TotalDebit` |
| Private Fields | _camelCase | `_journalItems`, `_currentPeriod` |
| Constants | PascalCase | `DefaultCurrency`, `MaxLineCount` |
| Parameters | camelCase | `entryDate`, `createdBy` |
| Local Variables | camelCase | `debitTotal`, `isValid` |
| Files | Match class name | `JournalEntry.cs` |

### 1.2 Good vs Bad Examples

**Bad (❌)**
```csharp
public class journal_entry {
    public Guid id;
    public string entry_number;  // snake_case
    decimal total;               // no modifier, unclear
    decimal _amount;             // inconsistent prefix
    
    void checkbalance() { }      // camelCase method
}
```

**Good (✅)**
```csharp
public class JournalEntry
{
    public Guid Id { get; private set; }
    public string EntryNumber { get; private set; }
    private decimal _totalDebit;
    
    public bool CheckBalance() { }  // PascalCase
}
```

---

## 2. Clean Lite Architecture Rules

### 2.1 Domain Layer - Zero Dependencies

The Domain layer must have **ZERO** external dependencies:
- No Entity Framework
- No JSON serialization libraries
- No database connections
- No HTTP clients
- Only .NET built-in types

**Bad (❌)** - Domain referencing EF
```csharp
// AIErp.Domain/Entities/JournalEntry.cs
using Microsoft.EntityFrameworkCore;  // FORBIDDEN

public class JournalEntry {
    public int Id { get; set; }
}
```

**Good (✅)** - Pure C# Domain
```csharp
// AIErp.Domain/Entities/JournalEntry.cs
using System;
using System.Collections.Generic;
using System.Linq;

namespace AIErp.Domain.Entities;

public class JournalEntry
{
    public Guid Id { get; private set; }
    public decimal TotalDebit { get; private set; }
    // Pure C# - no external dependencies
}
```

### 2.2 Explicit Over Implicit

Always prefer explicit types over `var` when the type is not obvious.

**Bad (❌)**
```csharp
var result = CalculateTotal(debits, credits);
var items = GetJournalItems();
var amount = 1000;  // decimal? int?
```

**Good (✅)**
```csharp
decimal result = CalculateTotal(debits, credits);
IReadOnlyCollection<JournalItem> items = GetJournalItems();
decimal amount = 1000m;  // explicit decimal with m suffix
int count = items.Count;  // obvious from right side
```

**Exception**: `var` is acceptable when type is obvious from right side:
```csharp
var account = new Account();           // obvious
var status = VoucherStatus.Draft;     // obvious
var items = new List<JournalItem>();  // obvious
```

### 2.3 Dependency Direction

```
Domain ← Application ← Infrastructure
```

- Domain defines interfaces (e.g., `IVoucherRepository`)
- Application implements business logic
- Infrastructure implements repositories, DB access

---

## 3. Financial Accuracy

### 3.1 Money Type Rules

| Rule | Requirement |
|------|-------------|
| Always use `decimal` | Never use `double` or `float` for money |
| Suffix `m` for literals | `1000m` not `1000` |
| Use Money value object | Encapsulate amount + currency |

**Bad (❌)**
```csharp
public double Amount { get; set; }      // double is imprecise
decimal amount = 1000;                  // defaults to decimal but unclear
amount = 1000.99;                       // implicit double possible
```

**Good (✅)**
```csharp
public decimal Amount { get; private set; }  // explicit decimal
decimal amount = 1000m;                       // clear suffix

// Using Money value object
public Money TotalDebit { get; private set; }
```

### 3.2 Rounding Rules

- **Banker's Rounding** (Round half to even) for general calculations
- **Round to 4 decimal places** for exchange rates
- **Round to 0 decimal places** for VND currency
- **Always specify rounding explicitly**

**Bad (❌)**
```csharp
decimal result = amount * rate;  // implicit rounding
decimal total = 100m / 3m;       // infinite decimal
```

**Good (✅)**
```csharp
// Exchange rate calculation (4 decimals)
decimal exchangeRate = Math.Rate(1234.5678m, 4, MidpointRounding.AwayFromZero);

// VND total (0 decimals)
decimal vndTotal = Math.Round(amount, 0, MidpointRounding.AwayFromZero);

// Using Money value object with built-in rounding
public static Money operator +(Money left, Money right)
{
    if (left.Currency != right.Currency)
        throw new InvalidOperationException("Currency mismatch");
    
    decimal result = Math.Round(left.Amount + right.Amount, 4);
    return new Money(result, left.Currency);
}
```

### 3.3 Precision Standards

| Field Type | Precision | Example |
|------------|-----------|---------|
| Money/Amount | NUMERIC(20,4) | `12345678901234.5678` |
| Exchange Rate | NUMERIC(18,6) | `24567.123456` |
| Quantity | NUMERIC(18,3) | `123456.789` |
| Percentage | NUMERIC(5,2) | `99.99` |

---

## 4. Error Handling

### 4.1 No Silent Failures

Never swallow exceptions or return null without indication.

**Bad (❌)**
```csharp
public decimal? GetAmount() {
    try {
        return Calculate();
    } catch {
        return null;  // Silent failure
    }
}

public void Post() {
    if (!IsValid) return;  // Silent failure - caller doesn't know
}
```

**Good (✅)**
```csharp
public Money GetAmount()
{
    try
    {
        return Calculate();
    }
    catch (CalculationException ex)
    {
        throw new InvalidOperationException($"Failed to calculate amount: {ex.Message}", ex);
    }
}

public Result Post()
{
    if (!IsValid)
        return Result.Fail("Entry is not valid for posting");
    
    // ... post logic
    return Result.Success();
}
```

### 4.2 Custom Domain Exceptions

Define specific exceptions for domain errors.

```csharp
// Domain/Exceptions/DomainErrors.cs

public class ImbalanceDetectedError : Exception
{
    public decimal DebitTotal { get; }
    public decimal CreditTotal { get; }
    public decimal Difference => DebitTotal - CreditTotal;

    public ImbalanceDetectedError(decimal debit, decimal credit)
        : base($"Entry is not balanced. Debit: {debit:N4}, Credit: {credit:N4}, Diff: {debit - credit:N4}")
    {
        DebitTotal = debit;
        CreditTotal = credit;
    }
}

public class FiscalPeriodClosedError : Exception
{
    public Guid PeriodId { get; }
    public DateOnly Date { get; }

    public FiscalPeriodClosedError(Guid periodId, DateOnly date)
        : base($"Fiscal period {periodId} is closed. Cannot post for date {date}")
    {
        PeriodId = periodId;
        Date = date;
    }
}

public class InvalidStatusTransitionError : Exception
{
    public VoucherStatus Current { get; }
    public VoucherStatus Attempted { get; }

    public InvalidStatusTransitionError(VoucherStatus current, VoucherStatus attempted)
        : base($"Cannot transition from {current} to {attempted}")
    {
        Current = current;
        Attempted = attempted;
    }
}
```

### 4.3 Standard API Error Response

All API errors must follow a consistent format.

```csharp
// Application/DTOs/ErrorResponse.cs

public record ErrorResponse(
    int StatusCode,
    string ErrorCode,
    string Message,
    Dictionary<string, string>? Details = null,
    DateTime Timestamp = default
)
{
    public ErrorResponse() : this(0, "", "", null, DateTime.UtcNow) { }
}

// Example JSON response
{
    "statusCode": 400,
    "errorCode": "IMBALANCE_DETECTED",
    "message": "Entry is not balanced. Debit: 1000.0000, Credit: 950.0000, Diff: 50.0000",
    "details": {
        "totalDebit": "1000.0000",
        "totalCredit": "950.0000"
    },
    "timestamp": "2025-01-15T10:30:00Z"
}
```

### 4.4 Result Pattern for Operations

Use Result pattern for operations that can fail.

```csharp
// Application/Results/Result.cs

public struct Result
{
    public bool IsSuccess { get; }
    public bool IsFailure => !IsSuccess;
    public string Error { get; }

    private Result(bool isSuccess, string error)
    {
        IsSuccess = isSuccess;
        Error = error;
    }

    public static Result Success() => new(true, "");
    public static Result Fail(string error) => new(false, error);
}

public struct Result<T>
{
    public bool IsSuccess { get; }
    public bool IsFailure => !IsSuccess;
    public T? Value { get; }
    public string Error { get; }

    private Result(bool isSuccess, T value, string error)
    {
        IsSuccess = isSuccess;
        Value = value;
        Error = error;
    }

    public static Result<T> Success(T value) => new(true, value, "");
    public static Result<T> Fail(string error) => new(false, default, error);
}
```

---

## 5. Code Organization

### 5.1 File Structure

```
src/AIErp.Domain/
├── Entities/
│   └── JournalEntry.cs
├── ValueObjects/
│   └── Money.cs
├── Enums/
│   └── VoucherStatus.cs
├── Interfaces/
│   └── IJournalEntryRepository.cs
└── Exceptions/
    └── DomainErrors.cs
```

### 5.2 Class Organization Order

1. Fields (private)
2. Properties (public)
3. Constructors (static factory, then instance)
4. Public methods
5. Private methods

---

## 6. Testing Standards

### 6.1 Test Naming

```
{MethodName}_{Scenario}_{ExpectedResult}
```

Examples:
- `CheckBalance_WhenBalanced_ReturnsTrue`
- `Post_WhenPeriodClosed_ThrowsFiscalPeriodClosedError`
- `AddItem_WhenNotDraft_ThrowsInvalidStatusTransitionError`

### 6.2 Arrange-Act-Assert Pattern

```csharp
[Fact]
public void CheckBalance_WhenBalanced_ReturnsTrue()
{
    // Arrange
    var entry = JournalEntry.Create(
        DateOnly.FromDateTime(DateTime.Today),
        Guid.NewGuid(),
        "VND",
        "Test entry",
        "testuser"
    );
    entry.AddItem(JournalItem.Create(accountId: Guid.NewGuid(), 1000m, 0, "user"));
    entry.AddItem(JournalItem.Create(accountId: Guid.NewGuid(), 0, 1000m, "user"));
    
    // Act
    bool result = entry.CheckBalance();
    
    // Assert
    Assert.True(result);
}
```

---

## 7. Security Standards

### 7.1 Input Validation

- Always validate inputs at API boundary
- Use FluentValidation in Application layer
- Domain entities validate business rules

### 7.2 Sensitive Data

- Never log sensitive data (passwords, tokens, financial details)
- Use masking for display
- Store hashes, not plain text

---

## 8. Summary Checklist

| Category | Rule |
|----------|------|
| **Naming** | PascalCase classes/methods, _camelCase private fields |
| **Architecture** | Domain = Zero dependencies |
| **Financial** | Always decimal, explicit rounding |
| **Errors** | No silent failures, custom exceptions, Result pattern |
| **API** | Standard error response format |
| **Tests** | Descriptive names, Arrange-Act-Assert |
| **Security** | No secrets in logs, validate inputs |
