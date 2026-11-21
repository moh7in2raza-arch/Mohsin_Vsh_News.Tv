# Mohsin_Vsh_News.tv - project status report

Generated: 2026-11-20 14:38  |  Folder: C:\Mohsin_Vsh_News.tv

## 1. Tools

```
python : Python 3.12.10
python path : C:\Mohsin_Vsh_News.tv\.venv\Scripts\python.exe
psql   : psql (PostgreSQL) 18.6
ISCC.exe at default path : True
wsl:
    NAME      STATE           VERSION
  * Ubuntu    Stopped         2
```

Key packages in the active environment:
```
argon2-cffi==25.1.0
argon2-cffi-bindings==26.2.0
psycopg==3.3.9
psycopg-binary==3.3.9
pyinstaller==6.22.3
pyinstaller-hooks-contrib==2026.10
PySide6==6.12.0
pytest==9.2.0
python-dotenv==1.2.4
```

## 2. Git

```
branch : main
tags   : login-interface-fix-2026-11-19, phase19-recovery-stable, phase20-start, prototype-sqlite-start, prototype-sqlite-start3, prototype-v0, week6-complete
.venv ignored : .venv

last commits:
  0160220 Fix requirements.txt formatting
  d47bd59 Stop tracking zips and SQLite prototype database
  54ae204 Expand README with project scope and architecture
  2ae07c7 Translate posting errors in voucher service, add tests
  d281fed Fix requirements and project metadata
  a1d7661 Add migration 0009: restrict account manage permission
  e4d52e2 Add migration 0008: company settings and fiscal periods
  b300c55 Fix login window startup flow
  945de33 Phase 20: Register employee service
  5a63dca Phase 19: Employee repository migrated to PostgreSQL

uncommitted changes (git status --short):
   M docs/project_status_report.md
   M widgets.py
  ?? M.R_VSH_NEWS_PROJECT_SETUP_AUDIT.txt
  ?? PROJECT_SETUP_AUDIT.txt
  ?? git-report-latest.txt
```

## 3. Files (src, tests, tools, docs)

```
src\__init__.py                                                                0 bytes  EMPTY
src\app\__init__.py                                                          492 bytes  has content
src\app\bootstrap.py                                                        1132 bytes  has content
src\app\main.py                                                             1442 bytes  has content
src\app\application\__init__.py                                                0 bytes  EMPTY
src\app\application\context.py                                               803 bytes  has content
src\app\application\dto.py                                                  1151 bytes  has content
src\app\application\session.py                                               267 bytes  has content
src\app\application\commands\__init__.py                                       0 bytes  EMPTY
src\app\application\queries\__init__.py                                        0 bytes  EMPTY
src\app\application\security\__init__.py                                       0 bytes  EMPTY
src\app\application\services\__init__.py                                       0 bytes  EMPTY
src\app\application\services\account_service.py                             1939 bytes  has content
src\app\application\services\auth_service.py                                2652 bytes  has content
src\app\application\services\employee_service.py                            1069 bytes  has content
src\app\application\services\permission_service.py                           363 bytes  has content
src\app\application\services\posting_service.py                             1055 bytes  has content
src\app\application\services\report_service.py                              1731 bytes  has content
src\app\application\services\voucher_service.py                             7226 bytes  has content
src\app\domain\__init__.py                                                     0 bytes  EMPTY
src\app\domain\workflow.py                                                   473 bytes  has content
src\app\domain\accounting\__init__.py                                          0 bytes  EMPTY
src\app\domain\accounting\chart.py                                           453 bytes  has content
src\app\domain\accounting\journal.py                                        1507 bytes  has content
src\app\domain\accounting\money.py                                           677 bytes  has content
src\app\domain\audit\__init__.py                                               0 bytes  EMPTY
src\app\domain\hr\__init__.py                                                  0 bytes  EMPTY
src\app\domain\hr\employee.py                                               1091 bytes  has content
src\app\domain\inventory\__init__.py                                           0 bytes  EMPTY
src\app\domain\payroll\__init__.py                                             0 bytes  EMPTY
src\app\domain\security\__init__.py                                            0 bytes  EMPTY
src\app\domain\security\permissions.py                                       542 bytes  has content
src\app\infrastructure\__init__.py                                             0 bytes  EMPTY
src\app\infrastructure\backup\__init__.py                                      0 bytes  EMPTY
src\app\infrastructure\database\__init__.py                                    0 bytes  EMPTY
src\app\infrastructure\database\connection.py                                854 bytes  has content
src\app\infrastructure\database\migrator.py                                 1470 bytes  has content
src\app\infrastructure\database\unit_of_work.py                             1820 bytes  has content
src\app\infrastructure\database\migrations\__init__.py                         0 bytes  EMPTY
src\app\infrastructure\database\migrations\0001_core.sql                    2786 bytes  has content
src\app\infrastructure\database\migrations\0002_hr.sql                       572 bytes  has content
src\app\infrastructure\database\migrations\0003_administration.sql           549 bytes  has content
src\app\infrastructure\database\migrations\0004_vouchers.sql                 527 bytes  has content
src\app\infrastructure\database\migrations\0005_journal.sql                  870 bytes  has content
src\app\infrastructure\database\migrations\0006_accounting_integrity.sql    2530 bytes  has content
src\app\infrastructure\database\migrations\0007_employee_profile.sql         992 bytes  has content
src\app\infrastructure\database\migrations\0008_company_settings_fiscal_periods.sql    1035 bytes  has content
src\app\infrastructure\database\migrations\0009_restrict_account_manage.sql     260 bytes  has content
src\app\infrastructure\logging\__init__.py                                     0 bytes  EMPTY
src\app\infrastructure\logging\setup.py                                      623 bytes  has content
src\app\infrastructure\reports\__init__.py                                     0 bytes  EMPTY
src\app\infrastructure\repositories\__init__.py                                0 bytes  EMPTY
src\app\infrastructure\repositories\_sql.py                                  375 bytes  has content
src\app\infrastructure\repositories\account_repository.py                   1210 bytes  has content
src\app\infrastructure\repositories\audit_repository.py                      347 bytes  has content
src\app\infrastructure\repositories\employee_repository.py                  3696 bytes  has content
src\app\infrastructure\repositories\permission_repository.py                 524 bytes  has content
src\app\infrastructure\repositories\report_repository.py                    1651 bytes  has content
src\app\infrastructure\repositories\user_repository.py                      1035 bytes  has content
src\app\infrastructure\repositories\voucher_repository.py                   4098 bytes  has content
src\app\ui\__init__.py                                                         0 bytes  EMPTY
src\app\ui\accounts_view.py                                                 2948 bytes  has content
src\app\ui\dashboard_view.py                                                8479 bytes  has content
src\app\ui\employees_view.py                                                1759 bytes  has content
src\app\ui\login_window_backup.py                                           2498 bytes  has content
src\app\ui\login_window.py                                                 13548 bytes  has content
src\app\ui\main_window.py                                                   6190 bytes  has content
src\app\ui\main_window.py.backup                                            2708 bytes  has content
src\app\ui\reports_view.py                                                  5752 bytes  has content
src\app\ui\style.py                                                         1808 bytes  has content
src\app\ui\support.py                                                       3899 bytes  has content
src\app\ui\voucher_dialog.py                                                4728 bytes  has content
src\app\ui\vouchers_view.py                                                 6000 bytes  has content
tests\test_posting.py                                                       1402 bytes  has content
tests\accounting\.gitkeep                                                      2 bytes  has content
tests\integration\.gitkeep                                                     2 bytes  has content
tests\integration\test_voucher_flow.py                                      4265 bytes  has content
tests\unit\.gitkeep                                                            2 bytes  has content
tests\unit\test_journal.py                                                  1751 bytes  has content
tests\unit\test_money.py                                                     596 bytes  has content
tests\unit\test_shell_smoke.py                                               781 bytes  has content
tests\unit\test_voucher_service.py                                          1232 bytes  has content
tests\unit\test_workflow.py                                                  291 bytes  has content
tools\__init__.py                                                              0 bytes  EMPTY
tools\build_exe.ps1                                                         1917 bytes  has content
tools\check_db.py                                                            894 bytes  has content
tools\check_schema.py                                                       2382 bytes  has content
tools\migrate.py                                                             187 bytes  has content
tools\project_report.ps1                                                    5423 bytes  has content
tools\seed_accounts.py                                                      1262 bytes  has content
docs\project_status_report.md                                              13332 bytes  has content
docs\database\0001_core_draft.sql                                           8057 bytes  has content
docs\decisions\ADR-0001-canonical-technology-stack.md                       1381 bytes  has content
docs\hr_prototype\index.html                                                   0 bytes  EMPTY
docs\hr_prototype\README.txt                                                   0 bytes  EMPTY
docs\hr_prototype\reference-template.docx                                      0 bytes  EMPTY
```

