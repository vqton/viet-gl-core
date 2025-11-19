# Roadmap: TT99 Accounting System

## Project Overview

Develop a full-featured, scalable, and user-friendly accounting software system compliant with **Thông tư 99/2025/TT-BTC**, effective for use from 01/01/2026. The system will support core accounting functions, integrate with Vietnamese business requirements (e.g., e-Invoicing), and ensure accurate financial reporting as per Vietnamese standards.

## Vision

To provide a robust, TT99-compliant accounting solution that simplifies financial management for Vietnamese businesses, ensuring accuracy, compliance, and operational efficiency.

## Phases

### Phase 1: Foundation & Core GL (MVP v1.0)

*   **Goal:** Establish the technical foundation and core General Ledger functionality.
*   **Timeline:** ~3 Months
*   **Focus:** MVP with basic journal entry creation, account management, and fundamental GL reporting.
*   **Key Features:**
    *   **Technical Infrastructure:**
        *   Finalize project structure (DDD layers).
        *   Complete `TT99DbContext` with `Account`, `JournalEntry`, `LedgerEntry` entities.
        *   Apply initial database migration with comprehensive COA seeding (TT99 Appendix II).
        *   Implement domain logic (`IsBalanced`, `Post`).
        *   Configure DI, MediatR, FluentValidation.
        *   Implement `CreateJournalEntryCommand` and `GetGeneralLedgerQuery` handlers.
    *   **Core Features (GL):**
        *   CRUD for Chart of Accounts (MST-03).
        *   Create and post Journal Entries via API (GL-01).
        *   Basic GL reporting (GetGeneralLedgerQuery) (GL-RPT).
        *   Basic audit logging (SYS-03).
    *   **Compliance:** Ghi sổ kép, COA TT99 Appendix II.
    *   **NFR:** Basic application stability and API responsiveness.

---

### Phase 2: Expand Core Modules (MVP v2.0)

*   **Goal:** Add Cash, Bank, Purchase, Sales, and basic Inventory modules.
*   **Timeline:** ~4 Months (after Phase 1)
*   **Focus:** Core business processes integrated with GL.
*   **Key Features:**
    *   **New Modules:**
        *   Cash & Bank: Entry, reconciliation, reports (CSH-01, CSH-03, CSH-RPT).
        *   Purchase: PO, Receipt, Invoice, AP tracking, reports (PUR-01, PUR-04, PUR-RPT).
        *   Sales: Invoice (stubbed E-Invoice API), AR tracking, returns, reports (SAL-03, SAL-04, SAL-RPT).
        *   Inventory: Receipt, Issue, Transfer, Adjustment, reports (INV-01, INV-03, INV-RPT).
    *   **Enhanced GL:**
        *   Allocation (242), FX adjustment (GL-02, GL-03).
        *   Basic period-end closing entries (GL-04).
        *   Enhanced reports (Trial Balance, basic Income Statement/Balance Sheet).
    *   **UI/UX (Initial):** Basic UI for core modules.
    *   **NFR:** Improved performance, basic security controls.

---

### Phase 3: Advanced Modules & Full TT99 Reporting (MVP v3.0)

*   **Goal:** Implement Fixed Assets, Costing, Tax reporting, and generate full TT99 financial statements.
*   **Timeline:** ~4 Months (after Phase 2)
*   **Focus:** Completeness of accounting functions and compliance reporting.
*   **Key Features:**
    *   **New Features:**
        *   Fixed Assets: Addition, depreciation, disposal, reports (AST-01, AST-02, AST-RPT).
        *   Costing: BOM, cost collection, product costing (CST-01, CST-02, CST-05).
        *   Tax: VAT declaration, XML export, CIT calculation (TAX-01, TAX-02, TAX-03).
        *   Full Financial Statements (B01-DN, B02-DN, B03-DN, B09-DN) (GL-RPT).
        *   Data Migration Tool (MIG-01, MIG-02).
    *   **Compliance:** Full validation against TT99 Appendix III.
    *   **NFR:** Scalability, enhanced security & audit logs.

---

### Phase 4: Polish, Integrate & Deploy (Production Ready)

*   **Goal:** Refine the system, integrate external services, finalize UI/UX, and prepare for production.
*   **Timeline:** ~3 Months (after Phase 3)
*   **Focus:** Production readiness, user experience, and integration.
*   **Key Features:**
    *   **Integration:**
        *   Full E-Invoice API integration.
        *   (Optional) Bank feed integration.
    *   **UI/UX (Polish):** Complete and refine UI/UX for all modules.
    *   **Testing:** Comprehensive UAT.
    *   **Deployment:** Prepare for on-premise deployment.
    *   **NFR:** Final performance/load testing, security audit.

---

## Current Status

*   **Phase:** Planning / Early Development (Phase 1 Initiated)
*   **Last Updated:** November 20, 2025
*   **Next Steps:**
    *   Finalize Phase 1 scope.
    *   Set up CI/CD.
    *   Begin Phase 1 development (Technical Infrastructure & Core GL).

---
