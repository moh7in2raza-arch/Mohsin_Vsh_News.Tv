from __future__ import annotations

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QTableWidget,
    QTableWidgetItem,
    QToolButton,
    QHeaderView,
    QMessageBox,
)

from src.app.ui.report_headings import USERS_HEADINGS
from src.app.ui.support import create_export_menu, export_table


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
        self.export_button = QToolButton()
        self.export_button.setText("Export")
        self.export_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.export_button.setMenu(create_export_menu(self.export_button, self._export))

        button_row.addWidget(self.add_button)
        button_row.addWidget(self.edit_button)
        button_row.addWidget(self.reset_button)
        button_row.addWidget(self.disable_button)
        button_row.addWidget(self.role_button)

        button_row.addStretch()

        button_row.addWidget(self.refresh_button)
        button_row.addWidget(self.export_button)

        layout.addLayout(button_row)

        # ------------------------------------------------
        # Users Table
        # ------------------------------------------------

        self.table = QTableWidget()

        self.table.setColumnCount(6)

        self.table.setHorizontalHeaderLabels(
            list(USERS_HEADINGS)
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

        rows = [
            (
                user.get("username", ""),
                user.get("designation", ""),
                user.get("add_edit_rights", ""),
                user.get("delete_rights", ""),
                user.get("reports_access", ""),
                user.get("backup_restore", ""),
            )
            for user in users
        ]
        self.table.setRowCount(len(users))

        for row_index, values in enumerate(rows):
            for column, value in enumerate(values):
                self.table.setItem(
                    row_index, column, QTableWidgetItem(str(value or ""))
                )

    def _export(self, file_format: str) -> None:
        rows = [
            tuple(
                self.table.item(row, column).text()
                if self.table.item(row, column) is not None else ""
                for column in range(self.table.columnCount())
            )
            for row in range(self.table.rowCount())
        ]
        export_table(self, "Users", USERS_HEADINGS, rows, file_format)

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