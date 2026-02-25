# Domain Logic - Double-Entry Accounting

## 1. Core Principles

### 1.1 Double-Entry System
- Every transaction has two sides: **Debit** and **Credit**
- **Golden Rule**: Sum(Debit) = Sum(Credit) for every voucher
- Imbalance = Sum(Debit) - Sum(Credit) must be ZERO

### 1.2 Immutability
- Once **POSTED**, a voucher becomes **IMMUTABLE**
- No editing, deletion, or modification allowed after posting
- Only **VOID** action is permitted (creates reversal trail)

---

## 2. Voucher Lifecycle

```
[DRAFT] ──────► [POSTED] ──────► [VOID]
    │              │               │
    │              │               │
    ▼              ▼               ▼
 Create/Edit   Immutable      Reversal Trail
```

### 2.1 DRAFT (Trạng thái nháp)
- **Initial state** when created
- Can be **edited** (add/edit/delete lines)
- Can be **POSTED** or **VOIDED**

### 2.2 POSTED (Đã ghi sổ)
- **Locked state** - IMMUTABLE
- Ledger entries have been created
- Can only be **VOIDED** (not edited)
- Contains: PostedAt, PostedBy timestamps

### 2.3 VOID (Đã hủy)
- **Terminal state** - final state
- Original voucher preserved (audit trail)
- Reversal entries may be generated
- Contains: VoidedAt, VoidedBy timestamps

---

## 3. Validation Rules

### 3.1 Balance Check
```
Sum(Debit) - Sum(Credit) = 0
```
- Tolerance: 0 (strict equality for decimal)
- If imbalance detected → reject POST

### 3.2 Fiscal Period Check
- Voucher.Date must be within an **OPEN** fiscal period
- Period must exist and IsOpen = true
- Closed periods reject new postings

### 3.3 Line Rules
| Rule | Description |
|------|-------------|
| Mutually Exclusive | A line must have either Debit OR Credit, not both |
| Non-Zero | Either Debit or Credit must be > 0 |
| Valid Account | AccountCode must exist in Chart of Accounts |
| Currency | All lines must use same currency as voucher header |

### 3.4 Required Fields
- Voucher Date
- Currency
- At least 2 lines (debit + credit)
- Valid AccountCodes on all lines

---

## 4. Domain Model (Conceptual)

### 4.1 Entities
- **Voucher**: Aggregate root
  - Id, Date, FiscalPeriodId, Currency, Status, Description
  - Lines: List<VoucherLine>
  - Audit: CreatedAt, CreatedBy, PostedAt, PostedBy, VoidedAt, VoidedBy

- **VoucherLine**: Part of Voucher aggregate
  - Id, VoucherId, AccountCode, Debit, Credit, Description

- **Account**: Reference data
  - Code, Name, NormalBalance (Debit/Credit)

- **FiscalPeriod**: Reference data
  - Id, Year, Month, StartDate, EndDate, IsOpen

### 4.2 Value Objects
- **Money**: Amount (decimal) + Currency (string)
- **VoucherStatus**: Enum (Draft, Posted, Void)

### 4.3 Domain Errors
| Error | Trigger |
|-------|---------|
| ImbalanceDetectedError | Debit != Credit |
| FiscalPeriodClosedError | Period.IsOpen = false |
| InvalidStatusTransitionError | Invalid state change |
| UnknownAccountError | AccountCode not found |

---

## 5. Business Rules Summary

| Rule | Description |
|------|-------------|
| Double-Entry | Sum(Debit) = Sum(Credit) |
| Immutability | POSTED vouchers cannot be modified |
| One-Way Flow | DRAFT → POSTED → VOID |
| Fiscal Period | Must post within open period |
| Audit Trail | All actions timestamped and user-tracked |

---

## 6. Compliance (Circular 99/2025/TT-BTC)

- All vouchers must retain original data after posting
- Void operation must create audit trail
- Fiscal period control required
- Debit/Credit balance mandatory
- Currency handling per Vietnam accounting standards
