# ADR-001: Canonical Technology Stack

Status: Approved
Project: ERP Office Management
Project Root: C:\Mohsin_Vsh_News.tv

## 1. Platform Requirements
- Windows 10 64-bit, version 2004 or later, build 19041+.
- Hyper-V virtualization support.
- WSL2 mandatory.

## 2. Development Stack
- Python 3.12, 64-bit.
- Python executable added to system PATH.
- PySide6 desktop application framework.
- PostgreSQL database.
- Visual Studio Code with interactive debugging.
- Inno Setup 6.3 or higher.

## 3. Installer Compiler
Required deployment path:
C:\Program Files (x86)\Inno Setup 6\ISCC.exe

Existing compiler location to verify:
C:\Users\HP\Downloads\VSH_Accounting\Inno Setup 6\ISCC.exe

## 4. Application Architecture
- ui/
- application/
- domain/
- infrastructure/

The UI must not execute SQL directly.
Repositories are responsible for SQL execution.
Application services enforce permissions and coordinate workflows.
Domain modules contain business rules independent of UI and database.
Critical business operations and audit records must share a database transaction.
Accounting must follow double-entry principles.

## 5. Approval Gate
This decision must be reviewed and approved before Phase 1 is marked complete.
No alternative technology stack may be substituted without explicit approval.

