"""
VSH NEWS TV - ERP Office Management Dashboard
Technology: Python 3.12 (64-bit) + PySide6
Architecture boundary (ADR-001): UI only. No SQL or database access in this file.

Place this file at:
    C:\\Mohsin_Vsh_News.tv\\ui\\dashboard.py

Run standalone for a UI smoke test (from the project root, venv active):
    python -m ui.dashboard

Integrate into the application:
    from ui.dashboard import VSHDashboard
    dashboard = VSHDashboard()
    dashboard.module_requested.connect(controller.open_module)
    dashboard.show()
"""

from __future__ import annotations

import sys
from datetime import datetime
from typing import Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)


class VSHDashboard(QMainWindow):
    """Main ERP dashboard window.

    The dashboard emits module_requested when a user selects a module.
    Application/controller code should handle that signal and open the
    appropriate screen. This class deliberately does not access PostgreSQL.
    """

    module_requested = Signal(str)

    WINDOW_BACKGROUND = "#E8F0F8"
    NAV_BACKGROUND = "#0A2540"
    HEADER_BACKGROUND = "#072B59"
    TEXT_DARK = "#0F172A"

    MODULES = [
        {
            "title": "Master Data",
            "color": "#1D70D1",
            "icon": "▦",
            "items": ["Accounts", "Employees", "Customers", "Suppliers"],
        },
        {
            "title": "Transactions",
            "color": "#169C4B",
            "icon": "⇄",
            "items": ["Payment", "Receipt", "Journal", "Sales"],
        },
        {
            "title": "Financial Reports",
            "color": "#5B3CC4",
            "icon": "▤",
            "items": ["Ledger", "Trial Balance", "P&L Statement", "Balance Sheet"],
        },
        {
            "title": "Statements & Reconcile",
            "color": "#E67E22",
            "icon": "▧",
            "items": ["Statements", "Reconcile"],
        },
        {
            "title": "Attendance & Payroll",
            "color": "#008B9E",
            "icon": "♟",
            "items": ["Attendance", "Payroll", "Salary Reports"],
        },
        {
            "title": "Settings",
            "color": "#34495E",
            "icon": "⚙",
            "items": ["Users & Roles", "System Settings", "Company Profile"],
        },
        {
            "title": "Backup & Restore",
            "color": "#C0392B",
            "icon": "▣",
            "items": ["Backup Database", "Restore Database"],
        },
        {
            "title": "Media & Broadcast",
            "color": "#0D9488",
            "icon": "▣",
            "items": ["Ad Schedules", "Program Logs", "Client Billing"],
        },
    ]

    NAV_ITEMS = [
        "Home",
        "Master Data",
        "Transactions",
        "Reports",
        "Attendance & Payroll",
        "Settings",
        "Backup & Restore",
        "Exit",
    ]

    def __init__(
        self,
        user_name: str = "Mohsin Raza",
        user_id: str = "admin",
        user_role: str = "Administrator",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)

        self.user_name = user_name
        self.user_id = user_id
        self.user_role = user_role

        self.setWindowTitle("VSH NEWS TV - ERP Office Management")
        self.resize(1280, 800)
        self.setMinimumSize(1050, 680)
        self.setStyleSheet(
            f"QMainWindow {{ background-color: {self.WINDOW_BACKGROUND}; }}"
        )

        self._build_ui()
        self._start_clock()

    # ------------------------------------------------------------------
    # Main layout
    # ------------------------------------------------------------------
    def _build_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_header())

        body = QWidget()
        body_layout = QHBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        body_layout.addWidget(self._build_sidebar())

        self.content_area = QScrollArea()
        self.content_area.setWidgetResizable(True)
        self.content_area.setFrameShape(QFrame.Shape.NoFrame)
        self.content_area.setStyleSheet(
            "QScrollArea { background: #E8F0F8; border: none; }"
            "QScrollBar:vertical { width: 11px; background: #DCE6F1; }"
            "QScrollBar::handle:vertical { background: #91A9C2; border-radius: 5px; }"
        )
        self.content_area.setWidget(self._build_dashboard_content())
        body_layout.addWidget(self.content_area, 1)

        root.addWidget(body, 1)
        root.addWidget(self._build_status_bar())

    def _build_header(self) -> QWidget:
        header = QFrame()
        header.setFixedHeight(88)
        header.setStyleSheet(f"background-color: {self.HEADER_BACKGROUND};")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 8, 20, 8)
        layout.setSpacing(15)

        logo = QLabel("VSH\nNEWS")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedSize(66, 66)
        logo.setStyleSheet(
            "QLabel { background: #D32F2F; color: white; border-radius: 6px;"
            "font-family: Arial; font-size: 17px; font-weight: bold; }"
        )
        layout.addWidget(logo)

        title_box = QVBoxLayout()
        title = QLabel("VSH NEWS TV")
        title.setStyleSheet("color: white; font-size: 25px; font-weight: bold;")
        subtitle = QLabel("Visionary Baluchistan Media Corporation (Pvt) Ltd")
        subtitle.setStyleSheet("color: #CBD5E1; font-size: 12px;")
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        layout.addLayout(title_box, 1)

        user_box = QLabel(
            f"{self.user_name}\nUser ID: {self.user_id}\nRole: {self.user_role}"
        )
        user_box.setStyleSheet(
            "color: white; background: #0D3B75; border-radius: 8px;"
            "padding: 9px 14px; font-size: 11px;"
        )
        layout.addWidget(user_box)

        clock_box = QFrame()
        clock_box.setStyleSheet("background: #0D3B75; border-radius: 8px;")
        clock_layout = QVBoxLayout(clock_box)
        clock_layout.setContentsMargins(14, 8, 14, 8)
        self.time_label = QLabel()
        self.time_label.setStyleSheet(
            "color: white; font-size: 13px; font-weight: bold;"
        )
        self.date_label = QLabel()
        self.date_label.setStyleSheet("color: #CBD5E1; font-size: 11px;")
        clock_layout.addWidget(self.time_label)
        clock_layout.addWidget(self.date_label)
        layout.addWidget(clock_box)

        return header

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFixedWidth(230)
        sidebar.setStyleSheet(f"background-color: {self.NAV_BACKGROUND};")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(12, 18, 12, 12)
        layout.setSpacing(7)

        for index, item in enumerate(self.NAV_ITEMS):
            button = QPushButton(item if item == "Exit" else f"  {item}")
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setMinimumHeight(43)
            button.setStyleSheet(
                self._nav_button_style(active=(index == 0), exit_item=(item == "Exit"))
            )
            button.clicked.connect(
                lambda checked=False, name=item: self._on_navigation(name)
            )
            layout.addWidget(button)

        layout.addStretch(1)

        version = QLabel("ERP Office Management\nDesktop Application")
        version.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version.setStyleSheet("color: #91A9C2; font-size: 10px;")
        layout.addWidget(version)
        return sidebar

    @staticmethod
    def _nav_button_style(active: bool = False, exit_item: bool = False) -> str:
        background = "#1D70D1" if active else "transparent"
        foreground = "#FF8A8A" if exit_item else "white"
        return (
            "QPushButton {"
            f"background-color: {background}; color: {foreground};"
            "border: none; border-radius: 6px; text-align: left;"
            "padding: 8px 12px; font-size: 13px;"
            "}"
            "QPushButton:hover { background-color: #164E87; }"
        )

    def _build_status_bar(self) -> QWidget:
        bar = QFrame()
        bar.setFixedHeight(30)
        bar.setStyleSheet(f"background-color: {self.HEADER_BACKGROUND};")

        layout = QHBoxLayout(bar)
        layout.setContentsMargins(16, 0, 16, 0)

        self.status_label = QLabel("Home dashboard")
        self.status_label.setStyleSheet("color: #CBD5E1; font-size: 11px;")
        layout.addWidget(self.status_label, 1)

        env_label = QLabel("ERP Office Management")
        env_label.setStyleSheet("color: #91A9C2; font-size: 11px;")
        layout.addWidget(env_label)
        return bar

    # ------------------------------------------------------------------
    # Dashboard content
    # ------------------------------------------------------------------
    def _build_dashboard_content(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet("background-color: #E8F0F8;")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(16)

        layout.addWidget(self._build_welcome_banner())

        cards_grid = QGridLayout()
        cards_grid.setContentsMargins(0, 0, 0, 0)
        cards_grid.setHorizontalSpacing(12)
        cards_grid.setVerticalSpacing(12)

        for index, module in enumerate(self.MODULES):
            row, column = divmod(index, 4)
            cards_grid.addWidget(self._build_module_card(module), row, column)

        for column in range(4):
            cards_grid.setColumnStretch(column, 1)

        layout.addLayout(cards_grid)
        layout.addStretch(1)
        return page

    def _build_welcome_banner(self) -> QWidget:
        banner = QFrame()
        banner.setObjectName("welcomeBanner")
        banner.setMinimumHeight(155)
        banner.setStyleSheet(
            "QFrame#welcomeBanner { background: #DCEBFA; border: 1px solid #BFD8F2;"
            "border-radius: 12px; }"
        )

        layout = QHBoxLayout(banner)
        layout.setContentsMargins(24, 18, 24, 18)
        layout.setSpacing(22)

        logo = QLabel("VSH\nNEWS")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedSize(112, 112)
        logo.setStyleSheet(
            "QLabel { background: #D32F2F; color: white; border-radius: 8px;"
            "font-family: Arial; font-size: 27px; font-weight: bold; }"
        )
        layout.addWidget(logo)

        text_box = QVBoxLayout()
        text_box.setSpacing(6)

        welcome = QLabel("Welcome to VSH NEWS TV ERP Office Management System")
        welcome.setWordWrap(True)
        welcome.setStyleSheet(
            f"font-size: 20px; font-weight: bold; color: {self.TEXT_DARK};"
            "background: transparent; border: none;"
        )
        text_box.addWidget(welcome)

        sub = QLabel(
            f"Signed in as {self.user_name} ({self.user_role}). "
            "Select a module below to continue."
        )
        sub.setWordWrap(True)
        sub.setStyleSheet(
            "font-size: 12px; color: #475569; background: transparent; border: none;"
        )
        text_box.addWidget(sub)

        layout.addLayout(text_box, 1)
        return banner

    def _build_module_card(self, data: dict) -> QWidget:
        """Build one module card. `data` is one entry of MODULES."""
        card = QFrame()
        card.setObjectName("moduleCard")
        card.setStyleSheet(
            "QFrame#moduleCard { background: white; border: 1px solid #D5E0EC;"
            "border-radius: 10px; }"
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(14, 14, 14, 12)
        card_layout.setSpacing(6)

        heading = QHBoxLayout()
        heading.setSpacing(10)

        icon = QLabel(data["icon"])
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFixedSize(40, 40)
        icon.setStyleSheet(
            f"background: {data['color']}; color: white; border-radius: 20px;"
            "font-size: 19px; font-weight: bold;"
        )
        heading.addWidget(icon)

        title = QLabel(data["title"])
        title.setWordWrap(True)
        title.setStyleSheet(
            f"color: {self.TEXT_DARK}; font-size: 13px; font-weight: bold;"
            "background: transparent; border: none;"
        )
        heading.addWidget(title, 1)
        card_layout.addLayout(heading)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color: #E2E8F0; background: transparent;")
        card_layout.addWidget(line)

        for item_name in data["items"]:
            item_button = QPushButton(f"›  {item_name}")
            item_button.setCursor(Qt.CursorShape.PointingHandCursor)
            item_button.setMinimumHeight(27)
            item_button.setSizePolicy(
                QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
            )
            item_button.setStyleSheet(
                "QPushButton { background: transparent; color: #1E293B;"
                "border: none; text-align: left; padding: 3px 5px; font-size: 11px; }"
                "QPushButton:hover { background: #F1F5F9; color: #1D70D1; }"
            )
            item_button.clicked.connect(
                lambda checked=False, name=item_name: self._request_module(name)
            )
            card_layout.addWidget(item_button)

        card_layout.addStretch(1)
        return card

    # ------------------------------------------------------------------
    # Events and helpers
    # ------------------------------------------------------------------
    def _start_clock(self) -> None:
        self._update_clock()
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)

    def _update_clock(self) -> None:
        now = datetime.now()
        self.time_label.setText(now.strftime("%I:%M:%S %p"))
        self.date_label.setText(now.strftime("%d-%b-%Y"))

    def _request_module(self, module_name: str) -> None:
        self.status_label.setText(f"Selected: {module_name}")

        if module_name == "Employees":
            from src.app.ui.employees_view import EmployeesView

        self.employee_window = EmployeesView()
        self.employee_window.show()
        self.module_requested.emit(module_name)


    def _on_navigation(self, item: str) -> None:
        if item == "Exit":
            self.close()
        elif item == "Home":
            self.status_label.setText("Home dashboard")
        else:
            self._request_module(item)

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt event naming
        answer = QMessageBox.question(
            self,
            "Exit VSH NEWS TV",
            "Are you sure you want to close the application?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("VSH NEWS TV - ERP Office Management")
    app.setFont(QFont("Segoe UI", 10))

    window = VSHDashboard()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
