# VSH NEWS TV ERP Project Audit

**Audit date:** 2026-11-23
**Repository:** `moh7in2raza-arch/Mohsin_Vsh_News.Tv`
**Branch / revision:** `main` / `67a6561` (`stable-vsh-dashboard`)
**Scope:** source architecture, ADR alignment, UI modules, PostgreSQL, tests, and current Git state. Database checks were read-only; no credentials or password hashes are included here.

## 1. Executive Summary

The project has a working Python/PySide6/PostgreSQL foundation, a login flow, a VSH NEWS TV dashboard, and a tested accounting workflow for vouchers, posting, reversal, and core reports. The live PostgreSQL database is reachable as `erp_app`; migrations are at version 10, and the schema checker accepts the required core schema and permission codes.

The application is **not production-ready**. Several screens imply functionality that is not implemented: employee save reports success without persisting, the user service is empty, the user/role screen is effectively read-only, and multiple report and broadcast cards route to generic views. Fiscal-period closure is not enforced by voucher posting. One active database user has a placeholder password hash. All 23 pytest tests pass their assertions, but the full test process exits with Windows status `-1073741819` (`0xC0000005`, access violation); the isolated Qt shell smoke test reproduces this process-exit failure.

## 2. Current Completion Percentage

**Estimated completion: approximately 52%.** This is a feature-readiness estimate, not a LOC or test-coverage metric. Core database/authentication and accounting workflows are weighted more heavily than placeholder screens. The estimate reflects the functional dashboard and core financial workflow, offset by incomplete HR and user administration, limited reporting, missing period controls, and the unresolved Qt process crash.

## 3. Completed Modules

- **Architecture foundation:** `src/app/` is separated into UI, application services, domain, and infrastructure. SQL is primarily in repositories; `UnitOfWork` provides shared transaction scope for voucher/account/report/company operations.
- **PostgreSQL foundation:** `.env`-based connection works against `erp_office` as `erp_app`. The database is at schema version 10; `python -m tools.check_schema` passes its required table/column and permission checks.
- **Authentication:** Argon2 password verification, active-account check, permission loading, login/logout audit attempts, and a session object are implemented. The login signal currently connects to the VSH NEWS TV startup window.
- **Dashboard:** `VshNewsMainWindow` loads `DashboardView` after login. Dashboard buttons connect to module routes; all 25 visible card items have a route entry. VSH NEWS TV and company branding are present.
- **Accounts:** account listing and account creation are service/repository-backed and permission-checked. The view supports CSV/PDF export and optional Excel export.
- **Voucher/accounting core:** services cover draft creation, submit, approve, post, and reversal. Journal domain rules validate balanced debit/credit lines. Database migrations add constraints and append-only triggers for posted journal and audit data.
- **Company profile backend:** profile reads and updates have a service/repository path; updates record an audit event in the same unit of work.
- **Build-time syntax:** `python -m compileall -q src` passes.

## 4. Partially Completed Modules

| Module | Current state |
|---|---|
| **Employees / HR** | Employee domain, service, and repository expose CRUD-like operations, but `EmployeesView.save_employee()` only shows “Employee saved successfully” and never calls the service; `refresh()` is empty. The dashboard routes Attendance, Payroll, and Salary Reports to this same employee form. No attendance, payroll, lifecycle documents, letters, or exit workflow is implemented. |
| **Accounts** | List/create and export are wired. Customer/Supplier cards are aliases to the chart of accounts; there are no separate customer or supplier ledgers. |
| **Reports** | Trial balance and account ledger have service/repository implementations. P&L, Balance Sheet, statements, and reconciliation cards reuse `ReportsView`; that view only has Trial Balance and Account Ledger tabs. |
| **Vouchers** | Core workflow is implemented and integration-tested. Payment, Receipt, Journal, Sales, Client Billing, and Ad Schedules route to the generic voucher view without separate voucher-type filtering or media billing behavior. |
| **Company profile** | Company settings are stored and update through the company service. `get_profile()` catches every exception and silently returns defaults, which can hide connection/schema failures. |
| **Users & Roles** | The dashboard’s `UsersRolesView` displays current-session data when no user service is present. `src/app/application/services/user_service.py` is empty, `Services` has no users service, and the separate `UsersView` is not wired into the application. User creation, role assignment, disablement, and password reset are not operational. |
| **System settings** | The UI displays hard-coded settings and reports “saved” without persisting them. |
| **Backup / restore** | A UI invokes `pg_dump`/`psql` directly via `subprocess`; there is no automated backup/restore test or verified recovery procedure. Credentials may require external PostgreSQL client configuration. |

## 5. Missing Features

- Employee UI persistence, service-level authorization, transactional writes, audit records, full HR lifecycle, attendance, payroll, employee documents, and letters.
- User/role/permission administration, password reset and forced password-change flow. The login “Forgot Password?” and “Remember Session” controls have no completed workflow.
- P&L, Balance Sheet, bank reconciliation, and dedicated statement/report implementations.
- Fiscal-period enforcement during posting. `VoucherService.post()` currently passes `period_closed=False` to posting rules, so persisted fiscal-period closure is not consulted.
- Dedicated implementations for the dashboard’s broadcast/media cards; they currently alias accounting screens.
- Tested backup-and-restore, installer validation on a clean Windows machine, and a clean shutdown test for the native Qt application.
- Production credential/bootstrap process that rejects or replaces placeholder password hashes.

