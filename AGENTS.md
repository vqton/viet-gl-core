# AGENTS.md

## Overview
- This file provides guidance for agentic contributors working in this repository.
- It covers build, lint, test commands, code style guidelines, and project-specific rules.
- Project: AIErp - In-house ERP Core (Accounting) for SME
- Stack: .NET 9, C# 13, Clean Lite Architecture (Domain, Application, Infrastructure)
- Database: SQLite (for dev), PostgreSQL (for production)
- Compliance: Circular 99/2025/TT-BTC (Vietnam)

## 1) Build / Lint / Test Workflow

### Setup
- Install .NET 9 SDK from https://dotnet.microsoft.com/download
- Restore dependencies: `dotnet restore`
- Build solution: `dotnet build`

### Commands to Run
- Build: `dotnet build`
- Run all tests: `dotnet test`
- Run a single test: `dotnet test --filter "FullyQualifiedName~TestClassName.TestMethodName"`
- Run tests with coverage: `dotnet test --collect:"XPlat Code Coverage"`
- Clean build: `dotnet clean && dotnet build`
- Format code: `dotnet format`

### Single Test Examples
- `dotnet test --filter "FullyQualifiedName~JournalEntryTests.CheckBalance"`
- `dotnet test --filter "FullyQualifiedName~JournalEntryTests.CheckBalance_ShouldThrowWhenImbalanced"`
- `dotnet test --filter "Name~Balance"` (partial match)
- Run tests without building first: `dotnet test --no-build`

### Database Migrations
- Create migration: `dotnet ef migrations add <Name> -p src/AIErp.Infrastructure -s src/AIErp.WebAPI`
- Apply migrations: `dotnet ef database update -p src/AIErp.Infrastructure -s src/AIErp.WebAPI`
- Remove last migration: `dotnet ef migrations remove -p src/AIErp.Infrastructure -s src/AIErp.WebAPI`

## 2) Project Structure

```
src/
├── AIErp.Domain/          # Pure C#, No external libs (Clean Lite)
│   ├── Entities/          # Account, JournalEntry, JournalItem, Partner, FiscalPeriod
│   ├── Enums/             # VoucherStatus (Draft=1, Posted=2, Void=3), AccountType, NormalBalance, PartnerType
│   └── ValueObjects/      # Money
├── AIErp.Application/     # Use Cases (Commands/Queries)
│   ├── DTOs/              # JournalEntryDto, JournalEntryResultDto
│   ├── Interfaces/        # IJournalEntryService
│   ├── Services/          # JournalEntryService
│   └── Exceptions/        # BusinessException
├── AIErp.Infrastructure/  # DB Layer
│   ├── Persistence/       # AppDbContext
│   └── DependencyInjection.cs
└── AIErp.WebAPI/         # REST API
    ├── Controllers/       # JournalEntriesController
    └── appsettings.json   # SQLite: "Data Source=AIErp.db"

tests/
└── AIErp.Domain.Tests/   # Unit tests (xUnit)
    └── JournalEntryTests.cs
```

## 3) Code Style Guidelines

### General
- Follow Clean Lite: Domain = Pure C#, Application = Services, Infrastructure = DB/IO
- No logic in Controllers, no DB logic in Domain
- Keep entities as POCOs (no [Key], [Required] attributes in Domain)
- Domain entities should have zero external dependencies

### Naming Conventions
- Classes/Interfaces: PascalCase (e.g., `JournalEntry`, `IVoucherRepository`)
- Methods/Properties: PascalCase
- Private fields: _camelCase (e.g., `_journalItems`, `_dbContext`)
- Constants: PascalCase (e.g., `DefaultCurrency`)
- Files: Match class name (e.g., `JournalEntry.cs`)
- Test classes: `{EntityName}Tests` (e.g., `JournalEntryTests`)
- Test methods: `{MethodName}_Should{ExpectedBehavior}` (e.g., `CheckBalance_ShouldThrowWhenImbalanced`)

