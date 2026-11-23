# Mohsin_Vsh_News.tv - project status report

Generated: 2026-11-23 17:59  |  Folder: C:\Mohsin_Vsh_News.tv

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
tags   : backup-feature-employee-postgresql, backup-feature-next-step, backup-phase19-recovery, backup-recovery-backup, backup-rescue, backup-rescue-week6, checkpoint-before-cleanup, login-interface-fix-2026-11-19, phase19-recovery-stable, phase20-start, phase21-adr-consolidation, prototype-sqlite-start, prototype-sqlite-start3, prototype-v0, week6-complete
.venv ignored : .venv

last commits:
  ab7338a Step 2: move reports, SQL draft and backup files out of root and ui
  8c60259 Checkpoint before structure cleanup
  16753a3 Start dashboard service and users module ADR route
  5fc11b9 Generate ADR canonical tree
  90f0f03 ADR cleanup phase 2 remove duplicate UI routes
  c924d47 ADR consolidation: archive duplicate dashboards UI and SQLite route
  0160220 Fix requirements.txt formatting
  d47bd59 Stop tracking zips and SQLite prototype database
  54ae204 Expand README with project scope and architecture
  2ae07c7 Translate posting errors in voucher service, add tests

uncommitted changes (git status --short):
   D config/__init__.py
   D config/asgi.py
   D config/settings.py
   D config/urls.py
   D config/wsgi.py
   D create_first_admin.py
   M docs/project_status_report.md
   D manage.py
   M src/app/application/context.py
   M src/app/application/dto.py
   M src/app/application/services/report_service.py
   M src/app/bootstrap.py
   M src/app/infrastructure/database/unit_of_work.py
   M src/app/infrastructure/repositories/report_repository.py
  ?? archive/obsolete_django/
  ?? src/app/application/services/company_service.py
  ?? src/app/infrastructure/database/migrations/0010_company_and_statement_fields.sql
  ?? src/app/infrastructure/repositories/company_repository.py
  ?? src/app/ui/admin_views.py
  ?? tools/create_first_admin.py
  ?? tools/wire_company_and_ledger.py
