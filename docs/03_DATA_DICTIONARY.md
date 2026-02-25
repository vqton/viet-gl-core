# Data Dictionary - Accounting Core

## Overview
- This document defines the core data model for the accounting system.
- All monetary values use `NUMERIC(20,4)` for precision.
- Every table includes audit fields: `CreatedAt`, `CreatedBy`, `LastModifiedAt`, `LastModifiedBy`.

---

## 1. Account (Chart of Accounts)

### Description
- Master data for all accounts in the general ledger.
- Supports hierarchical structure (parent-child).

| Field | Type | Nullable | Default | Description |
|-------|------|----------|---------|-------------|
| Id | UUID | No | Auto | Primary key |
| Code | VARCHAR(20) | No | - | Unique account code (e.g., 1111, 3311) |
| Name | NVARCHAR(200) | No | - | Account name in Vietnamese/English |
| Type | INT | No | - | 1=Asset, 2=Liability, 3=Equity, 4=Revenue, 5=Expense |
| NormalBalance | INT | No | - | 1=Debit, 2=Credit |
| IsDetail | BOOLEAN | No | false | true=Detail account, false=Group header |
| ParentId | UUID | Yes | null | FK to parent Account (nullable for root) |
| IsActive | BOOLEAN | No | true | Soft delete flag |
| Description | NVARCHAR(500) | Yes | - | Optional notes |
| CreatedAt | TIMESTAMP | No | now() | Creation timestamp |
| CreatedBy | VARCHAR(50) | No | - | User who created |
| LastModifiedAt | TIMESTAMP | No | now() | Last update timestamp |
| LastModifiedBy | VARCHAR(50) | No | - | User who last modified |

### Relationships
- Self-referential: `ParentId` → `Account.Id`
- One Account has Many Child Accounts

### Indexes
- `UQ_Account_Code` UNIQUE on `Code`
- `IX_Account_ParentId` on `ParentId`

---

## 2. JournalEntry (Voucher / Phiếu kế toán)

### Description
- The main document for double-entry transactions.
- Represents a voucher (Sổ kế toán).

| Field | Type | Nullable | Default | Description |
|-------|------|----------|---------|-------------|
| Id | UUID | No | Auto | Primary key |
| EntryNumber | VARCHAR(20) | No | Auto | Sequential voucher number (e.g., PJ/2025/0001) |
| EntryDate | DATE | No | - | Transaction date |
| FiscalPeriodId | UUID | No | - | FK to FiscalPeriod |
| Currency | VARCHAR(3) | No | VND | ISO currency code |
| ExchangeRate | NUMERIC(18,6) | No | 1.0 | Exchange rate (for multi-currency) |
| Description | NVARCHAR(500) | No | - | Header description |
| Status | INT | No | 1 | 1=DRAFT, 2=POSTED, 3=VOID |
| TotalDebit | NUMERIC(20,4) | No | 0 | Sum of debit amounts |
| TotalCredit | NUMERIC(20,4) | No | 0 | Sum of credit amounts |
| PostedAt | TIMESTAMP | Yes | - | When posted |
| PostedBy | VARCHAR(50) | Yes | - | User who posted |
| VoidedAt | TIMESTAMP | Yes | - | When voided |
| VoidedBy | VARCHAR(50) | Yes | - | User who voided |
| OriginalEntryId | UUID | Yes | - | Original entry if voided (reversal link) |
| CreatedAt | TIMESTAMP | No | now() | Creation timestamp |
| CreatedBy | VARCHAR(50) | No | - | User who created |
| LastModifiedAt | TIMESTAMP | No | now() | Last update timestamp |
| LastModifiedBy | VARCHAR(50) | No | - | User who last modified |

### Relationships
- One JournalEntry has Many JournalItems
- One JournalEntry belongs to One FiscalPeriod

### Business Rules
- `TotalDebit` MUST equal `TotalCredit` (balance check)
- `Status = 1` (DRAFT): Can edit, can post, can void
- `Status = 2` (POSTED): Immutable, can only void
- `Status = 3` (VOID): Terminal state, no further changes

### Indexes
- `UQ_JournalEntry_EntryNumber` UNIQUE on `EntryNumber`
- `IX_JournalEntry_EntryDate` on `EntryDate`
- `IX_JournalEntry_FiscalPeriodId` on `FiscalPeriodId`
- `IX_JournalEntry_Status` on `Status`

---

## 3. JournalItem (Journal Entry Line / Bút toán)

### Description
- Individual debit/credit lines within a JournalEntry.
- Each item represents one line in the double-entry ledger.

| Field | Type | Nullable | Default | Description |
|-------|------|----------|---------|-------------|
| Id | UUID | No | Auto | Primary key |
| JournalEntryId | UUID | No | - | FK to JournalEntry |
| AccountId | UUID | No | - | FK to Account (Chart of Accounts) |
| PartnerId | UUID | Yes | - | FK to Partner (for 131, 331 accounts) |
| DebitAmount | NUMERIC(20,4) | No | 0 | Debit amount in voucher currency |
| CreditAmount | NUMERIC(20,4) | No | 0 | Credit amount in voucher currency |
| BaseAmount | NUMERIC(20,4) | No | 0 | Amount in base currency (VND) |
| ExchangeRate | NUMERIC(18,6) | No | 1.0 | Exchange rate used |
| Description | NVARCHAR(250) | Yes | - | Line description |
| CreatedAt | TIMESTAMP | No | now() | Creation timestamp |
| CreatedBy | VARCHAR(50) | No | - | User who created |
| LastModifiedAt | TIMESTAMP | No | now() | Last update timestamp |
| LastModifiedBy | VARCHAR(50) | No | - | User who last modified |

