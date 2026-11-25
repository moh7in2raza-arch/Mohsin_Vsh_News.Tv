# Employee Management Workflow Audit

**Project:** VSH NEWS TV ERP  
**Audit date:** 2026-11-25  
**Scope:** Employee UI, domain entity, application service, PostgreSQL repository/schema, document workflow, wiring, and available tests.  
**Constraints:** Preserve the existing UI design, PostgreSQL schema/integration, and ADR layer boundaries. This audit makes no application-code or schema changes.

## Executive assessment

The employee module has a basic form, domain validation, list display/export, repository CRUD methods, and official DOCX/PDF/print form generation. However, the production workflow is incomplete. Most importantly, employee writes bypass the Unit of Work and are not committed on the connection created by the application composition root. Search, table-driven edit/delete, and actual document attachments are not implemented. Mutation permissions are also not enforced by the employee service or view.

The only employee-specific automated test found covers generated DOCX content/package preservation. No employee service, repository, persistence, CRUD, or validation tests were found. No live database operation was performed as part of this source audit.

## Checklist

| Workflow area | Status | Finding |
|---|---|---|
| 1. Employee Create | **COMPLETED** / **IMPROVEMENT** | The form creates an `Employee`, validates it, and calls the create service when the ID is not found. The service and repository implement insertion. In a service-less view, the UI instead reports success and retains the record only in memory (**BUG**, see error/persistence findings). There is no post-save form reset. |
| 2. Employee Save | **COMPLETED** / **BUG** | Save dispatches to create/update based on `employee_exists`. Repository writes are not committed through a Unit of Work, so success can be shown for a write that is later rolled back. The existence check and write are separate operations, and repository update does not check affected-row count. |
| 3. Employee Validation | **COMPLETED** / **MISSING** / **BUG** | Required employee ID, name, CNIC, department, designation, and non-negative salary checks exist. Email, phone, CNIC format, status choices, and salary precision/finite-value validation are missing. `Decimal("NaN")` is accepted by parsing and can raise `InvalidOperation` during domain comparison, which the UI does not catch; positive infinity can pass the negative check and fail later at PostgreSQL. |
| 4. Department Selection | **MISSING** / **BUG** | Department is a free-text line edit, not a selection populated from active configured departments. Repository lookup is exact-name and, if no row matches, automatically inserts a new department. This permits typos/inactive department use, can create unwanted master data, and can fail on generated department-code collisions. |
| 5. Employee Search | **MISSING** | The view loads the full ordered employee list and supports table export, but has no search field, filters, or paging. |
| 6. Employee Edit | **MISSING** / **BUG** | There is no row selection/load-to-form workflow. Entering an existing employee ID manually switches Save to update, which can overwrite the row without an explicit edit action. Repository update silently succeeds even if no row matched. |
| 7. Employee Delete | **MISSING** / **COMPLETED** | Service and repository delete methods exist, but the UI exposes no delete action, selection, or confirmation flow. No delete-specific service/repository tests were found. |
| 8. Employee Document Attachment | **MISSING** / **COMPLETED** | DOCX generation, PDF conversion, preview, and printing of the approved application form are implemented; the DOCX generation has a focused integrity/content test. This is not an attachment workflow: there is no upload, employee-document association, storage path/metadata, retrieval, or delete operation for employee files. |
| 9. Database Persistence | **BUG** / **COMPLETED** | SQL uses parameterized PostgreSQL statements and maps employee/departments to the current schema. But `build_services()` creates an external connection and passes it to `EmployeeRepository`; its connection context only yields that connection, and `EmployeeService` does not use `UnitOfWork`. With psycopg's default `autocommit=False`, employee writes have no commit boundary and may be rolled back when the connection closes. The repository connection is also not closed by the shown composition root. |
| 10. Error Handling | **COMPLETED** / **BUG** / **IMPROVEMENT** | Shared service calls show a generic UI error and log unexpected failures. The `employee_exists` call is outside that helper and displays raw exception text without logging. Document actions catch only selected exceptions; filesystem, ZIP/XML/template-index, and some process-launch errors can escape the UI handlers. Duplicate-CNIC/database errors are not translated into useful employee-specific messages. |

