from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)


class UsersView(QWidget):
    """
    Users & Roles Management Screen

    ADR Rules:
    - No SQL
    - No Repository Access
    - No Database Calls
    - All data comes through UserService
    """

    def __init__(self, user_service, parent=None):
        super().__init__(parent)

        self.user_service = user_service

        self._build_ui()
        self.load_users()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # ------------------------------------------------
        # Title
        # ------------------------------------------------

        title = QLabel("Users & Roles")
        title.setStyleSheet(
            """
            font-size: 20px;
            font-weight: bold;
            """
        )

        layout.addWidget(title)

        subtitle = QLabel(
            "Manage application users, roles and permissions."
        )

        subtitle.setStyleSheet(
            """
            color: #666;
            font-size: 11px;
            """
        )

        layout.addWidget(subtitle)

        # ------------------------------------------------
        # Search
        # ------------------------------------------------

        search_row = QHBoxLayout()

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText(
            "Search user..."
        )

        self.search_edit.textChanged.connect(
            self.filter_users
        )

        search_row.addWidget(self.search_edit)

        layout.addLayout(search_row)

        # ------------------------------------------------
        # Action Buttons
        # ------------------------------------------------

        button_row = QHBoxLayout()

        self.add_button = QPushButton("Add User")
        self.edit_button = QPushButton("Edit User")
        self.reset_button = QPushButton("Reset Password")
        self.disable_button = QPushButton("Disable User")
        self.role_button = QPushButton("Assign Role")
        self.refresh_button = QPushButton("Refresh")

        button_row.addWidget(self.add_button)
        button_row.addWidget(self.edit_button)
        button_row.addWidget(self.reset_button)
        button_row.addWidget(self.disable_button)
        button_row.addWidget(self.role_button)

        button_row.addStretch()

        button_row.addWidget(self.refresh_button)

        layout.addLayout(button_row)

        # ------------------------------------------------
        # Users Table
        # ------------------------------------------------

        self.table = QTableWidget()

        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels(
            [
                "Username",
                "Employee",
                "Role",
                "Status",
                "Last Login",
                "Must Change Password",
            ]
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        self.table.setSelectionMode(
            QTableWidget.SelectionMode.SingleSelection
        )

        self.table.setAlternatingRowColors(True)

        layout.addWidget(self.table)

        # ------------------------------------------------
        # Signals
        # ------------------------------------------------

        self.refresh_button.clicked.connect(
            self.load_users
        )

        self.add_button.clicked.connect(
            self.add_user
        )

        self.edit_button.clicked.connect(
            self.edit_user
        )

        self.reset_button.clicked.connect(
            self.reset_password
        )

        self.disable_button.clicked.connect(
            self.disable_user
        )

        self.role_button.clicked.connect(
            self.assign_role
        )

    def load_users(self):
        """
        Load users from UserService.
        """

        users = []

        try:
            users = self.user_service.get_all_users()

        except Exception as ex:
            QMessageBox.warning(
                self,
                "Users",
                str(ex),
            )

        self.table.setRowCount(len(users))

        for row, user in enumerate(users):

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(
                    str(user.get("username", ""))
                ),
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(
                    str(user.get("employee_name", ""))
                ),
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(
                    str(user.get("role_name", ""))
                ),
            )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(
                    "Active"
                    if user.get("is_active")
                    else "Disabled"
                ),
            )

            self.table.setItem(
                row,
                4,
                QTableWidgetItem(
                    str(user.get("last_login", ""))
                ),
            )

            self.table.setItem(
                row,
                5,
                QTableWidgetItem(
                    "Yes"
                    if user.get("must_change_password")
                    else "No"
                ),
            )

    def filter_users(self):
        text = self.search_edit.text().lower()

        for row in range(self.table.rowCount()):
            username_item = self.table.item(row, 0)

            if username_item is None:
                continue

            visible = (
                text in username_item.text().lower()
            )

            self.table.setRowHidden(
                row,
                not visible,
            )

    def selected_username(self):
        row = self.table.currentRow()

        if row < 0:
            return None

        item = self.table.item(row, 0)

        if item:
            return item.text()

        return None

    def add_user(self):
        QMessageBox.information(
            self,
            "Users",
            "Add User screen will be implemented next.",
        )

    def edit_user(self):
        username = self.selected_username()

        if not username:
            return

        QMessageBox.information(
            self,
            "Users",
            f"Edit User: {username}",
        )

    def reset_password(self):
        username = self.selected_username()

        if not username:
            return

        QMessageBox.information(
            self,
            "Users",
            f"Reset Password: {username}",
        )

    def disable_user(self):
        username = self.selected_username()

        if not username:
            return

        QMessageBox.information(
            self,
            "Users",
            f"Disable User: {username}",
        )

    def assign_role(self):
        username = self.selected_username()

        if not username:
            return

        QMessageBox.information(
            self,
            "Users",
            f"Assign Role: {username}",
        )