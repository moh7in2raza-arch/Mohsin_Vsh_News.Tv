from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)


class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("ERP Login")

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Username"))

        self.username = QLineEdit()
        layout.addWidget(self.username)

        layout.addWidget(QLabel("Password"))

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password)

        self.login_button = QPushButton("Login")
        layout.addWidget(self.login_button)

        self.setLayout(layout)
        