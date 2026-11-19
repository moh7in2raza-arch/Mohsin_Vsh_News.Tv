# ERP Office Management

Desktop ERP for **VSH NEWS TV** (Visionary Balochistan Media Corporation (Pvt.) Limited).
Native Windows application: double-entry accounting, HR and administration, built on PySide6 and PostgreSQL.

The rulebook for every technical decision is
[`docs/decisions/ADR-001-canonical-technology-stack.md`](docs/decisions/ADR-001-canonical-technology-stack.md).
No stack substitution without explicit approval.

---

## Scope

| Module | What it covers |
|---|---|
| **Accounts** | Chart of accounts, vouchers (Payment first, then Receipt, Journal, Contra), posting to the journal, ledger, trial balance, reports |
| **HR** | One record per employee covering the whole life cycle (joining, documents, working record, exit); status changes (active, resigned, terminated, completed); office letters and applications printed on the company letterhead |
| **Admin** | Setup layer: users, roles, permissions, company settings, fiscal periods, backup and restore |

Broadcast and TV operations are **not** in the current build. The structure keeps room for a broadcast module later.
The fiscal year runs **1 July to 30 June**.

---

## Technology stack (ADR-001)

| Item | Choice |
|---|---|
| Language | Python 3.12, 64-bit |
| UI | PySide6 (native desktop) |
| Database | PostgreSQL 18, accessed with psycopg 3 |
| Password hashing | argon2-cffi |
| Tests | pytest |
| Packaging | PyInstaller, Inno Setup 6.3+ |
| Editor | VS Code |
| Platform | Windows 10/11, WSL2 required |

---

## Architecture rules

The code is split into four layers under `src/app/`:

```
ui  ->  application  ->  domain
              |
        infrastructure
```

1. The **UI never touches the database.** It only calls application services.
2. **Services enforce every rule** and re-check permissions on every call. Hiding a button is cosmetic only.
3. **Only repositories write SQL.**
4. The **domain layer** holds money math and workflow rules. It is testable without a window or a database.
5. Every important action writes an **audit record in the same transaction** as the action itself.
6. Accounting is **double-entry**. Invariants are enforced by triggers inside PostgreSQL.

---

## Repository layout

```
src/app/
  ui/                  PySide6 windows, views, dialogs, theme
  application/         services (auth, permission, account, voucher, posting, employee, report)
  domain/              accounting, hr, security, workflow (pure logic)
  infrastructure/
    database/          connection, migrator, unit of work, migrations/*.sql
    repositories/      all SQL lives here
    logging/ backup/ reports/
  bootstrap.py  main.py
tests/                 unit/ integration/ accounting/
tools/                 migrate, check_db, check_schema, seed_accounts, build_exe.ps1, project_report.ps1
build/                 PyInstaller spec, Inno Setup script
docs/                  decisions (ADR), database drafts, status report
assets/                logo and images
archive/               reference only; do not edit or run
run.py                 application entry point
```

---

## Getting started

### Prerequisites

- Windows 10 or 11 with Python 3.12 (64-bit) on `PATH`
- PostgreSQL 18 with `psql` on `PATH`
- Git, VS Code
- For release builds: Inno Setup 6.3+ and WSL2

### Setup

```powershell
git clone https://github.com/moh7in2raza-arch/Mohsin_Vsh_News.Tv.git C:\Mohsin_Vsh_News.tv
cd C:\Mohsin_Vsh_News.tv

python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Database

Create the role and database once (as the `postgres` user):

```sql
CREATE ROLE erp_app LOGIN PASSWORD 'choose-a-strong-password';
CREATE DATABASE erp_office OWNER erp_app;
```

Copy `.env.example` to `.env` and fill in the connection settings:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=erp_office
DB_USER=erp_app
DB_PASSWORD=...
```

`.env` holds secrets and must never be committed.

Apply the migrations and check the result:

```powershell
python -m tools.migrate
python -m tools.check_db
python -m tools.check_schema
```

### Run

```powershell
python run.py
```

### Test

```powershell
python -m pytest -q
```

Use the project's `.venv` interpreter. System Python does not have pytest.

---

## Database migrations

Migrations live in `src/app/infrastructure/database/migrations/` and are applied in order by `tools.migrate`.
Applied versions are recorded in the `schema_version` table.
Take a backup before applying a migration to a database that holds real data.

| Version | Content |
|---|---|
| 0001 | Core: users, roles, permissions |
| 0002 | HR |
| 0003 | Administration |
| 0004 | Vouchers |
| 0005 | Journal and audit |
| 0006 | Accounting integrity |
| 0007 | Employee profile |
| 0008 | Company settings and fiscal periods, finance grants |
| 0009 | `account.manage` restricted to Accountant and Admin |

---

## Building a release

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\build_exe.ps1
```

The installer script is `build/installer.iss`; compile it with Inno Setup (`ISCC.exe`).
Release builds must be tested by installing on a clean Windows machine before they are handed out.

---

## Status report

A read-only report of tools, git state, files, migrations, tests and database state:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\tools\project_report.ps1
```

Use `-SkipDb` to skip the database section. The output is written to `docs/project_status_report.md`.

---

## Roadmap

| Step | Goal | Status |
|---|---|---|
| 1 | Decide and document the canonical stack (ADR-001) | Done |
| 2 | One product source; everything else archived | In progress |
| 3 | Entry point, dependencies, setup, tests | Done |
| 4 | Authentication, authorization, workflows, account mapping | Done for current modules |
| 5 | Test calculations, backup and restore | In progress |
| 6 | Windows release build and install validation | Not started |

Next work: load the real chart of accounts, wire the new dashboard to the services, finish the voucher types, build the HR letters module, and validate the installer.

---

## Contributing

- Work on `master`, in small commits with clear messages.
- Run `python -m pytest -q` before every commit.
- New code goes under `src/`. Anything in `archive/` is reference only.
- A change to the stack or the architecture rules needs a new ADR.