## Cross-cutting production risks

- **Authorization:** Main-window navigation checks `employee.view`, but the employee view does not use its `session` argument to gate Save, and `EmployeeService` accepts no session/permission context. A user allowed to view the module can invoke mutations through its visible form; backend enforcement is absent. Migration `0007` defines `employee.manage`, but the application permission constants and employee workflow do not enforce it.
- **Auditability:** Employee create/update/delete do not record audit events. The architecture decision requires business operations and related audit records to share a transaction for critical operations. HR identity and compensation changes should have attributable audit records.
- **Stale document data:** Document actions prefer `_last_employee` whenever present. After saving an employee, changing form fields without another successful save can generate/print a form for the previous saved snapshot rather than the visible form.
- **Sensitive data exposure:** The employee table and its export include CNIC and salary. Access and export behavior should be limited to authorized roles and reviewed for least-privilege requirements.
- **Test gap:** Current tests establish document-template correctness and employee table headings, but do not verify CRUD dispatch, validation edge cases, permissions, transaction durability, department resolution, or database error behavior.

## Implementation roadmap

### P0 — Make writes durable and authorized

1. Route employee create/update/delete through the existing `UnitOfWork` pattern; ensure each operation has one transaction and connection lifecycle, rather than retaining an unmanaged external connection.
2. Enforce `employee.manage` in the application service for every mutation and gate corresponding UI actions. Keep the existing `employee.view` navigation requirement.
3. Add employee audit events in the same transaction as the employee mutation. Translate expected employee/database conflicts into actionable user-facing errors; preserve logging for unexpected failures.
4. Add focused tests proving a committed write survives the operation boundary, a failed operation rolls back, and view-only sessions cannot mutate employee records.

### P1 — Complete employee directory CRUD and master-data selection

1. Add an active-department selector backed by an application query/service; repository writes should resolve an existing department and must not silently create one during employee save.
2. Add search/filtering and an explicit table-row selection/load workflow for editing.
3. Add delete with permission gating and confirmation. Check affected-row counts for update/delete and report missing/stale records instead of returning success.
4. Validate finite, non-negative salary and database precision; define and validate employee ID, CNIC, email, phone, and status according to approved business rules. Retain PostgreSQL constraints as the final integrity boundary.
5. Add unit and repository integration tests for create, update, delete, duplicate identifiers/CNIC, missing rows, department mapping, and validation boundaries.

### P2 — Add attachment workflow and harden document UX

1. Confirm required document types, storage location/retention, size/type limits, and access rules before implementation. Add an attachment workflow only after those requirements are agreed; do not treat generated forms as uploaded employee documents.
2. Keep the approved form template immutable. Add explicit handling for filesystem, malformed-template, and Word/PowerShell errors so failures are reported in the UI and logged where appropriate.
3. Ensure document actions use the currently selected/saved employee intentionally, and add tests for stale form state and document-generation error paths.

### P3 — Operational readiness

1. Add pagination or bounded loading if expected employee volume requires it.
2. Review employee exports for data minimization, role restrictions, and audit requirements.
3. Add end-to-end tests against a disposable PostgreSQL database and document deployment checks for the installed Windows/Word PDF and print dependencies.

## Source areas reviewed

- `src/app/ui/employees_view.py`
- `src/app/ui/employee_document.py`
- `src/app/application/services/employee_service.py`
- `src/app/domain/hr/employee.py`
- `src/app/infrastructure/repositories/employee_repository.py`
- `src/app/infrastructure/database/migrations/0002_hr.sql`
- `src/app/infrastructure/database/migrations/0007_employee_profile.sql`
- `src/app/infrastructure/database/unit_of_work.py`
- `src/app/infrastructure/database/connection.py`
- `src/app/bootstrap.py`
- `src/app/ui/main_window.py`, `src/app/ui/support.py`
- `docs/decisions/ADR-0001-canonical-technology-stack.md`
- `tests/unit/test_employee_document.py`, `tests/unit/test_report_standardization.py`
