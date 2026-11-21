from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QListWidget, QMainWindow, QPushButton,
    QStackedWidget, QVBoxLayout, QWidget,
)

from src.app.domain.security import permissions as P
from src.app.ui.accounts_view import AccountsView
from src.app.ui.dashboard_view import DashboardView
from src.app.ui.reports_view import ReportsView
from src.app.ui.vouchers_view import VouchersView

# Only screens that currently exist and have permission codes are wired here.
_PAGE_DEFINITIONS = (
    (P.VOUCHER_VIEW, "Vouchers", VouchersView),
    (P.ACCOUNT_VIEW, "Chart of Accounts", AccountsView),
    (P.REPORT_VIEW, "Reports", ReportsView),
)


class MainWindow(QMainWindow):
    logged_out = Signal()

    def __init__(self, services, session):
        super().__init__()
        self._services = services
        self._session = session
        self.setWindowTitle("VSH NEWS TV | Office Management System")
        self.resize(1440, 900)
        self.setMinimumSize(1100, 700)

        self._stack = QStackedWidget()
        self._views = []
        self._nav_rows = {}

        self._dashboard = DashboardView(session)
        self._dashboard.module_requested.connect(self._open_requested_module)
        self._stack.addWidget(self._dashboard)

        self._nav = QListWidget()
        self._nav.setObjectName("nav")
        self._add_navigation("Home", self._dashboard)

        for permission, label, view_class in _PAGE_DEFINITIONS:
            if session.has(permission):
                view = view_class(services, session)
                self._views.append(view)
                self._stack.addWidget(view)
                self._add_navigation(label, view)

        brand = QLabel("VSH NEWS TV")
        brand.setObjectName("brand")
        company = QLabel("Visionary Baluchistan\nMedia Corporation (Pvt.) Ltd.")
        company.setObjectName("company")
        whoami = QLabel(f"Signed in: {session.username}")
        whoami.setObjectName("whoami")

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
            QWidget#shell { background:#F7F3EA; }
            QWidget#nav-panel { background:#32101D; }
            QLabel#brand { color:#FFFFFF; font-size:19px; font-weight:800; padding:22px 16px 2px; }
            QLabel#company { color:#D8C5A2; font-size:10px; padding:0 16px 12px; }
            QLabel#whoami { color:#F0E8DC; background:#4B1427; padding:10px 16px; }
            QListWidget#nav { background:#32101D; border:0; color:#F5EDE3; outline:0; padding:8px; }
            QListWidget#nav::item { padding:12px 12px; margin:2px 0; border-radius:7px; }
            QListWidget#nav::item:selected { background:#6A2038; color:#FFFFFF; border-left:3px solid #C8A96B; }
            QListWidget#nav::item:hover { background:#4B1427; }
            QPushButton#logout { margin:10px 14px; padding:10px; color:#FFFFFF; background:#6A2038;
                border:1px solid #9A6F50; border-radius:7px; }
            QPushButton#logout:hover { background:#842B49; }
        """)

    def _add_navigation(self, label, view):
        self._nav_rows[label] = self._nav.count()
        self._nav.addItem(label)
        self._nav.setItemWidget(self._nav.item(self._nav.count() - 1), None)
        # Keep page index aligned with navigation row.
        self._nav.item(self._nav.count() - 1).setData(32, self._stack.indexOf(view))

    def _show_page(self, row):
        if row < 0:
            return
        item = self._nav.item(row)
        if item is None:
            return
        page_index = item.data(32)
        if page_index is None:
            return
        self._stack.setCurrentIndex(int(page_index))
        widget = self._stack.currentWidget()
        refresh = getattr(widget, "refresh", None)
        if callable(refresh):
            refresh()

    def _open_requested_module(self, name):
        target = {
            "Vouchers": "Vouchers",
            "Chart of accounts": "Chart of Accounts",
            "Reports": "Reports",
        }.get(name)
        if target in self._nav_rows:
            self._nav.setCurrentRow(self._nav_rows[target])
        else:
            # Do not open fake or disconnected screens. The module will be
            # added to navigation once its form and service are implemented.
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self, "Module not connected",
                f"{name} is planned, but its complete screen/service is not yet connected."
            )

    def _logout(self):
        self._services.auth.logout()
        self.logged_out.emit()
        self.close()