```

## 3. Files (src, tests, tools, docs)

```
src\__init__.py                                                                0 bytes  EMPTY
src\app\bootstrap.py                                                        1197 bytes  has content
src\app\main.py                                                             1674 bytes  has content
src\app\__init__.py                                                          492 bytes  has content
src\app\application\context.py                                               846 bytes  has content
src\app\application\dto.py                                                  1417 bytes  has content
src\app\application\session.py                                               267 bytes  has content
src\app\application\__init__.py                                                0 bytes  EMPTY
src\app\application\commands\__init__.py                                       0 bytes  EMPTY
src\app\application\queries\__init__.py                                        0 bytes  EMPTY
src\app\application\security\__init__.py                                       0 bytes  EMPTY
src\app\application\services\account_service.py                             1939 bytes  has content
src\app\application\services\auth_service.py                                2652 bytes  has content
src\app\application\services\company_service.py                             2222 bytes  has content
src\app\application\services\dashboard_service.py                            652 bytes  has content
src\app\application\services\employee_service.py                            1069 bytes  has content
src\app\application\services\permission_service.py                           363 bytes  has content
src\app\application\services\posting_service.py                             1055 bytes  has content
src\app\application\services\report_service.py                              2267 bytes  has content
src\app\application\services\user_service.py                                   0 bytes  EMPTY
src\app\application\services\voucher_service.py                             7226 bytes  has content
src\app\application\services\__init__.py                                       0 bytes  EMPTY
src\app\domain\workflow.py                                                   473 bytes  has content
src\app\domain\__init__.py                                                     0 bytes  EMPTY
src\app\domain\accounting\chart.py                                           453 bytes  has content
src\app\domain\accounting\journal.py                                        1507 bytes  has content
src\app\domain\accounting\money.py                                           677 bytes  has content
src\app\domain\accounting\__init__.py                                          0 bytes  EMPTY
src\app\domain\audit\__init__.py                                               0 bytes  EMPTY
src\app\domain\hr\employee.py                                               1091 bytes  has content
src\app\domain\hr\__init__.py                                                  0 bytes  EMPTY
src\app\domain\inventory\__init__.py                                           0 bytes  EMPTY
src\app\domain\payroll\__init__.py                                             0 bytes  EMPTY
src\app\domain\security\permissions.py                                       542 bytes  has content
src\app\domain\security\user.py                                                0 bytes  EMPTY
src\app\domain\security\__init__.py                                            0 bytes  EMPTY
src\app\infrastructure\__init__.py                                             0 bytes  EMPTY
src\app\infrastructure\backup\__init__.py                                      0 bytes  EMPTY
src\app\infrastructure\database\connection.py                                854 bytes  has content
src\app\infrastructure\database\migrator.py                                 1470 bytes  has content
src\app\infrastructure\database\unit_of_work.py                             1960 bytes  has content
src\app\infrastructure\database\__init__.py                                    0 bytes  EMPTY
src\app\infrastructure\database\migrations\0001_core.sql                    2786 bytes  has content
src\app\infrastructure\database\migrations\0002_hr.sql                       572 bytes  has content
src\app\infrastructure\database\migrations\0003_administration.sql           549 bytes  has content
src\app\infrastructure\database\migrations\0004_vouchers.sql                 527 bytes  has content
src\app\infrastructure\database\migrations\0005_journal.sql                  870 bytes  has content
src\app\infrastructure\database\migrations\0006_accounting_integrity.sql    2530 bytes  has content
src\app\infrastructure\database\migrations\0007_employee_profile.sql         992 bytes  has content
src\app\infrastructure\database\migrations\0008_company_settings_fiscal_periods.sql    1035 bytes  has content
src\app\infrastructure\database\migrations\0009_restrict_account_manage.sql     260 bytes  has content
src\app\infrastructure\database\migrations\0010_company_and_statement_fields.sql     798 bytes  has content
src\app\infrastructure\database\migrations\__init__.py                         0 bytes  EMPTY
src\app\infrastructure\logging\setup.py                                      623 bytes  has content
src\app\infrastructure\logging\__init__.py                                     0 bytes  EMPTY
src\app\infrastructure\reports\__init__.py                                     0 bytes  EMPTY
src\app\infrastructure\repositories\account_repository.py                   1210 bytes  has content
src\app\infrastructure\repositories\audit_repository.py                      347 bytes  has content
src\app\infrastructure\repositories\company_repository.py                   1568 bytes  has content
src\app\infrastructure\repositories\employee_repository.py                  3696 bytes  has content
src\app\infrastructure\repositories\permission_repository.py                 524 bytes  has content
src\app\infrastructure\repositories\report_repository.py                    1908 bytes  has content
src\app\infrastructure\repositories\user_repository.py                      1035 bytes  has content
src\app\infrastructure\repositories\voucher_repository.py                   4098 bytes  has content
src\app\infrastructure\repositories\_sql.py                                  375 bytes  has content
src\app\infrastructure\repositories\__init__.py                                0 bytes  EMPTY
src\app\ui\accounts_view.py                                                 6346 bytes  has content
src\app\ui\admin_views.py                                                  10672 bytes  has content
src\app\ui\dashboard_view.py                                                9084 bytes  has content
src\app\ui\employees_view.py                                                1759 bytes  has content
src\app\ui\login_window.py                                                 10734 bytes  has content
src\app\ui\main_window.py                                                  11386 bytes  has content
src\app\ui\module_shell.py                                                  7446 bytes  has content
src\app\ui\reports_view.py                                                  5752 bytes  has content
src\app\ui\style.py                                                         1808 bytes  has content
src\app\ui\support.py                                                       5315 bytes  has content
src\app\ui\users_view.py                                                    7975 bytes  has content
src\app\ui\vouchers_view.py                                                 6000 bytes  has content
src\app\ui\voucher_dialog.py                                                4728 bytes  has content
src\app\ui\__init__.py                                                         0 bytes  EMPTY
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
tools\apply_updates.py                                                     12148 bytes  has content
tools\build_exe.ps1                                                         1917 bytes  has content
tools\check_db.py                                                            894 bytes  has content
tools\check_schema.py                                                       2382 bytes  has content
tools\create_first_admin.py                                                 1702 bytes  has content
tools\migrate.py                                                             187 bytes  has content
tools\project_report.ps1                                                    5423 bytes  has content
tools\seed_accounts.py                                                      1262 bytes  has content
tools\wire_company_and_ledger.py                                           11677 bytes  has content
tools\__init__.py                                                              0 bytes  EMPTY
docs\ADR_CANONICAL_TREE.txt                                                 6583 bytes  has content
docs\Balochistan ERP Finance Dashboard.png                               2063497 bytes  has content
docs\project_status_report.md                                              19283 bytes  has content
docs\src_structure.txt                                                      5919 bytes  has content
docs\database\0001_core_draft.sql                                           8057 bytes  has content
docs\database\erp_office_phase3.sql                                         1388 bytes  has content
docs\decisions\ADR-0001-canonical-technology-stack.md                       1381 bytes  has content
docs\hr_prototype\index.html                                                   0 bytes  EMPTY
docs\hr_prototype\README.txt                                                   0 bytes  EMPTY
docs\hr_prototype\reference-template.docx                                      0 bytes  EMPTY
docs\reports\git-report-latest.txt                                           944 bytes  has content
docs\reports\git_report.txt                                                11195 bytes  has content
docs\reports\M.R_VSH_NEWS_PROJECT_SETUP_AUDIT.txt                          17500 bytes  has content
docs\reports\PROJECT_COMPLETE_STATUS_REPORT.txt                            41528 bytes  has content
docs\reports\PROJECT_PYTHON_FILES.txt                                     232823 bytes  has content
docs\reports\project_report.txt                                             8390 bytes  has content
docs\reports\PROJECT_SETUP_AUDIT.txt                                       21534 bytes  has content
docs\reports\project_structure.txt                                       1016981 bytes  has content
docs\reports\PROJECT_STRUCTURE_FULL.txt                                   615962 bytes  has content
```

Total files: 119  |  empty: 27  |  with content: 92

## 4. SQL files

```
AUDIT_RECORDS\backup_before_employee_module\app\infrastructure\database\migrations\0007_employee_profile.sql     992 bytes
AUDIT_RECORDS\backup_before_employee_module\migrations\0001_core.sql                2786 bytes
AUDIT_RECORDS\backup_before_employee_module\migrations\0002_hr.sql                   572 bytes
AUDIT_RECORDS\backup_before_employee_module\migrations\0003_administration.sql       549 bytes
AUDIT_RECORDS\backup_before_employee_module\migrations\0004_vouchers.sql             527 bytes
AUDIT_RECORDS\backup_before_employee_module\migrations\0005_journal.sql              870 bytes
AUDIT_RECORDS\backup_before_employee_module\migrations\0006_accounting_integrity.sql    2530 bytes
docs\database\0001_core_draft.sql                                                   8057 bytes
docs\database\erp_office_phase3.sql                                                 1388 bytes
src\app\infrastructure\database\migrations\0001_core.sql                            2786 bytes
src\app\infrastructure\database\migrations\0002_hr.sql                               572 bytes
src\app\infrastructure\database\migrations\0003_administration.sql                   549 bytes
src\app\infrastructure\database\migrations\0004_vouchers.sql                         527 bytes
src\app\infrastructure\database\migrations\0005_journal.sql                          870 bytes
src\app\infrastructure\database\migrations\0006_accounting_integrity.sql            2530 bytes
src\app\infrastructure\database\migrations\0007_employee_profile.sql                 992 bytes
src\app\infrastructure\database\migrations\0008_company_settings_fiscal_periods.sql    1035 bytes
src\app\infrastructure\database\migrations\0009_restrict_account_manage.sql          260 bytes
src\app\infrastructure\database\migrations\0010_company_and_statement_fields.sql     798 bytes
```

## 5. Tests (pytest -q)

```
.......................                                                  [100%]
23 passed in 1.07s
```

## 6. Database erp_office (read-only queries, as erp_app)

```
--- schema_version
 version |                   name                   |          applied_at           
