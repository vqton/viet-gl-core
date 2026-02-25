# Lite Architecture - Clean Architecture for .NET 9

## 1. Three-Layer Vision

```
┌─────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                    │
│         Use Cases / Commands / Queries / DTOs           │
├─────────────────────────────────────────────────────────┤
│                      DOMAIN LAYER                       │
│      Entities / Value Objects / Domain Services        │
│              (Pure C#, No External Libs)               │
├─────────────────────────────────────────────────────────┤
│                   INFRASTRUCTURE LAYER                  │
│      PostgreSQL / Controllers / External Services      │
└─────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Responsibility | Contains |
|-------|----------------|----------|
| **Domain** | Business rules, invariants, entities | Pure C#, no IO, no libs |
| **Application** | Use cases, orchestration, DTOs | Services, Commands, Queries |
| **Infrastructure** | DB access, HTTP, external systems | Repositories, Controllers, Adapters |

---

## 2. Folder Structure Map

```
viet-gl-core/
├── src/
│   ├── VietGl.Domain/           # Core business logic
│   │   ├── Entities/
│   │   │   ├── Voucher.cs
│   │   │   ├── VoucherLine.cs
│   │   │   ├── Account.cs
│   │   │   └── FiscalPeriod.cs
│   │   ├── ValueObjects/
│   │   │   ├── Money.cs
│   │   │   └── VoucherStatus.cs
│   │   ├── Interfaces/
│   │   │   ├── IVoucherRepository.cs
│   │   │   └── IFiscalPeriodRepository.cs
│   │   └── DomainServices/
│   │       └── VoucherValidationService.cs
│   │
│   ├── VietGl.Application/      # Use cases & orchestration
│   │   ├── Commands/
│   │   │   ├── CreateVoucherCommand.cs
│   │   │   ├── PostVoucherCommand.cs
│   │   │   └── VoidVoucherCommand.cs
│   │   ├── Queries/
│   │   │   └── GetVoucherByIdQuery.cs
│   │   ├── DTOs/
│   │   │   ├── VoucherDto.cs
│   │   │   └── VoucherLineDto.cs
│   │   └── Services/
│   │       └── VoucherService.cs
│   │
│   └── VietGl.Infrastructure/   # Data & External
│       ├── Data/
│       │   └── VietGlDbContext.cs
│       ├── Repositories/
│       │   ├── VoucherRepository.cs
│       │   └── FiscalPeriodRepository.cs
│       └── Controllers/
│           └── VouchersController.cs
│
└── tests/
    ├── VietGl.Domain.Tests/
    ├── VietGl.Application.Tests/
    └── VietGl.Infrastructure.Tests/
```

---

## 3. Key Principles

### 3.1 No Logic in Controllers
- Controllers are **entry points only**
- They only:
  - Receive HTTP requests
  - Map to commands/queries
  - Return responses
- **No business logic** in controllers

### 3.2 No DB Logic in Domain
- Domain entities are **POCOs** (Plain Old CLR Objects)
- No `[Key]`, `[Required]`, `[ForeignKey]` attributes
- No `DbContext` references
- Validation is **domain logic**, not database constraints

### 3.3 Dependency Rule
```
Domain ← Application ← Infrastructure
         (references)
```
- Domain has **zero dependencies**
- Application references Domain
- Infrastructure references Domain + Application

---

## 4. Evolutionary Path

### Phase 1: The House (Current)
```
Single Solution
├── VietGl.Domain (class library)
├── VietGl.Application (class library)
├── VietGl.Infrastructure (web API)
└── Tests
```
- Small team (1-3 developers)
- Monolithic deployment
- Basic CRUD + Posting workflow

### Phase 2: Townhouse (Growth)
```
Separate Solutions
├── VietGl.Domain (shared nuget)
├── VietGl.Accounting.Application
├── VietGl.Accounting.Api
├── VietGl.Reporting.Application
└── VietGl.Reporting.Api
```
- Multiple bounded contexts
- Shared domain via NuGet
- Team split by context

### Phase 3: Skyscraper (Enterprise)
```
Microservices Architecture
├── VietGl.Domain (shared)
├── VietGl.Accounting.Service (web API)
├── VietGl.Inventory.Service (gRPC)
├── VietGl.HRM.Service (gRPC)
├── VietGl.BI.Service (background worker)
├── VietGl.ApiGateway (Ocelot)
└── VietGl.Composition (orchestration)
```
- Independent deployable services
- Event-driven communication
- CQRS per service
- Separate databases per context

---

## 5. Scaling Checklist

| Phase | Architecture | Team Size | Deployment |
|-------|--------------|-----------|------------|
| 1 | Monolithic | 1-3 | Single IIS/Docker |
| 2 | Modular Monolith | 5-15 | Multiple apps |
| 3 | Microservices | 20+ | Kubernetes |

### When to Evolve?
- **Phase 1 → 2**: Team grows beyond 5, different release cycles needed
- **Phase 2 → 3**: Performance issues, scaling needs, independent scaling required

---

## 6. Technology Stack

| Component | Technology |
|-----------|------------|
| Framework | .NET 9 |
| Database | PostgreSQL |
| ORM | Entity Framework Core (Infrastructure only) |
| API | Minimal APIs or Controllers |
| Validation | FluentValidation (Application layer) |
| Testing | xUnit + Moq |

---

## 7. Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Entity | PascalCase | Voucher, Account |
| Command | {Action}{Entity}Command | CreateVoucherCommand |
| Query | {Action}{Entity}Query | GetVoucherByIdQuery |
| Repository | I{Entity}Repository | IVoucherRepository |
| Service | {Entity}Service | VoucherService |

---

## 8. Quick Reference

```bash
# Run solution
dotnet build
dotnet run --project src/VietGl.Infrastructure

# Run tests
dotnet test
```

---

## 9. Architecture Principles Summary

| Principle | Implementation |
|-----------|----------------|
| **Single Responsibility** | Each layer has one job |
| **Dependency Inversion** | Domain defines interfaces |
| **Immutability** | POSTED vouchers cannot change |
| **Testability** | Domain has no external deps |
| **Evolutionary** | Start simple, scale when needed |