## 6. Technical Debt

- **Employee connection/transaction lifecycle:** `build_services()` opens a PostgreSQL connection and injects it into `EmployeeRepository`. The repository treats an injected connection as external and does not create its own transaction or close it. Employee writes therefore lack the transaction/audit guarantees used by the other services, and the injected connection remains open for the service lifetime.
- **False-success UI:** Employee save and some settings actions show success without performing or persisting the advertised operation.
- **Broad silent fallback:** `CompanyService.get_profile()` catches every exception and returns `DEFAULT_COMPANY`, masking database errors as normal data.
- **UI/infrastructure coupling:** `DatabaseBackupView` launches PostgreSQL command-line tools directly, rather than delegating backup/restore to an infrastructure service.
- **Permission drift:** the database has 20 permission codes, while `permissions.py` defines only the core 9 in `P.ALL`; dashboard routing uses string fallbacks for employee, user, and backup permissions.
- **Schema-check drift:** `tools/check_schema.py` reports schema version 10 but still tells operators to migrate only until version 6. Its direct-file invocation can also fail to import `src`; use the documented `python -m tools.check_schema`.
- **Documentation drift:** README links to `ADR-001-canonical-technology-stack.md`, but the checked-in ADR is `ADR-0001-canonical-technology-stack.md`. README roadmap/status text predates the current dashboard and module routes.
- **Qt test teardown:** `tests/unit/test_shell_smoke.py` closes windows but does not explicitly dispose of the `QApplication` lifecycle. This is the only test isolated to the access-violation exit; the cause is not yet proven, but it must be resolved before treating the test run as clean.

## 7. Database Status

- **Connectivity:** verified read-only connection to database `erp_office` as role `erp_app`.
- **Schema:** latest applied migration is **10**; the documented schema checker exits successfully. No migration was applied during this audit.
- **Current row counts:** 2 users, 1 employee, 14 accounts, 0 voucher headers, 0 journal entries, and 1 company settings row.
- **Credential readiness:** one active user row has a placeholder password hash. It cannot authenticate with a valid Argon2 password until reset; the account and hash are intentionally not identified in this report.
- **Permission data:** 20 permission rows exist; the schema checker found no missing codes from the application’s current `P.ALL` set.
- **Operational consequence:** the database is structurally reachable, but it contains no accounting transactions, and the active placeholder credential requires remediation before release.

## 8. Git Status

- **Branch:** `main`
- **HEAD:** `67a6561` (`stable-vsh-dashboard`), aligned with `origin/main` at audit time.
- Before writing this report, the only reported working-tree item was an unrelated untracked root file, `ProjectReport.md`. No source modifications were pending.
- This audit updates `docs/project_status_report.md`; that report file is therefore the intended tracked change. The pre-existing `ProjectReport.md` is not modified.

## 9. Production Readiness

**Not ready for production (no-go).** The database and main accounting flow have meaningful implementation and test coverage, but current evidence includes:

1. A reproducible Windows access violation after the Qt shell smoke test passes.
2. An active placeholder credential.
3. Employee and user-management screens that are incomplete or report success without persistence.
4. No fiscal-period enforcement in voucher posting.
5. Incomplete financial statements and unimplemented HR/reporting/dashboard aliases.
6. No verified backup restore or clean-machine installer acceptance.

The latest full test run reported **23 passed**, but pytest exited with `-1073741819` (`0xC0000005`). Isolating `tests/unit/test_shell_smoke.py` produced **1 passed** and the same fatal process exit. The other 22 unit/integration tests completed with exit code 0. `compileall` and `python -m tools.check_schema` also completed successfully.

## 10. Recommended Next Steps

1. **Resolve the Qt access violation:** make QApplication and test-widget teardown deterministic; rerun the isolated smoke test and full suite on Windows until both exit cleanly.
2. **Remove the placeholder credential:** reset or disable the affected active account using a controlled admin/bootstrap process; verify no placeholder hashes remain.
3. **Implement employee CRUD end-to-end:** inject the employee service into the view, use a per-operation unit of work, enforce permissions, validate input, and audit writes; remove false-success messages.
4. **Implement user administration:** add a real user service/repository workflow and connect it to `UsersView`/`UsersRolesView`; define all permission constants centrally and test authorization.
5. **Finish accounting controls and reports:** consult fiscal-period state on posting and implement/report-test P&L, Balance Sheet, reconciliation, and statement routes.
6. **Make dashboard scope truthful:** implement dedicated attendance/payroll/media modules or mark those routes clearly unavailable instead of routing to generic screens.
7. **Harden company and backup operations:** surface profile-read failures; move `pg_dump`/restore into infrastructure services and test a restore in a disposable database.
8. **Refresh operator documentation and release gates:** fix the ADR link and schema-version message, update the README roadmap, and validate the installer on a clean Windows system with a tested backup/restore plan.
