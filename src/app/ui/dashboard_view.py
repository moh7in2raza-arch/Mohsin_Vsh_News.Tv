from datetime import datetime

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QVBoxLayout, QWidget,
)


class DashboardView(QWidget):
    module_requested = Signal(str)

    BACKGROUND = "#E8F0F8"
    NAVY = "#072B59"
    DARK = "#0F172A"

    MODULES = (
        ("Vouchers", "Financial transactions", "#169C4B", "⇄"),
        ("Chart of accounts", "Manage account structure", "#1D70D1", "▦"),
        ("Employees", "Employee records and departments", "#008B9E", "♟"),
        ("Reports", "Financial reports and statements", "#5B3CC4", "▤"),
    )

    def __init__(self, session, available_modules, parent=None):
        super().__init__(parent)

        self.session = session
        self.available_modules = set(available_modules)

        self.setStyleSheet(f"background-color: {self.BACKGROUND};")

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 20, 22, 20)
        root.setSpacing(18)

        root.addWidget(self._build_header())
        root.addWidget(self._build_welcome())

        heading = QLabel("APPLICATION MODULES")
        heading.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #0F172A;"
        )
        root.addWidget(heading)

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)

        column = 0
        row = 0

        for name, description, color, symbol in self.MODULES:
            if name not in self.available_modules:
                continue

            grid.addWidget(
                self._build_card(name, description, color, symbol),
                row, column
            )

            column += 1
            if column == 2:
                column = 0
                row += 1

        root.addLayout(grid)
        root.addStretch(1)

        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet(
            "color: #64748B; padding: 8px; border-top: 1px solid #CBD5E1;"
        )
        root.addWidget(self.status_label)

        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start(1000)
        self._update_clock()

    def _build_header(self):
        header = QFrame()
        header.setFixedHeight(90)
        header.setStyleSheet(
            f"background-color: {self.NAVY}; border-radius: 10px;"
        )

        layout = QHBoxLayout(header)
        layout.setContentsMargins(18, 10, 18, 10)

        logo = QLabel("VSH\nNEWS")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedSize(65, 65)
        logo.setStyleSheet(
            "background: #D32F2F; color: white; border-radius: 7px;"
            "font-size: 16px; font-weight: bold;"
        )
        layout.addWidget(logo)

        company = QVBoxLayout()

        title = QLabel("VSH NEWS TV")
        title.setStyleSheet(
            "color: white; font-size: 23px; font-weight: bold;"
        )

        subtitle = QLabel(
            "Visionary Baluchistan Media Corporation (Pvt) Ltd"
        )
        subtitle.setStyleSheet("color: #CBD5E1; font-size: 11px;")

        company.addWidget(title)
        company.addWidget(subtitle)
        layout.addLayout(company, 1)

        self.clock_label = QLabel()
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.clock_label.setStyleSheet(
            "color: white; font-size: 13px; font-weight: bold;"
        )
        layout.addWidget(self.clock_label)

        return header

    def _build_welcome(self):
        banner = QFrame()
        banner.setStyleSheet(
            "background: #DCEBFA; border: 1px solid #BFD8F2;"
            "border-radius: 10px;"
        )

        layout = QVBoxLayout(banner)
        layout.setContentsMargins(22, 20, 22, 20)

        welcome = QLabel(
            "Welcome to VSH NEWS TV ERP Office Management System"
        )
        welcome.setWordWrap(True)
        welcome.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #0F172A;"
            "border: none; background: transparent;"
        )

        identity = QLabel(
            f"Signed in as: {self.session.username}   "
            f"|   User ID: {self.session.user_id}"
        )
        identity.setStyleSheet(
            "font-size: 12px; color: #475569;"
            "border: none; background: transparent;"
        )

        layout.addWidget(welcome)
        layout.addWidget(identity)

        return banner

    def _build_card(self, name, description, color, symbol):
        card = QFrame()
        card.setObjectName("dashboardCard")
        card.setMinimumHeight(145)
        card.setStyleSheet(
            "QFrame#dashboardCard {"
            "background: white; border: 1px solid #D5E0EC;"
            "border-radius: 10px;"
            "}"
        )

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 14, 16, 14)
        layout.setSpacing(8)

        heading = QHBoxLayout()

        icon = QLabel(symbol)
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFixedSize(40, 40)
        icon.setStyleSheet(
            f"background: {color}; color: white;"
            "border-radius: 20px; font-size: 19px; font-weight: bold;"
        )

        title = QLabel(name)
        title.setStyleSheet(
            "font-size: 14px; font-weight: bold; color: #0F172A;"
            "border: none;"
        )

        heading.addWidget(icon)
        heading.addWidget(title, 1)
        layout.addLayout(heading)

        detail = QLabel(description)
        detail.setWordWrap(True)
        detail.setStyleSheet(
            "color: #64748B; font-size: 11px; border: none;"
        )
        layout.addWidget(detail)

        button = QPushButton(f"Open {name}  →")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setStyleSheet(
            f"QPushButton {{ background: {color}; color: white;"
            "border: none; border-radius: 5px; padding: 8px; }"
            "QPushButton:hover { background: #164E87; }"
        )
        button.clicked.connect(
            lambda checked=False, module=name:
                self._open_module(module)
        )
        layout.addWidget(button)

        return card

    def _open_module(self, name):
        self.status_label.setText(f"Opening {name}...")
        self.module_requested.emit(name)

    def _update_clock(self):
        now = datetime.now()
        self.clock_label.setText(
            now.strftime("%I:%M:%S %p") + "\n" +
            now.strftime("%d-%b-%Y")
        )

    def refresh(self):
        self.status_label.setText("Dashboard ready")
