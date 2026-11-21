from pathlib import Path

ROOT = Path(r"C:\Mohsin_Vsh_News.tv")

# 1. src/app/main.py -> Closes MainWindow on logout & resets LoginWindow

(ROOT / "src/app/main.py").write_text('''import logging
import sys

from PySide6.QtWidgets import QApplication, QMessageBox

from src.app.bootstrap import build_services, start_logging
from src.app.ui.login_window import LoginWindow
from src.app.ui.main_window import MainWindow
from src.app.ui.style import apply_style

log = logging.getLogger(__name__)


class Shell:
    """Owns the top-level windows: login <-> main."""

    def __init__(self, services):
        self._services = services
        self._main = None
        self.login = LoginWindow(services.auth)
        self.login.authenticated.connect(self._open_main)

    def start(self) -> None:
        if self._main is not None:
            self._main.hide()
            self._main.close()
            self._main.deleteLater()
            self._main = None
        self.login.reset()
        self.login.show()
        self.login.raise_()
        self.login.activateWindow()

    def _open_main(self, session) -> None:
        self._main = MainWindow(self._services, session)
        self._main.logged_out.connect(self.start)
        self._main.show()
        self.login.hide()


def _excepthook(exc_type, exc, tb) -> None:
    log.critical("Unhandled error", exc_info=(exc_type, exc, tb))
    QMessageBox.critical(None, "Unexpected error",
                         "The application hit an unexpected error. Details were written to the log.")


def main() -> int:
    start_logging()
    sys.excepthook = _excepthook
    app = QApplication(sys.argv)
    apply_style(app)
    shell = Shell(build_services())
    shell.start()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
''', encoding="utf-8")