### Relationships
- Many JournalItems belong to One JournalEntry
- Many JournalItems reference One Account
- Many JournalItems reference One Partner (optional)

### Business Rules
- Either `DebitAmount > 0` OR `CreditAmount > 0`, never both
- `DebitAmount + CreditAmount > 0` (must have value)
- For Account Code 131 (Receivable) or 331 (Payable): `PartnerId` is REQUIRED
- `BaseAmount = Amount * ExchangeRate`

### Indexes
- `IX_JournalItem_JournalEntryId` on `JournalEntryId`
- `IX_JournalItem_AccountId` on `AccountId`
- `IX_JournalItem_PartnerId` on `PartnerId`

---

## 4. Partner (Customer / Supplier)

### Description
- Master data for business partners (customers and suppliers).
- Used primarily with accounts 131 (Receivables) and 331 (Payables).

| Field | Type | Nullable | Default | Description |
|-------|------|----------|---------|-------------|
| Id | UUID | No | Auto | Primary key |
| Code | VARCHAR(20) | No | - | Unique partner code |
| Name | NVARCHAR(200) | No | - | Partner name |
| Type | INT | No | - | 1=Customer, 2=Supplier, 3=Both |
| TaxCode | VARCHAR(20) | Yes | - | Tax identification number |
| Phone | VARCHAR(20) | Yes | - | Contact phone |
| Email | VARCHAR(100) | Yes | - | Contact email |
| Address | NVARCHAR(500) | Yes | - | Physical address |
| IsActive | BOOLEAN | No | true | Soft delete flag |
| CreatedAt | TIMESTAMP | No | now() | Creation timestamp |
| CreatedBy | VARCHAR(50) | No | - | User who created |
| LastModifiedAt | TIMESTAMP | No | now() | Last update timestamp |
| LastModifiedBy | VARCHAR(50) | No | - | User who last modified |

### Relationships
- One Partner has Many JournalItems

### Indexes
- `UQ_Partner_Code` UNIQUE on `Code`
- `IX_Partner_Type` on `Type`

---

## 5. FiscalPeriod (Kỳ kế toán)

### Description
- Defines open/closed periods for accounting.
- Controls when postings are allowed.

| Field | Type | Nullable | Default | Description |
|-------|------|----------|---------|-------------|
| Id | UUID | No | Auto | Primary key |
| Year | INT | No | - | Fiscal year (e.g., 2025) |
| Period | INT | No | - | Month (1-12) or 0 for yearly |
| StartDate | DATE | No | - | Period start date |
| EndDate | DATE | No | - | Period end date |
| IsOpen | BOOLEAN | No | false | true=Can post, false=Closed |
| IsAdjustmentPeriod | BOOLEAN | No | false | For adjusting entries |
| Description | NVARCHAR(200) | Yes | - | Notes |
| CreatedAt | TIMESTAMP | No | now() | Creation timestamp |
| CreatedBy | VARCHAR(50) | No | - | User who created |
| LastModifiedAt | TIMESTAMP | No | now() | Last update timestamp |
| LastModifiedBy | VARCHAR(50) | No | - | User who last modified |

### Business Rules
- Only ONE open period per year at a time
- Cannot close period if unposted draft entries exist (optional enforcement)
- Year + Period combination must be unique

### Indexes
- `UQ_FiscalPeriod_YearPeriod` UNIQUE on `Year, Period`
- `IX_FiscalPeriod_IsOpen` on `IsOpen`

---

## 6. Summary: Entity Relationships

```
┌─────────────┐       ┌────────────────┐       ┌─────────────┐
│   Account   │       │  JournalEntry │       │   Partner   │
│  (Chart of  │◄──────│    (Voucher)  │──────►│ (Customer/  │
│  Accounts)  │       │                │       │  Supplier)  │
└─────────────┘       └────────┬───────┘       └─────────────┘
                               │
                               │ 1:N
                               ▼
                        ┌────────────────┐
                        │  JournalItem   │
                        │   (Line)       │
                        └────────────────┘
                               │
                               │ N:1
                               ▼
                        ┌─────────────┐
                        │FiscalPeriod │
                        └─────────────┘
```

---

## 7. Audit Fields Standard

Every table MUST include:

| Field | Type | Description |
|-------|------|-------------|
| CreatedAt | TIMESTAMP | When record was created |
| CreatedBy | VARCHAR(50) | Who created the record |
| LastModifiedAt | TIMESTAMP | When record was last updated |
| LastModifiedBy | VARCHAR(50) | Who last modified the record |

### Implementation Notes
- Use `DEFAULT NOW()` for timestamp fields
- Populate `CreatedBy` / `LastModifiedBy` from JWT claims or system user
- Implement soft delete via `IsActive` flag where applicable

---

## 8. Data Type Quick Reference

| Concept | PostgreSQL Type | C# Type |
|---------|----------------|---------|
| Primary Key | UUID | Guid |
| Money | NUMERIC(20,4) | decimal |
| Exchange Rate | NUMERIC(18,6) | decimal |
| Date | DATE | DateOnly |
| Timestamp | TIMESTAMP | DateTime |
| User ID | VARCHAR(50) | string |
| Vietnamese Text | NVARCHAR(n) | string |
| Code | VARCHAR(20) | string |
