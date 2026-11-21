VSH NEWS TV ERP dashboard integration

Package contents:
- src/app/ui/dashboard_view.py (new role-aware dashboard page)
- src/app/ui/main_window.py (replacement main window wired to dashboard + existing pages)

Install:
1. Close the ERP application.
2. Back up these existing files:
   C:\Mohsin_Vsh_News.tv\src\app\ui\main_window.py
3. Copy the two package files into the matching paths under:
   C:\Mohsin_Vsh_News.tv\src\app\ui\
4. Confirm the logo is at either:
   C:\Mohsin_Vsh_News.tv\assets\vsh_logo.png.png
   or C:\Mohsin_Vsh_News.tv\vsh_logo.png.png
5. Run your normal project entry point (the existing run.py / approved launcher).

Notes:
- This follows ADR-0001: PySide6 UI only; no SQL or direct database calls in dashboard.
- The current Session model has permissions but no role-name field. The dashboard therefore infers a workspace label from permission codes, rather than inventing a role.
- Only currently wired screens (Vouchers, Chart of Accounts, Reports) open. HR, Payroll, Attendance, Users/Roles and Operations shortcuts clearly report that their modules are not yet connected.
- Summary tiles are status/shortcut tiles, not fabricated financial totals. Live KPIs should be connected through application services after their queries are implemented.
- Balochistan scenery / Pakistan flag imagery is not bundled because the ZIP did not contain approved background assets. The brand palette, company identity, logo lookup and footer are included.