# 2. src/app/ui/login_window.py -> Both inputs empty on open/logout + EXIT button + VSH logo
(ROOT / "src/app/ui/login_window.py").write_text('''"""VSH NEWS TV - Professional ERP Login Window."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.app.application.services.auth_service import AuthError

OBSIDIAN_DARK = "#0B1120"
OBSIDIAN_CARD = "#111827"
RED = "#DC2626"
RED_DARK = "#991B1B"
GOLD = "#FACC15"
TEXT_LIGHT = "#F8FAFC"
MUTED = "#94A3B8"


def _find_logo() -> Path | None:
    bases = [Path(sys._MEIPASS)] if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS") else []
    bases.extend([Path(__file__).resolve().parents[3], Path.cwd()])
    for base in bases:
        for rel in ("assets/vsh_logo.png.png", "assets/vsh_logo.png", "vsh_logo.png.png"):
            p = base / rel
            if p.exists():
                return p
    return None


class LoginWindow(QWidget):
    authenticated = Signal(object)
    forgot_password_requested = Signal(str)

    def __init__(self, auth_service):
        super().__init__()
        self._auth = auth_service
        self.setWindowTitle("VSH NEWS TV | ERP Login")
        logo_path = _find_logo()
        if logo_path:
            self.setWindowIcon(QIcon(str(logo_path)))
        self.resize(500, 660)
        self.setMinimumSize(450, 590)
        self._build_ui()
        self.reset()

    def reset(self) -> None:
        self.user_input.clear()
        self.pass_input.clear()
        self.remember_box.setChecked(False)
        self.status_label.clear()
        self.login_button.setEnabled(True)
        self.login_button.setText("LOGIN")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.eye_button.setText("Show")
        self.user_input.setFocus()

    def _build_ui(self):
        self.setStyleSheet(f"""
            QWidget {{ font-family: 'Segoe UI'; color: {TEXT_LIGHT}; }}
            QWidget#loginWindow {{ background-color: {OBSIDIAN_DARK}; }}
            QFrame#loginCard {{ background-color: {OBSIDIAN_CARD}; border: 2px solid {RED}; border-radius: 18px; }}
            QLabel#companyName {{ color: #FFFFFF; font-size: 22px; font-weight: bold; }}
            QLabel#companySub {{ color: {MUTED}; font-size: 11px; }}
            QLabel#loginTitle {{ color: {GOLD}; font-size: 26px; font-weight: bold; }}
            QLabel#loginSubtitle {{ color: {MUTED}; font-size: 12px; }}
            QLineEdit {{
                background-color: #FFFFFF; color: #0F172A; border: 1px solid #334155;
                border-radius: 9px; padding: 12px; font-size: 13px; selection-background-color: {RED};
            }}
            QLineEdit:focus {{ border: 2px solid {RED}; }}
            QPushButton#loginButton {{
                background-color: {RED}; color: white; border: none;
                border-radius: 9px; padding: 13px; font-size: 14px; font-weight: bold;
            }}
            QPushButton#loginButton:hover {{ background-color: {RED_DARK}; }}
            QPushButton#exitButton {{
                background-color: #1E293B; color: #F87171; border: 1px solid #475569;
                border-radius: 9px; padding: 13px; font-size: 14px; font-weight: bold;
            }}
            QPushButton#exitButton:hover {{ background-color: #334155; color: #FFFFFF; }}
            QPushButton#forgotButton {{ color: {GOLD}; background: transparent; border: none; font-size: 11px; }}
            QPushButton#forgotButton:hover {{ color: white; text-decoration: underline; }}
            QPushButton#eyeButton {{
                background: #1E293B; color: #F8FAFC; border: 1px solid #334155;
                border-radius: 8px; font-size: 12px; padding: 10px 6px;
            }}
            QCheckBox {{ color: {MUTED}; font-size: 11px; spacing: 7px; }}
            QLabel#footer {{ color: {MUTED}; font-size: 10px; }}
            QLabel#status {{ color: {GOLD}; font-size: 11px; }}
        """)
        self.setObjectName("loginWindow")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(25, 25, 25, 25)

        self.card = QFrame()
        self.card.setObjectName("loginCard")
        self.card.setMaximumWidth(420)
        self.card.setMinimumWidth(370)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(32, 28, 32, 24)
        card_layout.setSpacing(15)

        branding = QVBoxLayout()
        branding.setAlignment(Qt.AlignmentFlag.AlignCenter)
        branding.setSpacing(5)

        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo.setFixedSize(112, 112)
        self._load_logo()
        branding.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)

        company_name = QLabel("VSH NEWS TV")
        company_name.setObjectName("companyName")
        company_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        branding.addWidget(company_name)

        company_sub = QLabel("Visionary Baluchistan Media Corporation (Pvt) Ltd")
        company_sub.setObjectName("companySub")
        company_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        branding.addWidget(company_sub)
        card_layout.addLayout(branding)

        title = QLabel("ERP Login")
        title.setObjectName("loginTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(title)

        subtitle = QLabel("Secure Access to Your System")
        subtitle.setObjectName("loginSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(subtitle)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        self.user_input.setClearButtonEnabled(True)
        card_layout.addWidget(self.user_input)

        password_layout = QHBoxLayout()
        password_layout.setSpacing(6)
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.returnPressed.connect(self._handle_login)

        self.eye_button = QPushButton("Show")
        self.eye_button.setObjectName("eyeButton")
        self.eye_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.eye_button.setFixedWidth(58)
        self.eye_button.clicked.connect(self._toggle_password)

        password_layout.addWidget(self.pass_input)
        password_layout.addWidget(self.eye_button)
        card_layout.addLayout(password_layout)

        options = QHBoxLayout()
        self.remember_box = QCheckBox("Remember Session")
        options.addWidget(self.remember_box)
        options.addStretch()
        self.forgot_button = QPushButton("Forgot Password?")
        self.forgot_button.setObjectName("forgotButton")
        self.forgot_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.forgot_button.clicked.connect(lambda: self.forgot_password_requested.emit(self.user_input.text().strip()))
        options.addWidget(self.forgot_button)
        card_layout.addLayout(options)

        self.status_label = QLabel("")
        self.status_label.setObjectName("status")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        card_layout.addWidget(self.status_label)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self.login_button = QPushButton("LOGIN")
        self.login_button.setObjectName("loginButton")
        self.login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.login_button.clicked.connect(self._handle_login)

        self.exit_button = QPushButton("EXIT")
        self.exit_button.setObjectName("exitButton")
        self.exit_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.exit_button.clicked.connect(self._handle_exit)

btn_row.addWidget(self.login_button, 2)
btn_row.addWidget(self.exit_button, 1)
card_layout.addLayout(btn_row)
footer = QLabel("VSH NEWS Accounting System  |  Version 1.0.0")
footer.setObjectName("footer")
footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
card_layout.addWidget(footer)
main_layout.addWidget(self.card)
def _load_logo(self):
logo_path = _find_logo()
if logo_path and logo_path.exists():
pixmap = QPixmap(str(logo_path))
self.logo.setPixmap(pixmap.scaled(108, 108, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
else:
self.logo.setText("VSH\nNEWS")
def _toggle_password(self):
if self.pass_input.echoMode() == QLineEdit.EchoMode.Password:
self.pass_input.setEchoMode(QLineEdit.EchoMode.Normal)
self.eye_button.setText("Hide")
else:
self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
self.eye_button.setText("Show")
def _handle_exit(self):
self.close()
app = QApplication.instance()
if app is not None:
app.quit()
def _handle_login(self):
username = self.user_input.text().strip()
password = self.pass_input.text()
if not username or not password:
QMessageBox.warning(self, "Validation Error", "Please enter both username and password.")
return
self.login_button.setEnabled(False)
self.login_button.setText("AUTHENTICATING...")
self.status_label.setText("Verifying credentials...")
try:
session = self._auth.login(username, password)
except AuthError as ex:
self.status_label.setText(str(ex))
self.pass_input.clear()
self.pass_input.setFocus()
except Exception:
self.status_label.setText("")
QMessageBox.critical(self, "Login Error", "An unexpected authentication error occurred.")
else:
self.status_label.setText("Authentication successful.")
self.user_input.clear()
self.pass_input.clear()
self.authenticated.emit(session)
finally:
self.login_button.setEnabled(True)
self.login_button.setText("LOGIN")
''', encoding="utf-8"
)