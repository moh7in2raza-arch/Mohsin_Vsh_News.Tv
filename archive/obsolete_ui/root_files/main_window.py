"""Main system window: header, sidebar, home dashboard, opened screens, status bar.

UI layer only (ADR-001). It receives what it needs from outside:
  - user:  who is logged in (from the auth service)
  - can:   cosmetic permission check (from the permission service)
  - db_ok / db_label: connection status (from an application service)
"""
from __future__ import annotations

from typing import Callable

from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QMainWindow, QMessageBox, QStackedWidget, QVBoxLayout, QHBoxLayout, QWidget,
)

from src.app.ui import theme
from src.app.ui.navigation import ITEM_BY_KEY, UserInfo
from src.app.ui.screens import SCREENS
from src.app.ui.widgets import (
    HeaderBar, HomePage, ScreenFrame, Sidebar, StatusBar, placeholder,
)

DEFAULT_COMPANY = "Visionary Baluchistan Media Corporation (Pvt) Ltd"


class MainWindow(QMainWindow):
    def __init__(self, user: UserInfo, can: Callable[[str], bool], *,
                 company: str = DEFAULT_COMPANY, db_ok: bool = True,
                 db_label: str = "PostgreSQL erp_office") -> None:
        super().__init__()
        self.setWindowTitle("VSH NEWS TV - Main System")
        self.resize(1360, 860)
        self.setMinimumSize(1120, 720)
        self.setFont(QFont(theme.FONT, 10))
        self.setStyleSheet(theme.APP_QSS)

        central = QWidget()
        self.setCentralWidget(central)
        outer = QVBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        outer.addWidget(HeaderBar(user, company))

        body = QHBoxLayout()
        body.setSpacing(0)
        self._sidebar = Sidebar(can)
        self._stack = QStackedWidget()
        self._home = HomePage(can)
        self._stack.addWidget(self._home)
        body.addWidget(self._sidebar)
        body.addWidget(self._stack, 1)
        outer.addLayout(body, 1)

        self.status = StatusBar(db_label, db_ok)
        outer.addWidget(self.status)

        self._pages: dict[str, QWidget] = {}
        self._sidebar.homeRequested.connect(self.show_home)
        self._sidebar.itemRequested.connect(self.open_screen)
        self._sidebar.exitRequested.connect(self.confirm_exit)
        self._home.requested.connect(self.open_screen)

    # ---- navigation
    def show_home(self) -> None:
        self._stack.setCurrentWidget(self._home)
        self._sidebar.set_home_active(True)

    def open_screen(self, key: str) -> None:
        if key == "exit":
            self.confirm_exit()
            return
        if key not in self._pages:
            self._pages[key] = self._build_page(key)
            self._stack.addWidget(self._pages[key])
        self._stack.setCurrentWidget(self._pages[key])
        self._sidebar.set_home_active(False)

    def _build_page(self, key: str) -> QWidget:
        title = ITEM_BY_KEY[key].title if key in ITEM_BY_KEY else key
        factory = SCREENS.get(key)
        if factory is None:
            body = placeholder(f"{title}\n\nThis screen has not been built yet.")
        else:
            try:
                body = factory()
            except Exception as exc:          # one broken screen must not kill the app
                body = placeholder(f"Could not open {title}.\n\n{exc}")
        frame = ScreenFrame(title, body)
        frame.backRequested.connect(self.show_home)
        return frame

    def confirm_exit(self) -> None:
        answer = QMessageBox.question(
            self, "Exit", "Close VSH NEWS TV?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if answer == QMessageBox.StandardButton.Yes:
            self.close()
