VSH ERP dashboard add-on — integration for the supplied project

This package is an add-on to the existing ERP, not a separate application.

Verified against the user's current source excerpts:
- MainWindow(services, session)
- Session has username, permissions and has(code)
- Existing permission constants: VOUCHER_VIEW, ACCOUNT_VIEW, REPORT_VIEW
- Existing views accept (services, session)
- Existing auth logout call: services.auth.logout()

Files:
- src/app/ui/dashboard_view.py
- src/app/ui/main_window.py

Install only after backing up the existing main_window.py:
1. Copy dashboard_view.py into:
   C:\Mohsin_Vsh_News.tv\src\app\ui\dashboard_view.py
2. Copy main_window.py into:
   C:\Mohsin_Vsh_News.tv\src\app\ui\main_window.py
3. Keep the logo at either:
   C:\Mohsin_Vsh_News.tv\assets\vsh_logo.png.png
   or C:\Mohsin_Vsh_News.tv\vsh_logo.png.png
4. Run the project's normal approved launcher.

This uses the current session and existing permission constants; no changes
to Session, permissions, database, services, or migrations are required.

Only the existing Vouchers, Chart of accounts and Reports screens are wired.
HR, Payroll, Attendance, Users/Roles and Operations are shown as planned
shortcuts and report that they are not yet connected. KPI tiles do not invent
financial figures. Live totals require application-service queries.

The dashboard is UI-only and makes no direct database calls. The supplied
source excerpt did not establish role names beyond permission codes, so the
workspace label is inferred from permissions rather than assuming role data.