Total files: 96  |  empty: 25  |  with content: 71

## 4. SQL files

```
erp_office_phase3.sql                                                               1388 bytes
AUDIT_RECORDS\backup_before_employee_module\app\infrastructure\database\migrations\0007_employee_profile.sql     992 bytes
AUDIT_RECORDS\backup_before_employee_module\migrations\0001_core.sql                2786 bytes
AUDIT_RECORDS\backup_before_employee_module\migrations\0002_hr.sql                   572 bytes
AUDIT_RECORDS\backup_before_employee_module\migrations\0003_administration.sql       549 bytes
AUDIT_RECORDS\backup_before_employee_module\migrations\0004_vouchers.sql             527 bytes
AUDIT_RECORDS\backup_before_employee_module\migrations\0005_journal.sql              870 bytes
AUDIT_RECORDS\backup_before_employee_module\migrations\0006_accounting_integrity.sql    2530 bytes
docs\database\0001_core_draft.sql                                                   8057 bytes
src\app\infrastructure\database\migrations\0001_core.sql                            2786 bytes
src\app\infrastructure\database\migrations\0002_hr.sql                               572 bytes
src\app\infrastructure\database\migrations\0003_administration.sql                   549 bytes
src\app\infrastructure\database\migrations\0004_vouchers.sql                         527 bytes
src\app\infrastructure\database\migrations\0005_journal.sql                          870 bytes
src\app\infrastructure\database\migrations\0006_accounting_integrity.sql            2530 bytes
src\app\infrastructure\database\migrations\0007_employee_profile.sql                 992 bytes
src\app\infrastructure\database\migrations\0008_company_settings_fiscal_periods.sql    1035 bytes
src\app\infrastructure\database\migrations\0009_restrict_account_manage.sql          260 bytes
```

## 5. Tests (pytest -q)

```
.......................                                                  [100%]
23 passed in 3.12s
```

## 6. Database erp_office (read-only queries, as erp_app)

```
psql: error: connection to server at "localhost" (::1), port 5432 failed: FATAL:  password authentication failed for user "erp_app"
```
