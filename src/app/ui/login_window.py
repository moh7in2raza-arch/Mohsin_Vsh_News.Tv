
"""VSH NEWS TV - Professional ERP Login Window."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, Signal, QSettings
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
)

from src.app.application.services.auth_service import AuthError


WINE = "#4B1427"
WINE_DARK = "#32101D"
RED = "#D71920"
RED_DARK = "#A90F18"
GOLD = "#C8A96B"
IVORY = "#F7F3EA"
CHARCOAL = "#28252A"
MUTED = "#D8C5A2"


class LoginWindow(QWidget):

    authenticated = Signal(object)
    forgot_password_requested = Signal(str)

    def __init__(self, auth_service):
        super().__init__()

        self._auth = auth_service
        self._settings = QSettings(
            "VSH NEWS TV",
            "VSH NEWS ERP"
        )

        self.setWindowTitle("VSH NEWS TV | ERP Login")
        self.resize(500, 650)
        self.setMinimumSize(450, 580)

        self._build_ui()
        self._load_preferences()

    def reset(self) -> None:
        self.pass_input.clear()
        self.status_label.clear()
        self.login_button.setEnabled(True)
        self.login_button.setText("LOGIN")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.eye_button.setText("Show")
        if self.user_input.text():
            self.pass_input.setFocus()
        else:
            self.user_input.setFocus()

    # --------------------------------------------------
    # USER INTERFACE
    # --------------------------------------------------

    def _build_ui(self):

        self.setStyleSheet(f"""
            QWidget {{
                font-family: 'Segoe UI';
                color: {IVORY};
            }}

            QWidget#loginWindow {{
                background-color: {WINE_DARK};
            }}

            QFrame#loginCard {{
                background-color: {WINE};
                border: 1px solid {GOLD};
                border-radius: 18px;
            }}

            QLabel#companyName {{
                color: {IVORY};
                font-size: 21px;
                font-weight: bold;
            }}

            QLabel#companySub {{
                color: {MUTED};
                font-size: 11px;
            }}

            QLabel#loginTitle {{
                color: {GOLD};
                font-size: 28px;
                font-weight: bold;
            }}

            QLabel#loginSubtitle {{
                color: {MUTED};
                font-size: 12px;
            }}

            QLineEdit {{
                background-color: #FFFFFF;
                color: {CHARCOAL};
                border: 1px solid {GOLD};
                border-radius: 9px;
                padding: 13px;
                font-size: 13px;
                selection-background-color: {RED};
            }}

            QLineEdit:focus {{
                border: 2px solid {GOLD};
            }}

            QPushButton#loginButton {{
                background-color: {RED};
                color: white;
                border: none;
                border-radius: 9px;
                padding: 13px;
                font-size: 15px;
                font-weight: bold;
            }}

            QPushButton#loginButton:hover {{
                background-color: {RED_DARK};
            }}

            QPushButton#loginButton:disabled {{
                background-color: #777777;
            }}

            QPushButton#forgotButton {{
                color: {GOLD};
                background: transparent;
                border: none;
                font-size: 11px;
                text-align: right;
            }}

            QPushButton#forgotButton:hover {{
                color: white;
                text-decoration: underline;
            }}

            QPushButton#eyeButton {{
                background: transparent;
                color: {WINE};
                border: none;
                font-size: 14px;
                padding: 5px;
            }}

            QCheckBox {{
                color: {MUTED};
                font-size: 11px;
                spacing: 7px;
            }}

            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
            }}

            QLabel#footer {{
                color: #D8C5A2;
                font-size: 10px;
            }}

            QLabel#status {{
                color: #FFD27F;
                font-size: 11px;
            }}
        """)

        self.setObjectName("loginWindow")

        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setContentsMargins(25, 25, 25, 25)

        # LOGIN CARD
        self.card = QFrame()
        self.card.setObjectName("loginCard")
        self.card.setMaximumWidth(410)
        self.card.setMinimumWidth(360)

        card_layout = QVBoxLayout(self.card)
        card_layout.setContentsMargins(32, 30, 32, 25)
        card_layout.setSpacing(17)

        # COMPANY BRANDING
        branding = QVBoxLayout()
        branding.setAlignment(Qt.AlignmentFlag.AlignCenter)
        branding.setSpacing(5)

        self.logo = QLabel()
        self.logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo.setFixedSize(110, 110)

        self._load_logo()

        branding.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignCenter)

        company_name = QLabel("VSH NEWS TV")
        company_name.setObjectName("companyName")
        company_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        branding.addWidget(company_name)

        company_sub = QLabel(
            "Media Corporation (Pvt.) Limited"
        )
        company_sub.setObjectName("companySub")
        company_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        branding.addWidget(company_sub)

        card_layout.addLayout(branding)

        # LOGIN HEADING
        title = QLabel("ERP Login")
        title.setObjectName("loginTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(title)

        subtitle = QLabel("Secure Access to Your System")
        subtitle.setObjectName("loginSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(subtitle)

        # USERNAME
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        self.user_input.setClearButtonEnabled(True)

        card_layout.addWidget(self.user_input)

        # PASSWORD
        password_layout = QHBoxLayout()
        password_layout.setSpacing(5)

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(
            QLineEdit.EchoMode.Password
        )

        self.pass_input.returnPressed.connect(
            self._handle_login
        )

        self.eye_button = QPushButton("Show")
        self.eye_button.setObjectName("eyeButton")
        self.eye_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )
        self.eye_button.setFixedWidth(55)

        self.eye_button.clicked.connect(
            self._toggle_password
        )

        password_layout.addWidget(self.pass_input)
        password_layout.addWidget(self.eye_button)

        card_layout.addLayout(password_layout)

        # REMEMBER AND FORGOT PASSWORD
        options = QHBoxLayout()

        self.remember_box = QCheckBox("Remember Me")

        options.addWidget(self.remember_box)
        options.addStretch()

        self.forgot_button = QPushButton("Forgot Password?")
        self.forgot_button.setObjectName("forgotButton")
        self.forgot_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.forgot_button.clicked.connect(
            self._handle_forgot_password
        )

        options.addWidget(self.forgot_button)

        card_layout.addLayout(options)

        # STATUS MESSAGE
        self.status_label = QLabel("")
        self.status_label.setObjectName("status")
        self.status_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter
        )

        card_layout.addWidget(self.status_label)

        # LOGIN BUTTON
        self.login_button = QPushButton("LOGIN")
        self.login_button.setObjectName("loginButton")
        self.login_button.setCursor(
            Qt.CursorShape.PointingHandCursor
        )

        self.login_button.clicked.connect(
            self._handle_login
        )

        card_layout.addWidget(self.login_button)

        # FOOTER
        footer = QLabel(
            "VSH NEWS Accounting System  |  Version 1.0.0"
        )
        footer.setObjectName("footer")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        card_layout.addWidget(footer)

        main_layout.addWidget(self.card)

    # --------------------------------------------------
    # COMPANY LOGO
    # --------------------------------------------------

    def _load_logo(self):

        logo_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "vsh_logo.png.png"
        )

        if logo_path.exists():

            pixmap = QPixmap(str(logo_path))

            self.logo.setPixmap(
                pixmap.scaled(
                    105,
                    105,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )

        else:

            self.logo.setText("VSH\nNEWS")
            self.logo.setStyleSheet(f"""
                background-color: {RED};
                color: white;
                border-radius: 12px;
                font-size: 22px;
                font-weight: bold;
            """)

    # --------------------------------------------------
    # PASSWORD VISIBILITY
    # --------------------------------------------------

    def _toggle_password(self):

        if self.pass_input.echoMode() == (
            QLineEdit.EchoMode.Password
        ):

            self.pass_input.setEchoMode(
                QLineEdit.EchoMode.Normal
            )

            self.eye_button.setText("Hide")

        else:

            self.pass_input.setEchoMode(
                QLineEdit.EchoMode.Password
            )

            self.eye_button.setText("Show")

    # --------------------------------------------------
    # USER PREFERENCES
    # --------------------------------------------------

    def _load_preferences(self):

        saved_username = self._settings.value(
            "login/username",
            "",
            type=str
        )

        if saved_username:

            self.user_input.setText(saved_username)
            self.remember_box.setChecked(True)
            self.pass_input.setFocus()

        else:

            self.user_input.setFocus()

    def _save_preferences(self, username):

        if self.remember_box.isChecked():

            self._settings.setValue(
                "login/username",
                username
            )

        else:

            self._settings.remove("login/username")

    # --------------------------------------------------
    # FORGOT PASSWORD
    # --------------------------------------------------

    def _handle_forgot_password(self):

        username = self.user_input.text().strip()

        self.forgot_password_requested.emit(username)

    # --------------------------------------------------
    # AUTHENTICATION
    # --------------------------------------------------

    def _handle_login(self):

        username = self.user_input.text().strip()
        password = self.pass_input.text()

        if not username or not password:

            QMessageBox.warning(
                self,
                "Validation Error",
                "Please enter both username and password."
            )

            return

        self.login_button.setEnabled(False)
        self.login_button.setText("AUTHENTICATING...")
        self.status_label.setText("Verifying credentials...")

        try:

            session = self._auth.login(
                username,
                password
            )

        except AuthError as ex:

            self.status_label.setText(str(ex))
            self.pass_input.clear()
            self.pass_input.setFocus()

        except Exception:

            self.status_label.setText("")

            QMessageBox.critical(
                self,
                "Login Error",
                "An unexpected authentication error occurred. "
                "Please contact your system administrator."
            )

        else:

            self._save_preferences(username)

            self.status_label.setText(
                "Authentication successful."
            )

            self.pass_input.clear()
            self.authenticated.emit(session)

        finally:

            self.login_button.setEnabled(True)
            self.login_button.setText("LOGIN")
