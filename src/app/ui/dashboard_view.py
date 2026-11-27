"""Role-aware VSH NEWS TV ERP Office Management System Dashboard (Dark Glow + User Photo)."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QPainter, QPainterPath, QPixmap
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QSizePolicy, QVBoxLayout, QWidget,
)

from src.app.ui.module_shell import resolve_vsh_logo, session_role_label

BG_DARK = "#121826"
SIDEBAR_BG = "#0F1420"
CARD_BG = "#1A2234"
BANNER_START = "#192030"
BANNER_END = "#451218"
VSH_RED = "#E11D48"
GOLD = "#FACC15"
TEXT_WHITE = "#F8FAFC"
TEXT_MUTED = "#94A3B8"


def _rounded_pixmap(image_path: str | Path, width: int, height: int, radius: int = 10) -> QPixmap | None:
    """Load an image and clip it into a smooth rounded rectangle."""
    pix = QPixmap(str(image_path))
    if pix.isNull():
        return None
    scaled = pix.scaled(
        width, height,
        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
        Qt.TransformationMode.SmoothTransformation,
    )
    # Center-crop to exact dimensions
    x = max(0, (scaled.width() - width) // 2)
    y = max(0, (scaled.height() - height) // 2)
    cropped = scaled.copy(x, y, width, height)

    target = QPixmap(width, height)
    target.fill(Qt.GlobalColor.transparent)
    painter = QPainter(target)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    path = QPainterPath()
    path.addRoundedRect(0, 0, width, height, radius, radius)
    painter.setClipPath(path)
    painter.drawPixmap(0, 0, cropped)
    painter.end()
    return target


class DashboardView(QWidget):
    module_requested = Signal(str)

    MODULES = [
        {"title": "Master Data", "color": "#3B82F6", "icon": "▤", "items": ["Accounts", "Employees", "Customers", "Suppliers"]},
        {"title": "Transactions", "color": "#22C55E", "icon": "⇄", "items": ["Payment", "Receipt", "Journal", "Sales"]},
        {"title": "Financial Reports", "color": "#A855F7", "icon": "📊", "items": ["Ledger", "Trial Balance", "P&L Statement", "Balance Sheet"]},
        {"title": "Statements & Reconcile", "color": "#F97316", "icon": "📄", "items": ["Statements", "Reconcile"]},
        {"title": "Attendance & Payroll", "color": "#06B6D4", "icon": "🪪", "items": ["Attendance", "Payroll", "Salary Reports"]},
        {"title": "Settings", "color": "#64748B", "icon": "⚙", "items": ["Users & Roles", "System Settings", "Company Profile"]},
        {"title": "Backup & Restore", "color": "#EF4444", "icon": "↻", "items": ["Backup Database", "Restore Database"]},
        {"title": "Media & Broadcast", "color": "#14B8A6", "icon": "📺", "items": ["Ad Schedules", "Program Logs", "Client Billing"]},
    ]

    def __init__(self, session, parent=None) -> None:
        super().__init__(parent)
        self.session = session
        self.user_name = getattr(session, "full_name", None) or getattr(session, "username", "Mohsin Raza")
        self.user_role = session_role_label(session)
        self.user_photo = getattr(session, "photo_path", None)

        self.setObjectName("dashboardPage")
        self.setStyleSheet(f"QWidget#dashboardPage {{ background-color: {BG_DARK}; }}")

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Left sidebar with VSH NEWS logo, User Photo, and Nav links
        root.addWidget(self._build_sidebar())

        # Right main workspace area
        right_panel = QWidget()
        right_panel.setStyleSheet(f"background-color: {BG_DARK};")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(
            f"QScrollArea {{ background: {BG_DARK}; border: none; }}"
            "QScrollBar:vertical { width: 8px; background: #0F1420; }"
            f"QScrollBar::handle:vertical {{ background: {VSH_RED}; border-radius: 4px; }}"
        )
        scroll.setWidget(self._build_main_content())
        right_layout.addWidget(scroll, 1)

        root.addWidget(right_panel, 1)

        self._clock_timer = QTimer(self)
        self._clock_timer.timeout.connect(self._update_clock)
        self._clock_timer.start(1000)
        self._update_clock()

    def _build_sidebar(self) -> QWidget:
        sidebar = QFrame()
        sidebar.setFixedWidth(215)
        sidebar.setStyleSheet(
            f"QFrame {{ background-color: {SIDEBAR_BG}; border-right: 1px solid #1E293B; }}"
        )
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(16, 18, 16, 18)
        layout.setSpacing(14)

        # Top VSH NEWS Badge
        logo = QLabel("VSH\nNEWS")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setFixedSize(96, 62)
        logo.setStyleSheet(
            "QLabel { background: #B91C1C; color: #FFFFFF; border: 2px solid #FACC15;"
            "border-radius: 8px; font-size: 18px; font-weight: bold; }"
        )
        logo_path = resolve_vsh_logo()
        if logo_path:
            pix = QPixmap(str(logo_path))
            if not pix.isNull():
                logo.setPixmap(
                    pix.scaled(90, 56, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                )
        layout.addWidget(logo, 0, Qt.AlignmentFlag.AlignHCenter)

        # User Profile Photo Card
        photo_lbl = QLabel()
        photo_lbl.setFixedSize(78, 78)
        photo_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        photo_lbl.setStyleSheet(
            "QLabel { background: #1E293B; color: #F8FAFC; border: 2px solid #334155;"
            "border-radius: 10px; font-size: 24px; font-weight: bold; }"
        )
        if self.user_photo and Path(self.user_photo).exists():
            avatar = _rounded_pixmap(self.user_photo, 74, 74, radius=8)
            if avatar:
                photo_lbl.setPixmap(avatar)
        else:
            initials = "".join(part[0].upper() for part in self.user_name.split()[:2]) or "U"
            photo_lbl.setText(initials)

        layout.addWidget(photo_lbl, 0, Qt.AlignmentFlag.AlignHCenter)

        name_lbl = QLabel(self.user_name)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 14px; font-weight: bold; border: none;")
        layout.addWidget(name_lbl)

        role_lbl = QLabel(self.user_role)
        role_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        role_lbl.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; border: none; margin-top: -10px;")
        layout.addWidget(role_lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #1E293B;")
        layout.addWidget(sep)

        # Sidebar Navigation Buttons
        nav_items = [
            ("⌂  Home", True),
            ("▦  Master Data", False),
            ("⇄  Transactions", False),
            ("📊  Reports", False),
            ("🪪  Attendance & Payroll", False),
            ("⚙  Settings", False),
            ("↻  Backup & Restore", False),
            ("⏻  Exit", False),
        ]
        for label, active in nav_items:
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(36)
            if active:
                btn.setStyleSheet(
                    "QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #DC2626, stop:1 #991B1B);"
                    "color: white; border: none; border-radius: 6px; text-align: left; padding-left: 12px;"
                    "font-size: 12px; font-weight: bold; }"
                )
            else:
                btn.setStyleSheet(
                    f"QPushButton {{ background: transparent; color: {TEXT_MUTED}; border: none;"
                    "border-radius: 6px; text-align: left; padding-left: 12px; font-size: 12px; }}"
                    f"QPushButton:hover {{ background: #1E293B; color: {TEXT_WHITE}; }}"
                )
            clean_name = label.split("  ", 1)[-1]
            btn.clicked.connect(lambda checked=False, n=clean_name: self.module_requested.emit(n))
            layout.addWidget(btn)

        layout.addStretch(1)
        return sidebar

    def _build_main_content(self) -> QWidget:
        page = QWidget()
        page.setStyleSheet(f"background-color: {BG_DARK};")
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(18)

        layout.addWidget(self._build_welcome_banner())

        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)
        for index, module in enumerate(self.MODULES):
            row, col = divmod(index, 4)
            grid.addWidget(self._build_module_card(module), row, col)
        for col in range(4):
            grid.setColumnStretch(col, 1)

        layout.addLayout(grid)
        layout.addStretch(1)
        return page

    def _build_welcome_banner(self) -> QWidget:
        banner = QFrame()
        banner.setObjectName("welcomeBanner")
        banner.setMinimumHeight(115)
        banner.setStyleSheet(
            f"QFrame#welcomeBanner {{ background: qlineargradient(x1:0, y1:0, x2:1, y2:0,"
            f"stop:0 {BANNER_START}, stop:0.65 #2B1622, stop:1 {BANNER_END});"
            f"border: 1px solid {VSH_RED}; border-radius: 12px; }}"
        )
        layout = QHBoxLayout(banner)
        layout.setContentsMargins(24, 16, 20, 16)

        center_box = QVBoxLayout()
        center_box.setSpacing(4)

        title = QLabel("Welcome to VSH NEWS TV ERP Office Management System")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)
        title.setStyleSheet(f"font-size: 20px; font-weight: bold; color: {TEXT_WHITE}; background: transparent;")
        center_box.addWidget(title)
        sub1 = QLabel("Visionary Baluchistan Media Corporation (Pvt) Ltd")
        sub1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub1.setStyleSheet(f"font-size: 13px; font-weight: 600; color: #E2E8F0; background: transparent;")
        center_box.addWidget(sub1)
        sub2 = QLabel("Efficient • Transparent • Reliable")
        sub2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub2.setStyleSheet(f"font-size: 11px; color: {TEXT_MUTED}; background: transparent;")
        center_box.addWidget(sub2)
        layout.addLayout(center_box, 1)
        clock_box = QFrame()
        clock_box.setStyleSheet("QFrame { background: rgba(15, 20, 32, 0.72); border: 1px solid #334155; border-radius: 8px; }"
)

        clock_layout = QVBoxLayout(clock_box)
        clock_layout.setContentsMargins(16, 10, 16, 10)
        clock_layout.setSpacing(2)
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet(f"color: {TEXT_WHITE}; font-size: 17px; font-weight: bold; border: none;")
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet(f"color: {TEXT_MUTED}; font-size: 11px; font-weight: 600; border: none;")
        clock_layout.addWidget(self.time_label)
        clock_layout.addWidget(self.date_label)
        layout.addWidget(clock_box)

        return banner

    def _build_module_card(self, data: dict) -> QWidget:
        card = QFrame()
        card.setObjectName("moduleCard")
        card.setMinimumHeight(215)

        card.setStyleSheet(
            f"""
            QFrame#moduleCard {{
                background: {CARD_BG};
                border: 1px solid {data['color']};
                border-radius: 12px;
            }}
            """
        )

        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 14)
        card_layout.setSpacing(8)

        header = QHBoxLayout()
        header.setSpacing(10)

        icon = QLabel(data["icon"])
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon.setFixedSize(36, 36)

        icon.setStyleSheet(
            f"""
            background:{data['color']};
            color:white;
            border-radius:18px;
            font-size:16px;
            font-weight:bold;
            """
        )

        title = QLabel(data["title"])
        title.setWordWrap(True)
        title.setStyleSheet(
            f"color:{TEXT_WHITE}; font-size:14px; font-weight:bold;"
        )

        header.addWidget(icon)
        header.addWidget(title, 1)

        card_layout.addLayout(header)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("color:#28334A;")
        card_layout.addWidget(line)

        for item_name in data["items"]:
            btn = QPushButton(item_name)

            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setMinimumHeight(28)

            btn.clicked.connect(
                lambda checked=False, n=item_name:
                self.module_requested.emit(n)
            )

            card_layout.addWidget(btn)

        card_layout.addStretch()

        return card

    def _update_clock(self) -> None:
        now = datetime.now()

        self.time_label.setText(
            now.strftime("%I:%M %p")
        )

        self.date_label.setText(
            now.strftime("%d %b %Y").upper()
        )  