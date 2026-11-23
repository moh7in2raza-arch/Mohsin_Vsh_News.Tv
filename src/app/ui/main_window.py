"""VSH NEWS TV dashboard and module launcher."""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from src.app.domain.security import permissions as P
from src.app.ui.accounts_view import AccountsView
from src.app.ui.admin_views import (
    CompanyProfileView,
    DatabaseBackupView,
    SystemSettingsView,
    UsersRolesView,
)
from src.app.ui.dashboard_view import DashboardView
from src.app.ui.employees_view import EmployeesView
from src.app.ui.module_shell import VshModuleShellWindow, session_role_label
from src.app.ui.reports_view import ReportsView
from src.app.ui.vouchers_view import VouchersView

_EMPLOYEE_VIEW = getattr(P, "EMPLOYEE_VIEW", "employee.view")
_USER_MANAGE = getattr(P, "USER_MANAGE", "user.manage")
_BACKUP_RUN = getattr(P, "BACKUP_RUN", "backup.run")

_MODULE_REGISTRY = {
    "Accounts": (P.ACCOUNT_VIEW, "master_data", "Chart of Accounts", AccountsView, "Active Chart of Accounts", False),
    "Chart of accounts": (P.ACCOUNT_VIEW, "master_data", "Chart of Accounts", AccountsView, "Active Chart of Accounts", False),
    "Employees": (_EMPLOYEE_VIEW, "master_data", "Employee Directory", EmployeesView, "Staff & HR Master", False),
    "Customers": (P.ACCOUNT_VIEW, "master_data", "Customers Master", AccountsView, "Receivable Sub-Ledger", False),
    "Suppliers": (P.ACCOUNT_VIEW, "master_data", "Suppliers Master", AccountsView, "Payable Sub-Ledger", False),
    "Vouchers": (P.VOUCHER_VIEW, "transactions", "Vouchers & Journal Entries", VouchersView, "All Vouchers", False),
    "Payment": (P.VOUCHER_VIEW, "transactions", "Payment Vouchers", VouchersView, "Payment Vouchers", False),
    "Receipt": (P.VOUCHER_VIEW, "transactions", "Receipt Vouchers", VouchersView, "Receipt Vouchers", False),
    "Journal": (P.VOUCHER_VIEW, "transactions", "Journal Vouchers", VouchersView, "General Journal", False),
    "Sales": (P.VOUCHER_VIEW, "transactions", "Sales Vouchers", VouchersView, "Sales & Advertising", False),
    "Reports": (P.REPORT_VIEW, "reports", "Financial Reports", ReportsView, "Trial Balance & Account Ledger", True),
    "Ledger": (P.REPORT_VIEW, "reports", "General & Account Ledger", ReportsView, "Account Ledger", True),
    "Trial Balance": (P.REPORT_VIEW, "reports", "Trial Balance", ReportsView, "As-Of Date Trial Balance", True),
    "P&L Statement": (P.REPORT_VIEW, "reports", "Profit & Loss Statement", ReportsView, "Income & Expense Summary", True),
    "Balance Sheet": (P.REPORT_VIEW, "reports", "Balance Sheet", ReportsView, "Assets, Liabilities & Equity", True),
    "Statements": (P.REPORT_VIEW, "reconcile", "Account Statements", ReportsView, "Statement Mode", True),
    "Reconcile": (P.REPORT_VIEW, "reconcile", "Bank & Ledger Reconciliation", ReportsView, "Reconciliation Criteria", True),
    "Attendance": (_EMPLOYEE_VIEW, "hr_payroll", "Staff Attendance", EmployeesView, "Daily Attendance Register", False),
    "Payroll": (_EMPLOYEE_VIEW, "hr_payroll", "Monthly Payroll", EmployeesView, "Payroll Processing", False),
    "Salary Reports": (_EMPLOYEE_VIEW, "hr_payroll", "Salary Reports", EmployeesView, "Payroll Summary", False),
    "Users & Roles": (_USER_MANAGE, "admin", "Users & Roles Administration", UsersRolesView, "RBAC Security", False),
    "System Settings": (_USER_MANAGE, "admin", "System Settings", SystemSettingsView, "ERP Configuration", False),
    "Company Profile": (_USER_MANAGE, "admin", "Company Profile", CompanyProfileView, "Company Profile", False),
    "Backup Database": (_BACKUP_RUN, "admin", "Database Backup (PostgreSQL)", DatabaseBackupView, "PostgreSQL Backup", False),
    "Restore Database": (_BACKUP_RUN, "admin", "Database Restore", DatabaseBackupView, "PostgreSQL Restore", False),
    "Ad Schedules": (P.VOUCHER_VIEW, "hr_payroll", "Media Ad Schedules", VouchersView, "Broadcast Advertising Schedule", False),
    "Program Logs": (P.REPORT_VIEW, "hr_payroll", "Broadcast Program Logs", ReportsView, "Transmission & Program Log", False),
    "Client Billing": (P.VOUCHER_VIEW, "transactions", "Media Client Billing", VouchersView, "Agency & Client Billing", False),
}


