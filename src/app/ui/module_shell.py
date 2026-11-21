"""Shared module window shell for VSH NEWS TV ERP.

Strict ADR-0001 compliance: UI-only component; zero SQL or direct DB access.
Keeps the canonical VSH header, user role badge, live clock, and status bar
while applying a visual background theme driven by functional criteria.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

FUNCTIONAL_THEMES = {
    "master_data": {
        "bg": "#EDF4FC",
        "header_bg": "#1E3A8A",
        "accent": "#2563EB",
        "badge_bg": "#1D4ED8",
        "label": "MASTER DATA WORKSPACE",
    },
    "transactions": {
        "bg": "#ECFDF5",
        "header_bg": "#065F46",
        "accent": "#059669",
        "badge_bg": "#047857",
        "label": "TRANSACTIONS & VOUCHERS WORKSPACE",
    },
    "reports": {
        "bg": "#EEF2FF",
        "header_bg": "#3730A3",
        "accent": "#4F46E5",
        "badge_bg": "#4338CA",
        "label": "FINANCIAL REPORTING WORKSPACE",
    },
    "reconcile": {
        "bg": "#FFFBEB",
        "header_bg": "#92400E",
        "accent": "#D97706",
        "badge_bg": "#B45309",
        "label": "STATEMENTS & RECONCILIATION WORKSPACE",
    },
    "hr_payroll": {
        "bg": "#F0FDFA",
        "header_bg": "#115E59",
        "accent": "#0D9488",
        "badge_bg": "#0F766E",
        "label": "ATTENDANCE & PAYROLL WORKSPACE",
    },
    "admin": {
        "bg": "#FDF2F4",
        "header_bg": "#4B1427",
        "accent": "#881337",
        "badge_bg": "#6A2038",
        "label": "SYSTEM ADMINISTRATION & BACKUP",
    },
}


def resolve_vsh_logo() -> Path | None:
    """PyInstaller-safe logo resolver (ADR-0001 packaging compatible)."""
    bases = []
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bases.append(Path(sys._MEIPASS))
    bases.append(Path(__file__).resolve().parents[3])

    for base in bases:
        for rel in ("assets/vsh_logo.png.png", "assets/vsh_logo.png", "vsh_logo.png.png", "vsh_logo.png"):
            p = base / rel
            if p.exists():
                return p
    return None


def session_role_label(session) -> str:
    roles = getattr(session, "roles", None)
    if roles:
        return ", ".join(str(r) for r in roles)
    perms = getattr(session, "permissions", frozenset())
    if "user.manage" in perms or "account.manage" in perms:
        return "Administrator"
    return "Operator"


class VshModuleShellWindow(QMainWindow):
    """Independent top-level module window with VSH header, role badge, and functional theme."""

    def __init__(
        self,
        session,
        title: str,
        category: str,
        content_widget: QWidget,
        criteria_note: str = "",
        maximized: bool = False,
    ):
        super().__init__(parent=None)
        self._session = session
        theme = FUNCTIONAL_THEMES.get(category, FUNCTIONAL_THEMES["master_data"])

        self.setWindowTitle(f"VSH NEWS TV — {title}")
        self.resize(1340, 840)

        # --- Top Header (Matches Main Dashboard Head & Role Badge) ---
        header = QWidget()
        header.setObjectName("vshModuleHeader")
        header.setFixedHeight(80)
        h_row = QHBoxLayout(header)
        h_row.setContentsMargins(18, 10, 18, 10)
        h_row.setSpacing(14)

        logo = QLabel()
        logo.setFixedSize(58, 58)
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setStyleSheet(
            "background: #FFFFFF; border: 2px solid #C8A96B; border-radius: 8px; "
            "color: #4B1427; font-weight: 900; font-size: 11px;"
        )
        logo_path = resolve_vsh_logo()
        if logo_path:
            pix = QPixmap(str(logo_path))
            if not pix.isNull():
                logo.setPixmap(
                    pix.scaled(52, 52, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                )
        else:
            logo.setText("VSH\nNEWS")

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        lbl_top = QLabel(f"VSH NEWS TV  —  {title.upper()}")
        lbl_top.setStyleSheet("color: #FFFFFF; font-size: 18px; font-weight: 800;")
        sub_text = "Visionary Baluchistan Media Corporation (Pvt) Ltd"
        if criteria_note:
            sub_text += f"   |   Criteria: {criteria_note}"
        lbl_sub = QLabel(sub_text)
        lbl_sub.setStyleSheet("color: #E2E8F0; font-size: 11px;")
        title_col.addWidget(lbl_top)
        title_col.addWidget(lbl_sub)

        role_box = QLabel(
            f"User ID: {getattr(session, 'username', 'user')}\n"
            f"Role: {session_role_label(session)}"
        )
        role_box.setStyleSheet(
            f"background: {theme['badge_bg']}; color: #FFFFFF; border: 1px solid #C8A96B; "
            "padding: 6px 12px; border-radius: 7px; font-size: 11px; font-weight: 600;"
        )

        self._clock = QLabel()
        self._clock.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._clock.setStyleSheet("color: #FFFFFF; font-size: 11px; font-weight: 700;")
        self._tick()
        timer = QTimer(self)
        timer.timeout.connect(self._tick)
        timer.start(1000)

        h_row.addWidget(logo)
        h_row.addLayout(title_col, 1)
        h_row.addWidget(role_box)
        h_row.addWidget(self._clock)

        # --- Functional Body ---
        body = QWidget()
        body.setObjectName("vshFunctionalBody")
        b_lay = QVBoxLayout(body)
        b_lay.setContentsMargins(16, 14, 16, 14)
        b_lay.addWidget(content_widget)

        root = QWidget()
        r_lay = QVBoxLayout(root)
        r_lay.setContentsMargins(0, 0, 0, 0)
        r_lay.setSpacing(0)
        r_lay.addWidget(header)
        r_lay.addWidget(body, 1)
        self.setCentralWidget(root)

        status = QStatusBar()
        status.showMessage(
            f"Database: Connected (PostgreSQL)   |   {theme['label']}   |   "
            "VSH NEWS TV — Working for a Better Tomorrow"
        )
        self.setStatusBar(status)

        self.setStyleSheet(f"""
            QWidget#vshModuleHeader {{ background: {theme['header_bg']}; border-bottom: 3px solid #C8A96B; }}
            QWidget#vshFunctionalBody {{ background: {theme['bg']}; }}
            QTableWidget {{ background: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 6px; }}
            QPushButton {{
                background: #FFFFFF; border: 1px solid #CBD5E1;
                padding: 7px 14px; border-radius: 5px; font-weight: 600;
            }}
            QPushButton:hover {{ border-color: {theme['accent']}; }}
            QPushButton#primary {{ background: {theme['accent']}; color: #FFFFFF; border: none; }}
            QStatusBar {{ background: {theme['header_bg']}; color: #F8FAFC; font-size: 11px; }}
        """)

        if maximized:
            self.showMaximized()
        else:
            self.show()

    def _tick(self) -> None:
        now = datetime.now()
        self._clock.setText(now.strftime("%I:%M:%S %p\n%d-%b-%Y"))