### Formatting
- Use dotnet format: `dotnet format`
- Braces on new line for classes/methods
- One space after keywords (if, for, while)
- Use expression-bodied members when appropriate
- 120 char line length max
- Use trailing commas in multi-line initializers

### Typing
- Use C# 13 features: primary constructors, collection expressions
- Enable nullable reference types
- Use `record` for immutable value objects
- Avoid `var` for primitive types; use explicit types
- Use `decimal` for money/financial calculations

### Imports
- Group: System → Microsoft → Third-party → Project
- Remove unused imports
- Use global usings in `GlobalUsings.cs`

### Error Handling
- Throw specific exceptions (ArgumentException, InvalidOperationException)
- Never swallow exceptions silently
- Use domain errors: ImbalanceDetectedError, FiscalPeriodClosedError, InvalidStatusTransitionError
- Use BusinessException for domain rule violations

### Logging
- Use ILogger<T> from Microsoft.Extensions.Logging
- Log at appropriate levels: LogInformation, LogWarning, LogError

### Documentation
- XML doc comments for public APIs
- Summary: one-line description
- Params: describe parameters
- Returns: describe return value
- Example: `<summary>Creates a new journal entry.</summary>`

## 4) Domain Layer Rules

- Pure C# - no EF, no JSON, no external dependencies
- Entities: Account, JournalEntry, JournalItem, Partner, FiscalPeriod
- Enums: VoucherStatus (Draft=1, Posted=2, Void=3), AccountType, NormalBalance, PartnerType
- Value Objects: Money (immutable, currency validation)
- Validation inside entities (e.g., `JournalEntry.CheckBalance()`)
- Use factory methods for entity creation

## 5) Testing Guidelines

- Tests live in `tests/` folder
- Naming: `{EntityName}Tests.cs`
- Use xUnit (required) + FluentAssertions (recommended)
- Test patterns:
  - Arrange: Create entity with factory methods
  - Act: Call domain method
  - Assert: Verify state changes or exceptions
- Test invariants: balance check, status transitions, validation
- All domain tests should pass without database

## 6) API Guidelines

### JSON Serialization
- Enums as strings: Use `JsonStringEnumConverter`
- DefaultIgnoreCondition: WhenWritingNull
- PropertyNamingPolicy: null (PascalCase)

### Controller Pattern
```csharp
[ApiController]
[Route("api/v1/[controller]")]
public class JournalEntriesController(IJournalEntryService service) : ControllerBase
{
    // Use primary constructor injection
    // Return IActionResult with proper response envelope
}
```

### Response Envelope
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2026-02-25T00:00:00Z"
}
```

## 7) Git Workflow

### Branching
- `feature/description` - new features
- `fix/description` - bug fixes
- `docs/description` - documentation

### Commit Messages
- Format: `type(scope): description`
- Examples:
  - `feat(domain): add CheckBalance method to JournalEntry`
  - `fix: correct off-by-one in balance calculation`
  - `docs: update data dictionary with new fields`
  - `chore(db): switch from PostgreSQL to SQLite`

### Pull Requests
- Keep PRs small and focused
- Include tests for new functionality
- Update documentation if needed

## 8) Security

- Never commit secrets, credentials, or keys
- Use environment variables for sensitive config
- Connection strings in appsettings.*.json should be placeholder
- Add sensitive files to .gitignore

## 9) Cursor / Copilot Rules

- No Cursor rules present in .cursor/
- No Copilot rules in .github/copilot-instructions.md
- Follow standard Clean Architecture principles
- Always use Clean Lite Architecture (Domain = Pure C#)

## 10) Notes

- This is a living document - update as the project evolves
- Refer to docs/01_DOMAIN_LOGIC.md for business rules
- Refer to docs/02_LITE_ARCHITECTURE.md for architecture details
- Refer to docs/03_DATA_DICTIONARY.md for database schema
- Database file: `AIErp.db` in WebAPI project directory (SQLite)
- API runs on http://localhost:5279 (development)
