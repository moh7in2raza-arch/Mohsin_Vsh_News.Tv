from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from src.app.domain.security import permissions as P
from src.app.ui.accounts_view import AccountsView
from src.app.ui.reports_view import ReportsView
from src.app.ui.vouchers_view import VouchersView

_PAGES = (
    (P.VOUCHER_VIEW, "Vouchers", VouchersView),
    (P.ACCOUNT_VIEW, "Chart of accounts", AccountsView),
    (P.REPORT_VIEW, "Reports", ReportsView),
)


class MainWindow(QMainWindow):
    logged_out = Signal()

    def __init__(self, services, session):
        super().__init__()
        self._services = services
        self.setWindowTitle("ERP Office Management")
        self.resize(1200, 720)

        self._stack = QStackedWidget()
        self._views = []
        self._nav = QListWidget()
        self._nav.setObjectName("nav")
        for permission, label, view_class in _PAGES:
            if session.has(permission):
                view = view_class(services, session)
                self._views.append(view)
                self._stack.addWidget(view)
                self._nav.addItem(label)
        if not self._views:
            self._stack.addWidget(QLabel("No modules are available for your role."))

        brand = QLabel("ERP Office")
        brand.setObjectName("brand")
        whoami = QLabel(f"Signed in as {session.username}")
        whoami.setObjectName("whoami")
        logout = QPushButton("Log out")
        logout.setObjectName("logout")
        logout.clicked.connect(self._logout)

        panel = QWidget()
        panel.setObjectName("nav-panel")
        panel.setFixedWidth(200)
        side = QVBoxLayout(panel)
        side.setContentsMargins(0, 0, 0, 0)
        side.setSpacing(0)
        side.addWidget(brand)
        side.addWidget(whoami)
        side.addWidget(self._nav, 1)
        side.addWidget(logout)

        central = QWidget()
        row = QHBoxLayout(central)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)
        row.addWidget(panel)
        row.addWidget(self._stack, 1)
        self.setCentralWidget(central)

        self._nav.currentRowChanged.connect(self._show_page)
        if self._views:
            self._nav.setCurrentRow(0)

    def _show_page(self, row: int) -> None:
        if 0 <= row < len(self._views):
            self._stack.setCurrentIndex(row)
            self._views[row].refresh()

    def _logout(self) -> None:
        self._services.auth.logout()
        self.logged_out.emit()
        self.close()
