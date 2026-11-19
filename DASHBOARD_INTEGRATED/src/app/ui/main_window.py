"""VSH ERP main window with the branded home dashboard.

Keeps the existing session, service, permission, and screen interfaces.
The dashboard is a UI layer only; it does not access the database directly.
"""
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.app.domain.security import permissions as P
from src.app.ui.accounts_view import AccountsView
from src.app.ui.dashboard_view import DashboardView
from src.app.ui.reports_view import ReportsView
from src.app.ui.vouchers_view import VouchersView


# These are the screens already present in the user's current MainWindow.
_PAGE_DEFINITIONS = (
    (P.VOUCHER_VIEW, "Vouchers", VouchersView),
    (P.ACCOUNT_VIEW, "Chart of accounts", AccountsView),
    (P.REPORT_VIEW, "Reports", ReportsView),
)


class MainWindow(QMainWindow):
    logged_out = Signal()

    def __init__(self, services, session):
        super().__init__()
        self._services = services
        self._session = session

        self.setWindowTitle(
            "VSH NEWS TV | Visionary Baluchistan Media Corporation (Pvt.) Limited"
        )
        self.resize(1440, 900)
        self.setMinimumSize(1100, 700)

        self._stack = QStackedWidget()
        self._navigation_pages = []

        # Home is the first page. Existing screens are added below it.
        self._dashboard = DashboardView(session)
        self._dashboard.module_requested.connect(self._open_dashboard_module)
        self._add_page("Dashboard", self._dashboard)

        for permission, label, view_class in _PAGE_DEFINITIONS:
            if session.has(permission):
                view = view_class(services, session)
                self._add_page(label, view)

        brand = QLabel("VSH NEWS TV")
        brand.setObjectName("brand")

        company = QLabel(
            "Visionary Baluchistan\nMedia Corporation (Pvt.) Limited"
        )
        company.setObjectName("company")
        company.setWordWrap(True)

        whoami = QLabel(f"Signed in as {session.username}")
        whoami.setObjectName("whoami")
        whoami.setWordWrap(True)

        self._nav = QListWidget()
        self._nav.setObjectName("nav")
        for label, _page in self._navigation_pages:
            self._nav.addItem(label)

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
        row.addWidget(self._stack, 1)
        self.setCentralWidget(central)

        self._nav.currentRowChanged.connect(self._show_page)
        self._nav.setCurrentRow(0)

        self.setStyleSheet("""
            QWidget#shell { background: #F7F3EA; }
            QWidget#nav-panel { background: #32101D; }
            QLabel#brand {
                color: #FFFFFF; font-size: 19px; font-weight: 800;
                padding: 22px 16px 2px;
            }
            QLabel#company {
                color: #D8C5A2; font-size: 10px; padding: 0 16px 12px;
            }
            QLabel#whoami {
                color: #F0E8DC; background: #4B1427; padding: 10px 16px;
            }
            QListWidget#nav {
                background: #32101D; border: 0; color: #F5EDE3;
                outline: 0; padding: 8px;
            }
            QListWidget#nav::item {
                padding: 12px; margin: 2px 0; border-radius: 7px;
            }
            QListWidget#nav::item:selected {
                background: #6A2038; color: #FFFFFF;
                border-left: 3px solid #C8A96B;
            }
            QListWidget#nav::item:hover { background: #4B1427; }
            QPushButton#logout {
                margin: 10px 14px; padding: 10px; color: #FFFFFF;
                background: #6A2038; border: 1px solid #9A6F50;
                border-radius: 7px;
            }
            QPushButton#logout:hover { background: #842B49; }
        """)

    def _add_page(self, label: str, widget: QWidget) -> None:
        self._stack.addWidget(widget)
        self._navigation_pages.append((label, widget))

    def _show_page(self, row: int) -> None:
        if not 0 <= row < len(self._navigation_pages):
            return

        widget = self._navigation_pages[row][1]
        self._stack.setCurrentWidget(widget)

        refresh = getattr(widget, "refresh", None)
        if callable(refresh):
            refresh()

    def _open_dashboard_module(self, module_name: str) -> None:
        # These exact modules are already implemented and permission-gated.
        aliases = {
            "Vouchers": "Vouchers",
            "Chart of accounts": "Chart of accounts",
            "Reports": "Reports",
        }
        target_label = aliases.get(module_name)

        if target_label:
            for row, (label, _widget) in enumerate(self._navigation_pages):
                if label == target_label:
                    self._nav.setCurrentRow(row)
                    return

        # Other tiles are visible as roadmap shortcuts, but no unfinished
        # module is presented as if it were already implemented.
        QMessageBox.information(
            self,
            "Module not connected yet",
            (
                f"{module_name} is not connected to a complete screen and "
                "application service in the current project. It has not been "
                "opened or fabricated."
            ),
        )

    def _logout(self) -> None:
        self._services.auth.logout()
        self.logged_out.emit()
        self.close()
