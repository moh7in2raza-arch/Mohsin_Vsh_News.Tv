# Mohsin_Vsh_News.tv - project status report

Generated: 2026-11-14 15:27  |  Folder: C:\Mohsin_Vsh_News.tv

## 1. Tools

```
python : Python 3.12.10
python path : C:\Mohsin_Vsh_News.tv\venv\Scripts\python.exe
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
pyinstaller==6.22.3
pyinstaller-hooks-contrib==2026.10
PySide6==6.12.0
pytest==9.2.0
```

## 2. Git

```
branch : master
tags   : prototype-v0, week6-complete
.venv ignored : 

last commits:
  e612d07 Add journal and audit schema
  6699289 Add voucher repository skeleton
  5dadf03 Recover missing migration files
  c227786 Add posting validation rules
  3c36b35 Create posting service with posting tests
  670b792 Clean startup configuration and environment setup
  0d089ea Weeks 5-6 start: permission service, workflow, voucher service skeleton, project report script
  0314e84 Authentication milestone complete
  86388b7 ADR-001: environment verified and approved
  1676106 Add money helpers with tests

uncommitted changes (git status --short):
  R  docs/decisions/ADR-001-canonical-technology-stack.md -> docs/Decisions/ADR-0001-canonical-technology-stack.md
  M  src/app/infrastructure/repositories/voucher_repository.py
```

## 3. Files (src, tests, tools, docs)

```
src\__init__.py                                                                0 bytes  EMPTY
src\app\main.py                                                              281 bytes  has content
src\app\__init__.py                                                          492 bytes  has content
src\app\application\__init__.py                                                0 bytes  EMPTY
src\app\application\commands\__init__.py                                       0 bytes  EMPTY
src\app\application\queries\__init__.py                                        0 bytes  EMPTY
src\app\application\security\__init__.py                                       0 bytes  EMPTY
src\app\application\services\auth_service.py                                1075 bytes  has content
src\app\application\services\permission_service.py                           363 bytes  has content
src\app\application\services\posting_service.py                             1055 bytes  has content
src\app\application\services\voucher_service.py                              545 bytes  has content
src\app\application\services\__init__.py                                       0 bytes  EMPTY
src\app\domain\workflow.py                                                   473 bytes  has content
src\app\domain\__init__.py                                                     0 bytes  EMPTY
src\app\domain\accounting\money.py                                           677 bytes  has content
src\app\domain\accounting\__init__.py                                          0 bytes  EMPTY
src\app\domain\audit\__init__.py                                               0 bytes  EMPTY
src\app\domain\hr\__init__.py                                                  0 bytes  EMPTY
src\app\domain\inventory\__init__.py                                           0 bytes  EMPTY
src\app\domain\payroll\__init__.py                                             0 bytes  EMPTY
src\app\infrastructure\__init__.py                                             0 bytes  EMPTY
src\app\infrastructure\backup\__init__.py                                      0 bytes  EMPTY
src\app\infrastructure\database\connection.py                                574 bytes  has content
src\app\infrastructure\database\migrator.py                                 1428 bytes  has content
src\app\infrastructure\database\__init__.py                                    0 bytes  EMPTY
src\app\infrastructure\database\migrations\0001_core.sql                    2717 bytes  has content
src\app\infrastructure\database\migrations\0002_hr.sql                       572 bytes  has content
src\app\infrastructure\database\migrations\0003_administration.sql           549 bytes  has content
src\app\infrastructure\database\migrations\0004_vouchers.sql                 527 bytes  has content
src\app\infrastructure\database\migrations\0005_journal.sql                  870 bytes  has content
src\app\infrastructure\database\migrations\__init__.py                      8057 bytes  has content
src\app\infrastructure\logging\__init__.py                                     0 bytes  EMPTY
src\app\infrastructure\reports\__init__.py                                     0 bytes  EMPTY
src\app\infrastructure\repositories\user_repository.py                      1035 bytes  has content
src\app\infrastructure\repositories\voucher_repository.py                    581 bytes  has content
src\app\infrastructure\repositories\__init__.py                                0 bytes  EMPTY
src\app\ui\login_window.py                                                   731 bytes  has content
src\app\ui\__init__.py                                                         0 bytes  EMPTY
tests\test_posting.py                                                       1402 bytes  has content
tests\accounting\.gitkeep                                                      2 bytes  has content
tests\integration\.gitkeep                                                     2 bytes  has content
tests\unit\.gitkeep                                                            2 bytes  has content
tests\unit\test_money.py                                                     572 bytes  has content
tests\unit\test_workflow.py                                                  291 bytes  has content
tools\check_db.py                                                            865 bytes  has content
tools\migrate.py                                                             183 bytes  has content
tools\project_report.ps1                                                    5423 bytes  has content
docs\project_status_report.md                                               7469 bytes  has content
docs\Decisions\ADR-0001-canonical-technology-stack.md                       1381 bytes  has content
```

Total files: 49  |  empty: 19  |  with content: 30

## 4. SQL files

```
erp_office_phase3.sql                                                               1316 bytes
src\app\infrastructure\database\migrations\0001_core.sql                            2717 bytes
src\app\infrastructure\database\migrations\0002_hr.sql                               572 bytes
src\app\infrastructure\database\migrations\0003_administration.sql                   549 bytes
src\app\infrastructure\database\migrations\0004_vouchers.sql                         527 bytes
src\app\infrastructure\database\migrations\0005_journal.sql                          870 bytes
```

## 5. Tests (pytest -q)

```
...........                                                              [100%]
11 passed in 0.05s
```

## 6. Database erp_office (read-only queries, as erp_app)

```
--- schema_version
 version |          name           |          applied_at           
---------+-------------------------+-------------------------------
       1 | 0001_core.sql           | 2026-11-10 15:15:43.198791+05
       2 | 0002_hr.sql             | 2026-11-12 15:23:46.980471+05
       3 | 0003_administration.sql | 2026-11-12 15:29:01.861586+05
       4 | 0004_vouchers.sql       | 2026-11-12 15:32:33.408087+05
(4 rows)

--- tables and owners
    tablename     | tableowner 
------------------+------------
 accounts         | erp_app
 assets           | erp_app
 departments      | erp_app
 employees        | erp_app
 inventory_items  | erp_app
 permissions      | erp_app
 role_permissions | erp_app
 roles            | erp_app
 schema_version   | erp_app
 user_roles       | erp_app
 users            | erp_app
 voucher_headers  | erp_app
 voucher_lines    | erp_app
(13 rows)

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
 accounts    |     0
 users       |     1
 roles       |     5
 permissions |    15
(4 rows)

```
