# Accounting Voucher System Analysis

## Result

The application code now supports Journal, Payment, Receipt, Contra, Sales,
and Purchase vouchers; draft editing and soft deletion; submission, approval,
posting and reversal; ledger/trial-balance generation; voucher search and
PDF output. Voucher totals are validated before saving and again before
posting.

The configured database has **not** been migrated. Its full pre-migration
backup failed because the application database role cannot read legacy Django
tables. The migration runner stopped before applying DDL or seed data. No
configured-database records were changed.

## Repository and schema findings

- Active entry points: `run.py`, `src/app/main.py`; the app uses PySide6 and
  PostgreSQL.
- Voucher UI: `src/app/ui/voucher_dialog.py`,
  `src/app/ui/vouchers_view.py`.
- Voucher workflow: `VoucherService`, `PostingService`, domain journal rules,
  and `VoucherRepository`.
- Existing voucher tables: `voucher_headers` and `voucher_lines`.
- Existing ledger tables: append-only `journal_entries` and `journal_lines`.
  Posting creates their rows transactionally with the voucher status and audit
  entry.
- Existing chart table: `accounts`, currently flat, with 14 legacy accounts.
  The migration adds `account_groups`, `account_headers`, and a required
  `accounts.header_id` relationship without renaming or deleting existing
  account records.
- `fiscal_periods` exists but had no rows. The migration adds the current
  July-June open financial year unless a configured period already overlaps it.
- Cost centers are not implemented in the active schema or application.
- Migration versions **0001–0011** are recorded as applied. **0012** is pending.
  The active database had zero voucher headers and zero journal entries at
  inspection time.
- Migration 0003 creates `company_settings` and `fiscal_periods`; 0008 repeats
  these declarations with `IF NOT EXISTS`. Both are already applied and the
  latter is idempotent. `docs/database/0001_core_draft.sql` is not an active
  migration and describes a different, incompatible chart schema; it must not
  be applied to this database.

## Implementation and files changed

| File | Change |
|---|---|
| `.env.example` | Document optional, dedicated database-backup credentials. |
| `README.md` | Document the six voucher types, migration backup behavior, and migration 0012. |
| `docs/reports/accounting_voucher_system_analysis.md` | This repository/schema analysis and rollout report. |
| `src/app/application/dto.py` | Add voucher type/reference and account-header data fields. |
| `src/app/application/services/account_service.py` | Load account headers and validate header/type on account creation. |
| `src/app/application/services/voucher_pdf_service.py` | Print the correct voucher type and invoice/reference. |
| `src/app/application/services/voucher_service.py` | Validate voucher types, financial periods, accounting-side rules, search, editing, posting and soft deletion. |
| `src/app/domain/accounting/voucher_types.py` | Define supported voucher types and numbering prefixes. |
| `src/app/domain/security/permissions.py` | Add the draft-delete permission. |
| `src/app/domain/workflow.py` | Add the retained `Deleted` status for filtering. |
| `src/app/infrastructure/database/migrator.py` | Require a successful full `pg_dump` backup before any pending migration. |
| `src/app/infrastructure/database/migrations/0012_accounting_vouchers_and_chart.sql` | Add groups/headers, voucher metadata/status, permissions, the default chart and fiscal year. |
| `src/app/infrastructure/repositories/account_repository.py` | Read grouped chart data and validate account headers. |
| `src/app/infrastructure/repositories/voucher_repository.py` | Persist/search voucher types and references, check open periods, and retain deleted drafts. |
| `src/app/ui/accounts_view.py` | Display/select account headers in the chart screen. |
| `src/app/ui/report_headings.py` | Add the account-header column. |
| `src/app/ui/voucher_dialog.py` | Bind voucher type, party, reference, cheque and journal-line inputs. |
| `src/app/ui/vouchers_view.py` | Wire search, listing, draft edit/delete, view, posting and PDF print actions. |
| `tests/integration/test_accounting_voucher_system.py` | Apply migrations in a rolled-back isolated PostgreSQL schema and exercise the lifecycle. |
| `tests/integration/test_voucher_flow.py` | Require migration 0012 for live-schema integration checks. |
| `tests/unit/test_migrator.py` | Verify backup precedes DDL and backup credentials stay out of command arguments. |
| `tests/unit/test_report_standardization.py` | Update the account table contract. |
| `tests/unit/test_voucher_dialog.py` | Verify voucher-type and reference bindings. |
| `tests/unit/test_voucher_pdf_service.py` | Verify dynamic type and reference printing. |
| `tools/check_schema.py` | Check the new chart and voucher columns. |
| `tools/seed_accounts.py` | Align the manual seeder with the canonical chart and account headers. |

The pre-existing modified voucher-template PDF and pre-existing untracked audit
files were not changed by this work.

## Seed data and voucher rules

Migration 0012 creates five account groups and categorized account headers,
then seeds the requested 19 posting accounts idempotently. Existing entries
with matching code/name/type are retained and attached to their header; no
existing account is renamed or deleted. The isolated migration test starts
with the 14 accounts from the legacy chart and verifies all 19 requested names
are present, the original code/name is retained, and every account has a
header.

Voucher numbering uses type prefixes: `JV`, `PV`, `RV`, `CV`, `SV`, and `PU`.
All types require balanced, non-zero debit/credit lines and active accounts.
Payment must credit cash/bank; Receipt must debit cash/bank; Contra transfers
between distinct cash/bank accounts; Sales requires a customer/invoice
reference and debits an asset while crediting income; Purchase requires a
supplier/invoice reference and debits an asset/expense while crediting an
asset/liability. Journal accepts general balanced entries.

Draft deletion is a soft delete (`Deleted` status): details and audit history
are retained and deleted entries are hidden from the default list. Posted
vouchers cannot be edited or deleted; corrections continue to use reversals.

## Backup and migration status

`python -m tools.migrate` attempted the required full backup. `pg_dump` failed
on `public.django_migrations` because the configured application role lacks
read permission. A no-password check with the local PostgreSQL owner also
could not authenticate. The partial dump was removed, and read-only checks
confirmed schema version 11, 14 accounts, zero vouchers, and no new tables.

The migration runner now aborts before DDL if a backup cannot be created. To
apply migration 0012, configure a dedicated full-dump-capable account using
`DB_BACKUP_USER` / `DB_BACKUP_PASSWORD` (or create and verify an equivalent
complete backup through the database administrator), then run
`python -m tools.migrate`. Do not use a partial dump as the migration backup.

## Verification and remaining scope

- Full project test suite: **36 passed, 3 skipped** (the live-schema lifecycle
  tests skip until migration 0012 is applied).
- The new PostgreSQL integration test ran every migration in an isolated
  schema and rolled it back; it verified all six voucher types, balance
  rejection, draft editing, approval/posting, journal and ledger/trial-balance
  output, draft soft deletion, and preservation of existing account rows.
- Cost centers remain unsupported. Sales and Purchase record accounting
  vouchers with party and invoice reference but do not implement stock
  quantities, tax calculations, or a separate customer/supplier subledger.
- The configured database remains at version 11 until a full backup succeeds
  and migration 0012 is explicitly rerun.