class VshNewsMainWindow(QMainWindow):
    """Top-level VSH NEWS TV dashboard shown after authentication."""

    logged_out = Signal()

    def __init__(self, services, session):
        super().__init__()
        self._services = services
        self._session = session
        self._open_windows: dict[str, VshModuleShellWindow] = {}

        self.setWindowTitle("VSH NEWS TV — Dashboard")
        self.resize(1440, 900)
        self.setMinimumSize(1100, 700)

        self._dashboard = DashboardView(session)
        self._dashboard.module_requested.connect(self._open_dashboard_module)

        brand = QLabel("VSH NEWS TV")
        brand.setObjectName("brand")
        company = QLabel("Visionary Baluchistan\nMedia Corporation (Pvt) Ltd")
        company.setObjectName("company")
        company.setWordWrap(True)
        whoami = QLabel(
            f"User ID: {session.username}\nRole: {session_role_label(session)}"
        )
        whoami.setObjectName("whoami")
        whoami.setWordWrap(True)

        self._nav = QListWidget()
        self._nav.setObjectName("nav")
        self._nav.addItems(
            [
                "Home",
                "Accounts",
                "Employees",
                "Vouchers",
                "Trial Balance",
                "Ledger",
                "Attendance",
                "Users & Roles",
                "Company Profile",
                "Backup Database",
                "Exit",
            ]
        )
        self._nav.setCurrentRow(0)
        self._nav.itemClicked.connect(
            lambda item: self._open_dashboard_module(item.text())
        )

        logout = QPushButton("Log out")
        logout.setObjectName("logout")
        logout.clicked.connect(self._logout)

        panel = QWidget()
        panel.setObjectName("nav-panel")
        panel.setFixedWidth(245)
        side = QVBoxLayout(panel)
        side.setContentsMargins(0, 0, 0, 12)
        side.setSpacing(7)
        side.addWidget(brand)
        side.addWidget(company)
        side.addWidget(whoami)
        side.addWidget(self._nav, 1)
        side.addWidget(logout)

        central = QWidget()
        central.setObjectName("shell")
        row = QHBoxLayout(central)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addWidget(panel)
        self._stack = QStackedWidget()
        self._stack.addWidget(self._dashboard)
        row.addWidget(self._stack, 1)
        self.setCentralWidget(central)

        status = QStatusBar()
        status.showMessage(
            "Database: Connected (PostgreSQL)  |  System Ready  |  "
            "VSH NEWS TV — Working for a Better Tomorrow"
        )
        self.setStatusBar(status)
        self.setStyleSheet("""
            QWidget#shell { background: #1E293B; }
            QWidget#nav-panel { background: #32101D; border-right: 2px solid #C8A96B; }
            QLabel#brand {
                color: #FFFFFF; font-size: 19px; font-weight: 800;
                padding: 20px 16px 2px;
            }
            QLabel#company { color: #D8C5A2; font-size: 10px; padding: 0 16px 10px; }
            QLabel#whoami {
                color: #FFFFFF; background: #1E293B; border-top: 1px solid #DC2626;
                border-bottom: 1px solid #DC2626; padding: 10px 16px;
                font-size: 11px; font-weight: 600;
            }
            QListWidget#nav { background: #0F172A; border: 0; color: #F8FAFC; outline: 0; padding: 8px; }
            QListWidget#nav::item { padding: 11px 12px; margin: 2px 0; border-radius: 7px; font-weight: 600; }
            QListWidget#nav::item:selected { background: #DC2626; color: #FFFFFF; border-left: 4px solid #FACC15; }
            QListWidget#nav::item:hover { background: #4B1427; }
            QPushButton#logout {
                margin: 10px 14px; padding: 10px; color: #FFFFFF;
                background: #6A2038; border: 1px solid #C8A96B;
                border-radius: 7px; font-weight: 700;
            }
            QPushButton#logout:hover { background: #842B49; }
            QStatusBar {
                background: #0F172A; color: #F8FAFC;
                border-top: 1px solid #DC2626; font-size: 11px;
            }
        """)

    def _open_dashboard_module(self, module_name: str) -> None:
        if module_name == "Home":
            self._dashboard.refresh()
            return
        if module_name == "Exit":
            self.close()
            return

        spec = _MODULE_REGISTRY.get(module_name)
        if spec is None:
            QMessageBox.information(
                self,
                module_name,
                f"{module_name} module is not available.",
            )
            return

        permission, category, title, view_class, criteria_note, maximized = spec
        if permission and not self._session.has(permission):
            QMessageBox.warning(
                self,
                "Access Denied",
                f"Your role does not have permission ({permission}) for {title}.",
            )
            return

        existing = self._open_windows.get(title)
        if existing is not None:
            if not existing.isVisible():
                existing.showMaximized() if maximized else existing.show()
            existing.raise_()
            existing.activateWindow()
            return

        if module_name == "Restore Database":
            view = view_class(self._services, self._session, restore_mode=True)
        else:
            view = view_class(self._services, self._session)

        refresh = getattr(view, "refresh", None)
        if callable(refresh):
            refresh()

        window = VshModuleShellWindow(
            session=self._session,
            title=title,
            category=category,
            content_widget=view,
            criteria_note=criteria_note,
            maximized=maximized,
        )
        self._open_windows[title] = window

    def _logout(self) -> None:
        self._services.auth.logout()
        for window in list(self._open_windows.values()):
            window.close()
            window.deleteLater()
        self._open_windows.clear()
        self.logged_out.emit()
        self.close()


# Keep the prior import name available to existing callers.
MainWindow = VshNewsMainWindow
