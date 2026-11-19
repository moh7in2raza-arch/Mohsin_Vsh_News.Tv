"""Role-aware VSH NEWS TV ERP dashboard.

UI-only component: no SQL, database calls, or business rules belong here.
Compatible with the project's PySide6 / src.app architecture.
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget,
)

WINE = "#4B1427"
WINE_DARK = "#32101D"
GOLD = "#C8A96B"
IVORY = "#F7F3EA"
CHARCOAL = "#28252A"
MUTED = "#777078"
GREEN = "#247A55"
TEAL = "#347F83"
VIOLET = "#76618C"


class DashboardView(QWidget):
    """Home dashboard. Emits navigation requests; MainWindow owns routing."""
    module_requested = Signal(str)

    def __init__(self, session, parent=None):
        super().__init__(parent)
        self.session = session
        self.setObjectName("dashboardPage")
        self.setStyleSheet(f"""
            QWidget#dashboardPage {{ background: {IVORY}; color: {CHARCOAL}; }}
            QLabel {{ background: transparent; }}
            QFrame#hero {{ background: {WINE_DARK}; border: 1px solid {GOLD}; border-radius: 15px; }}
            QFrame#metric {{ background: #FFFEFB; border: 1px solid #E6DDCE; border-radius: 12px; }}
            QFrame#module {{ background: #FFFEFB; border: 1px solid #E6DDCE; border-radius: 12px; }}
            QPushButton#quick {{
                background: {WINE}; color: #FFFFFF; border: 0; border-radius: 8px;
                padding: 10px 14px; text-align: left; font-weight: 600;
            }}
            QPushButton#quick:hover {{ background: #6A2038; }}
            QLabel#eyebrow {{ color: {GOLD}; font-size: 10px; font-weight: 700; letter-spacing: 1px; }}
            QLabel#heroTitle {{ color: #FFFFFF; font-size: 22px; font-weight: 700; }}
            QLabel#heroSub {{ color: #E8DCCB; font-size: 11px; }}
            QLabel#section {{ color: {WINE}; font-size: 15px; font-weight: 700; }}
            QLabel#metricValue {{ color: {WINE}; font-size: 21px; font-weight: 700; }}
            QLabel#muted {{ color: {MUTED}; font-size: 10px; }}
        """)

        root = QVBoxLayout(self)
        root.setContentsMargins(22, 20, 22, 18)
        root.setSpacing(16)
        root.addWidget(self._hero())
        root.addWidget(self._section_label("At a glance"))

        metrics = QGridLayout()
        metrics.setSpacing(12)
        cards = [
            ("FINANCE", "Open financial summary", "Available through Reports", GOLD),
            ("VOUCHERS", "Manage transactions", "Permission-controlled access", GREEN),
            ("PEOPLE", "Employee workspace", "HR module connection pending", TEAL),
            ("CONTROL", "System administration", "Role-based access", VIOLET),
        ]
        for i, (eyebrow, title, detail, accent) in enumerate(cards):
            metrics.addWidget(self._metric(eyebrow, title, detail, accent), 0, i)
            metrics.setColumnStretch(i, 1)
        root.addLayout(metrics)

        root.addWidget(self._section_label("Quick access"))
        quick = QGridLayout()
        quick.setSpacing(10)
        self._add_quick(quick, 0, 0, "Chart of Accounts", "Chart of accounts")
        self._add_quick(quick, 0, 1, "Vouchers & Transactions", "Vouchers")
        self._add_quick(quick, 0, 2, "Financial Reports", "Reports")
        self._add_quick(quick, 1, 0, "Employee Management", "Employees")
        self._add_quick(quick, 1, 1, "Attendance & Payroll", "Attendance & Payroll")
        self._add_quick(quick, 1, 2, "Users & Permissions", "Users & Roles")
        root.addLayout(quick)
        root.addStretch(1)

        footer = QLabel("Vsh News Tv Office Management System")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet(f"color: {MUTED}; font-size: 10px; padding-top: 5px;")
        root.addWidget(footer)

        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)
        self._update_clock()

    def _hero(self):
        hero = QFrame()
        hero.setObjectName("hero")
        row = QHBoxLayout(hero)
        row.setContentsMargins(22, 18, 22, 18)
        row.setSpacing(18)

        logo = QLabel()
        logo.setFixedSize(74, 74)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(f"background: #FFFFFF; border: 2px solid {GOLD}; border-radius: 10px;")
        logo_path = Path(__file__).resolve().parents[3] / "assets" / "vsh_logo.png.png"
        if not logo_path.exists():
            logo_path = Path(__file__).resolve().parents[3] / "vsh_logo.png.png"
        if logo_path.exists():
            pix = QPixmap(str(logo_path))
            if not pix.isNull():
                logo.setPixmap(pix.scaled(68, 68, Qt.AspectRatioMode.KeepAspectRatio,
                                          Qt.TransformationMode.SmoothTransformation))
        else:
            logo.setText("VSH\nNEWS TV")
            logo.setStyleSheet(logo.styleSheet() + f"color: {WINE}; font-weight: 800;")
        row.addWidget(logo)

        text_col = QVBoxLayout()
        eyebrow = QLabel("VISIONARY BALUCHISTAN MEDIA CORPORATION")
        eyebrow.setObjectName("eyebrow")
        title = QLabel("Office Management Dashboard")
        title.setObjectName("heroTitle")
        title.setWordWrap(True)
        sub = QLabel("Visionary Baluchistan Media Corporation (Pvt.) Limited")
        sub.setObjectName("heroSub")
        sub.setWordWrap(True)
        text_col.addWidget(eyebrow)
        text_col.addWidget(title)
        text_col.addWidget(sub)
        row.addLayout(text_col, 1)

        right = QVBoxLayout()
        self.clock = QLabel()
        self.clock.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.clock.setStyleSheet("color:#FFFFFF;font-size:15px;font-weight:700;")
        self.date = QLabel()
        self.date.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.date.setStyleSheet("color:#E8DCCB;font-size:10px;")
        self.workspace = QLabel(self._workspace_name())
        self.workspace.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.workspace.setStyleSheet(f"color:{GOLD};font-size:10px;font-weight:700;")
        right.addWidget(self.clock)
        right.addWidget(self.date)
        right.addSpacing(6)
        right.addWidget(self.workspace)
        row.addLayout(right)
        return hero

    def _workspace_name(self):
        permissions = getattr(self.session, "permissions", frozenset())
        if "account.manage" in permissions:
            return "ADMIN / FINANCE WORKSPACE"
        if any(str(p).startswith("hr.") for p in permissions):
            return "HR WORKSPACE"
        if any(str(p).startswith("payroll.") for p in permissions):
            return "PAYROLL WORKSPACE"
        if any(str(p).startswith("operations.") for p in permissions):
            return "OPERATIONS WORKSPACE"
        return "OFFICE WORKSPACE"

    def _section_label(self, text):
        label = QLabel(text)
        label.setObjectName("section")
        return label

    def _metric(self, eyebrow, title, detail, accent):
        card = QFrame()
        card.setObjectName("metric")
        card.setMinimumHeight(108)
        box = QVBoxLayout(card)
        box.setContentsMargins(14, 12, 14, 12)
        tag = QLabel(eyebrow)
        tag.setStyleSheet(f"color:{accent};font-size:9px;font-weight:800;letter-spacing:1px;")
        value = QLabel(title)
        value.setObjectName("metricValue")
        value.setWordWrap(True)
        note = QLabel(detail)
        note.setObjectName("muted")
        note.setWordWrap(True)
        box.addWidget(tag)
        box.addWidget(value)
        box.addWidget(note)
        return card

    def _add_quick(self, grid, row, col, label, module):
        button = QPushButton("›   " + label)
        button.setObjectName("quick")
        button.setCursor(Qt.CursorShape.PointingHandCursor)
        button.setMinimumHeight(42)
        button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        button.clicked.connect(lambda checked=False, name=module: self.module_requested.emit(name))
        grid.addWidget(button, row, col)

    def _update_clock(self):
        now = datetime.now()
        self.clock.setText(now.strftime("%I:%M:%S %p"))
        self.date.setText(now.strftime("%A, %d %B %Y"))

    def refresh(self):
        self._update_clock()