---------+------------------------------------------+-------------------------------
       1 | 0001_core.sql                            | 2026-11-10 15:15:43.198791+05
       2 | 0002_hr.sql                              | 2026-11-12 15:23:46.980471+05
       3 | 0003_administration.sql                  | 2026-11-12 15:29:01.861586+05
       4 | 0004_vouchers.sql                        | 2026-11-12 15:32:33.408087+05
       5 | 0005_journal.sql                         | 2026-11-14 20:59:22.081332+05
       6 | 0006_accounting_integrity.sql            | 2026-11-14 20:59:22.081332+05
       7 | 0007_employee_profile.sql                | 2026-11-17 19:50:40.765857+05
       8 | 0008_company_settings_fiscal_periods.sql | 2026-11-19 15:28:25.716312+05
       9 | 0009_restrict_account_manage.sql         | 2026-11-19 15:31:42.749699+05
      10 | 0010_company_and_statement_fields.sql    | 2026-11-21 19:58:54.727368+05
(10 rows)

--- tables and owners
         tablename          | tableowner 
----------------------------+------------
 accounts                   | erp_app
 assets                     | erp_app
 audit_log                  | erp_app
 auth_group                 | postgres
 auth_group_permissions     | postgres
 auth_permission            | postgres
 auth_user                  | postgres
 auth_user_groups           | postgres
 auth_user_user_permissions | postgres
 company_settings           | erp_app
 departments                | erp_app
 django_admin_log           | postgres
 django_content_type        | postgres
 django_migrations          | postgres
 django_session             | postgres
 employees                  | erp_app
 fiscal_periods             | erp_app
 inventory_items            | erp_app
 journal_entries            | erp_app
 journal_lines              | erp_app
 permissions                | erp_app
 role_permissions           | erp_app
 roles                      | erp_app
 schema_version             | erp_app
 user_roles                 | erp_app
 users                      | erp_app
 voucher_headers            | erp_app
 voucher_lines              | erp_app
(28 rows)

--- accounts columns
  column_name   | data_type 
----------------+-----------
 id             | bigint
 code           | text
 name           | text
 type           | text
 normal_balance | character
 is_active      | boolean
(6 rows)

--- row counts
 table_name  | count 
-------------+-------
 accounts    |    14
 users       |     2
 roles       |     5
 permissions |    20
(4 rows)

```
