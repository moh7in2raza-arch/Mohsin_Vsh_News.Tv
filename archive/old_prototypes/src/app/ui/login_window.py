import logging

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.app.application.services.auth_service import AuthError

log = logging.getLogger(__name__)


class LoginWindow(QWidget):
    """Pure view: collects credentials, asks the AuthService, emits the Session."""

    login_succeeded = Signal(object)

    def __init__(self, auth_service):
        super().__init__()
        self._auth = auth_service
        self.setWindowTitle("ERP Office Management - Login")
        self.setMinimumWidth(360)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(8)

        title = QLabel("ERP Office Management")
        title.setObjectName("title")
        layout.addWidget(title)

        layout.addWidget(QLabel("Username"))
        self.username = QLineEdit()
        layout.addWidget(self.username)

        layout.addWidget(QLabel("Password"))
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.password)

        self.error = QLabel("")
        self.error.setObjectName("error")
        self.error.setWordWrap(True)
        layout.addWidget(self.error)

        self.login_button = QPushButton("Login")
        self.login_button.setObjectName("primary")
        self.login_button.setDefault(True)
        layout.addWidget(self.login_button)

        self.username.returnPressed.connect(self.password.setFocus)
        self.password.returnPressed.connect(self.handle_login)
        self.login_button.clicked.connect(self.handle_login)

    def reset(self) -> None:
        self.password.clear()
        self.error.clear()
        self.username.setFocus()

    def handle_login(self) -> None:
        self.error.clear()
        try:
            session = self._auth.login(self.username.text().strip(), self.password.text())
        except AuthError as ex:
            self.error.setText(str(ex))
            self.password.clear()
            return
        except Exception:
            log.exception("Login failed unexpectedly")
            self.error.setText("Cannot reach the database. Check the .env settings "
                               "and that PostgreSQL is running.")
            return
        self.password.clear()
        self.login_succeeded.emit(session)
        