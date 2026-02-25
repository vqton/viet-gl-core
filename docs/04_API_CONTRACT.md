# API Contract - Accounting Core

## Overview
- This document defines the API contract for the AIErp Accounting Core.
- Version: v1
- Base URL: `/api/v1`
- Content-Type: `application/json`
- Authentication: Bearer Token (required)

---

## 1. Standard API Envelope

### 1.1 Success Response

```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always `true` for success responses |
| data | object/array | The response payload |
| timestamp | ISO8601 | Server timestamp in UTC |

### 1.2 Error Response

```json
{
  "success": false,
  "error": {
    "code": "IMBALANCE_DETECTED",
    "message": "Entry is not balanced - Debit must equal Credit",
    "details": {
      "totalDebit": "1000.0000",
      "totalCredit": "950.0000",
      "difference": "50.0000"
    }
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always `false` for error responses |
| error.code | string | Machine-readable error code |
| error.message | string | Human-readable error message |
| error.details | object | Optional additional context |
| timestamp | ISO8601 | Server timestamp in UTC |

---

## 2. RESTful Standards

### 2.1 HTTP Methods

| Method | Usage | Safe | Idempotent |
|--------|-------|------|------------|
| GET | Read resources | Yes | Yes |
| POST | Create new resources | No | No |
| PUT | Replace existing resource | No | Yes |
| PATCH | Partial update | No | No |
| DELETE | Remove resource | No | Yes |

### 2.2 Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, DELETE |
| 201 | Created | Successful POST (resource created) |
| 204 | No Content | Successful DELETE (no body to return) |
| 400 | Bad Request | Validation error, business logic error |
| 401 | Unauthorized | Missing or invalid Bearer Token |
| 403 | Forbidden | Token valid but insufficient permissions |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Duplicate resource or concurrency issue |
| 500 | Internal Server Error | Unhandled server error |

### 2.3 Pagination (for list endpoints)

```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalItems": 150,
    "totalPages": 8
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

## 3. Core API Endpoints

### 3.1 Accounts (Danh mục tài khoản)

#### GET /api/v1/accounts
Lấy danh mục tài khoản (Chart of Accounts)

**Authorization**: Bearer Token required

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | int | No | Page number (default: 1) |
| pageSize | int | No | Items per page (default: 20, max: 100) |
| type | int | No | Filter by AccountType (1=Asset, 2=Liability, etc.) |
| isDetail | bool | No | Filter detail/group accounts |
| search | string | No | Search by Code or Name |

**Response (200)**:
```json
{
  "success": true,
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "code": "1111",
      "name": "Tiền mặt",
      "type": 1,
      "normalBalance": 1,
      "isDetail": true,
      "parentId": null,
      "isActive": true
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "code": "1311",
      "name": "Phải thu khách hàng",
      "type": 1,
      "normalBalance": 1,
      "isDetail": true,
      "parentId": "550e8400-e29b-41d4-a716-446655440000",
      "isActive": true
    }
  ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "totalItems": 150,
    "totalPages": 8
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

#### GET /api/v1/accounts/{id}
Lấy chi tiết một tài khoản

**Response (200)**:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "code": "1111",
    "name": "Tiền mặt",
    "type": 1,
    "normalBalance": 1,
    "isDetail": true,
    "parentId": null,
    "description": "Tiền mặt tại quỹ",
    "isActive": true,
    "createdAt": "2025-01-01T00:00:00Z",
    "createdBy": "system",
    "lastModifiedAt": "2025-01-10T00:00:00Z",
    "lastModifiedBy": "admin"
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

### 3.2 Vouchers (Chứng từ)

#### POST /api/v1/vouchers
Tạo mới chứng từ (trạng thái DRAFT)

**Authorization**: Bearer Token required

**Request Body**:
```json
{
  "entryDate": "2025-01-15",
  "fiscalPeriodId": "550e8400-e29b-41d4-a716-446655440099",
  "currency": "VND",
  "exchangeRate": 1.0,
  "description": "Thu tiền khách hàng A",
  "items": [
    {
      "accountId": "550e8400-e29b-41d4-a716-446655440001",
      "partnerId": "550e8400-e29b-41d4-a716-446655440010",
      "debitAmount": 10000000,
      "creditAmount": 0,
      "description": "Thu tiền"
    },
    {
      "accountId": "550e8400-e29b-41d4-a716-446655440000",
      "partnerId": null,
      "debitAmount": 0,
      "creditAmount": 10000000,
      "description": "Tiền vào quỹ"
    }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| entryDate | date | Yes | Transaction date |
| fiscalPeriodId | guid | Yes | Fiscal period ID |
| currency | string | Yes | Currency code (VND, USD, etc.) |
| exchangeRate | decimal | No | Exchange rate (default: 1.0) |
| description | string | Yes | Header description |
| items | array | Yes | Array of journal items (min 2) |

**Item Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| accountId | guid | Yes | Account ID |
| partnerId | guid | Conditional | Required for accounts 131, 331 |
| debitAmount | decimal | Yes* | Debit amount (mutually exclusive with credit) |
| creditAmount | decimal | Yes* | Credit amount (mutually exclusive with debit) |
| description | string | No | Line description |

*Either DebitAmount or CreditAmount must be > 0, not both.

**Response (201 - Created)**:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440099",
    "entryNumber": "PJ/2025/0001",
    "entryDate": "2025-01-15",
    "fiscalPeriodId": "550e8400-e29b-41d4-a716-446655440099",
    "currency": "VND",
    "exchangeRate": 1.0,
    "description": "Thu tiền khách hàng A",
    "status": 1,
    "totalDebit": 10000000,
    "totalCredit": 10000000,
    "createdAt": "2025-01-15T10:30:00Z",
    "createdBy": "user123",
    "items": [
      {
        "id": "...",
        "accountId": "550e8400-e29b-41d4-a716-446655440001",
        "partnerId": "550e8400-e29b-41d4-a716-446655440010",
        "debitAmount": 10000000,
        "creditAmount": 0
      },
      {
        "id": "...",
        "accountId": "550e8400-e29b-41d4-a716-446655440000",
        "partnerId": null,
        "debitAmount": 0,
        "creditAmount": 10000000
      }
    ]
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

**Error Response (400 - Business Logic)**:
```json
{
  "success": false,
  "error": {
    "code": "IMBALANCE_DETECTED",
    "message": "Entry is not balanced",
    "details": {
      "totalDebit": "10000000.0000",
      "totalCredit": "9500000.0000",
      "difference": "500000.0000"
    }
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

#### GET /api/v1/vouchers/{id}
Xem chi tiết chứng từ và các bút toán

**Response (200)**:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440099",
    "entryNumber": "PJ/2025/0001",
    "entryDate": "2025-01-15",
    "fiscalPeriodId": "550e8400-e29b-41d4-a716-446655440099",
    "currency": "VND",
    "description": "Thu tiền khách hàng A",
    "status": 2,
    "totalDebit": 10000000,
    "totalCredit": 10000000,
    "postedAt": "2025-01-15T11:00:00Z",
    "postedBy": "user123",
    "createdAt": "2025-01-15T10:30:00Z",
    "createdBy": "user123",
    "items": [
      {
        "id": "...",
        "accountId": "550e8400-e29b-41d4-a716-446655440001",
        "accountCode": "1311",
        "accountName": "Phải thu khách hàng",
        "partnerId": "550e8400-e29b-41d4-a716-446655440010",
        "partnerName": "Công ty ABC",
        "debitAmount": 10000000,
        "creditAmount": 0,
        "baseAmount": 10000000
      },
      {
        "id": "...",
        "accountId": "550e8400-e29b-41d4-a716-446655440000",
        "accountCode": "1111",
        "accountName": "Tiền mặt",
        "partnerId": null,
        "debitAmount": 0,
        "creditAmount": 10000000,
        "baseAmount": 10000000
      }
    ]
  },
  "timestamp": "2025-01-15T10:30:00Z"
}
```

#### GET /api/v1/vouchers
Tìm kiếm chứng từ

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| page | int | No | Page number |
| pageSize | int | No | Items per page |
| status | int | No | Filter by status (1=Draft, 2=Posted, 3=Void) |
| fromDate | date | No | Filter from date |
| toDate | date | No | Filter to date |
| search | string | No | Search in description/entryNumber |

#### POST /api/v1/vouchers/{id}/post
Ghi sổ chứng từ (Chuyển trạng thái DRAFT → POSTED)

**Authorization**: Bearer Token required

**Response (200)**:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440099",
    "entryNumber": "PJ/2025/0001",
    "status": 2,
    "postedAt": "2025-01-15T11:00:00Z",
    "postedBy": "user123"
  },
  "timestamp": "2025-01-15T11:00:00Z"
}
```

**Error Response (400)**:
```json
{
  "success": false,
  "error": {
    "code": "FISCAL_PERIOD_CLOSED",
    "message": "Fiscal period is closed for posting"
  },
  "timestamp": "2025-01-15T11:00:00Z"
}
```

#### POST /api/v1/vouchers/{id}/void
Hủy chứng từ (Chuyển trạng thái POSTED/VOID → VOID)

**Authorization**: Bearer Token required

**Response (200)**:
```json
{
  "success": true,
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440099",
    "entryNumber": "PJ/2025/0001",
    "status": 3,
    "voidedAt": "2025-01-15T11:30:00Z",
    "voidedBy": "user123"
  },
  "timestamp": "2025-01-15T11:30:00Z"
}
```

---

## 4. Integration Pattern (Clean Lite)

### 4.1 Principle
Other modules (Inventory, Sales, Purchase, HRM) **MUST NOT** write directly to the Accounting database. They must communicate via API or Internal Service Bus.

### 4.2 Integration Flow

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Inventory     │     │  Internal Bus    │     │  Accounting     │
│   Module        │────►│  (Message Queue) │────►│  Module         │
│                 │     │                  │     │                 │
│ - Xuất kho      │     │ - VoucherCreated │     │ - Receives      │
│ - Nhập kho      │     │ - VoucherPosted  │     │ - Validates     │
│ - Chuyển kho    │     │ - VoucherVoided  │     │ - Creates       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### 4.3 Integration API (for internal modules)

#### POST /api/v1/internal/vouchers
Internal endpoint for other modules to create vouchers

**Header**: `X-Internal-Key: {internal_api_key}`

**Request**: Same as public POST /api/v1/vouchers

**Usage Example**:
```json
// Inventory Module: When goods are delivered
POST /api/v1/internal/vouchers
Header: X-Internal-Key: internal-secret-key
Body: {
  "entryDate": "2025-01-15",
  "fiscalPeriodId": "...",
  "currency": "VND",
  "description": "Xuất kho - Đơn hàng DH001",
  "items": [
    { "accountId": "...", "debitAmount": 10000000, "creditAmount": 0 },
    { "accountId": "...", "debitAmount": 0, "creditAmount": 10000000 }
  ]
}
```

### 4.4 Event Types

| Event | Description | Payload |
|-------|-------------|---------|
| VoucherCreated | Internal voucher created | VoucherId, CreatedBy |
| VoucherPosted | Voucher posted to ledger | VoucherId, PostedBy, LedgerEntryIds |
| VoucherVoided | Voucher voided | VoucherId, VoidedBy, ReversalEntryId |

---

## 5. Security

### 5.1 Authentication

All endpoints require a Bearer Token in the Authorization header:

```
Authorization: Bearer {access_token}
```

### 5.2 Token Format

```json
{
  "sub": "user123",
  "companyId": "company-001",
  "roles": ["accountant", "manager"],
  "iat": 1705312200,
  "exp": 1705398600
}
```

### 5.3 Response Codes

| Code | Description |
|------|-------------|
| 401 | Missing Authorization header |
| 401 | Invalid or expired token |
| 403 | Token valid but insufficient permissions |

### 5.4 Permissions

| Role | GET /accounts | POST /vouchers | POST /vouchers/{id}/post | POST /vouchers/{id}/void |
|------|--------------|----------------|--------------------------|-------------------------|
| Viewer | ✅ | ❌ | ❌ | ❌ |
| Accountant | ✅ Read | ✅ Create | ✅ Post | ✅ Void |
| Manager | ✅ | ✅ | ✅ | ✅ |
| Admin | ✅ | ✅ | ✅ | ✅ |

---

## 6. Error Codes Reference

| Code | HTTP Status | Description |
|------|-------------|-------------|
| VALIDATION_ERROR | 400 | Invalid request body |
| IMBALANCE_DETECTED | 400 | Debit != Credit |
| FISCAL_PERIOD_CLOSED | 400 | Cannot post to closed period |
| INVALID_STATUS_TRANSITION | 400 | Invalid state change |
| PARTNER_REQUIRED | 400 | Partner required for 131/331 |
| UNKNOWN_ACCOUNT | 400 | Account does not exist |
| UNAUTHORIZED | 401 | Missing/invalid token |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| DUPLICATE_ENTRY | 409 | Duplicate entry number |
| INTERNAL_ERROR | 500 | Server error |

---

## 7. Quick Reference

### Base URL
```
Production: https://api.aierp.com/v1
Staging: https://staging-api.aierp.com/v1
Development: http://localhost:5000/api/v1
```

### Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/accounts | List accounts |
| GET | /api/v1/accounts/{id} | Get account details |
| GET | /api/v1/vouchers | List vouchers |
| GET | /api/v1/vouchers/{id} | Get voucher details |
| POST | /api/v1/vouchers | Create voucher (Draft) |
| POST | /api/v1/vouchers/{id}/post | Post voucher |
| POST | /api/v1/vouchers/{id}/void | Void voucher |
| POST | /api/v1/internal/vouchers | Internal voucher creation |
