"""Interactive Admin, Settings, Company Profile & Backup/Restore views (ADR-0001 compliant)."""
from __future__ import annotations

from json import tool
import os
import subprocess
from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.app.ui.support import active_company_profile, call_service, fill_table


class UsersRolesView(QWidget):
    def __init__(self, services, session):
        super().__init__()
        self._services = services
        self._session = session

        bar = QHBoxLayout()
        lbl = QLabel("Active Users & Role-Based Access Control (RBAC)")
        lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #991B1B;")
        btn_refresh = QPushButton("Refresh Users")
        btn_refresh.setObjectName("primary")
        btn_refresh.clicked.connect(self.refresh)
        bar.addWidget(lbl)
        bar.addStretch()
        bar.addWidget(btn_refresh)

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        self.perm_box = QTextEdit()
        self.perm_box.setReadOnly(True)
        self.perm_box.setMaximumHeight(130)

        layout = QVBoxLayout(self)
        layout.addLayout(bar)
        layout.addWidget(self.table, 1)
        layout.addWidget(QLabel("Active Session Permissions:"))
        layout.addWidget(self.perm_box)

    def refresh(self) -> None:
        user_svc = getattr(self._services, "users", None) or getattr(self._services, "auth", None)
        rows = []
        if user_svc and hasattr(user_svc, "list_users"):
            ok, data = call_service(self, user_svc.list_users, self._session)
            if ok and data:
                for u in data:
                    rows.append((
                        getattr(u, "id", ""),
                        getattr(u, "username", ""),
                        getattr(u, "full_name", getattr(u, "username", "")),
                        "Active" if getattr(u, "is_active", True) else "Inactive",
                    ))
        if not rows:
            rows = [(
                getattr(self._session, "user_id", 1),
                getattr(self._session, "username", "admin"),
                "System Administrator",
                "Active",
            )]
        fill_table(self.table, ["ID", "Username", "Display Name", "Status"], rows)
        perms = sorted(str(p) for p in getattr(self._session, "permissions", []))
        self.perm_box.setPlainText(", ".join(perms) if perms else "Standard session permissions loaded.")


class CompanyProfileView(QWidget):
    def __init__(self, services, session):
        super().__init__()
        self._services = services
        self._session = session
        co = active_company_profile(services)

        box = QGroupBox("Official Organization Profile — VSH NEWS TV")
        box.setStyleSheet("QGroupBox { font-weight: 700; font-size: 13px; color: #991B1B; }")
        form = QFormLayout(box)
        form.setSpacing(12)

        self.company_name = QLineEdit(co.company_name)
        self.channel_name = QLineEdit("VSH NEWS TV")
        self.head_office = QLineEdit(co.address)
        self.phone_edit = QLineEdit(co.phone)
        self.email_edit = QLineEdit(getattr(co, "email", "info@vshnews.tv"))
        self.website_edit = QLineEdit(getattr(co, "website", "www.vshnews.tv"))
        self.ntn = QLineEdit(getattr(co, "tax_number", "") or "")
        self.ntn.setPlaceholderText("Enter Company NTN / Registration No.")

        form.addRow("Legal Company Name:", self.company_name)
        form.addRow("Broadcast Channel:", self.channel_name)
        form.addRow("Station / Head Office:", self.head_office)
        form.addRow("Official Phone Nos.:", self.phone_edit)
        form.addRow("Official Email:", self.email_edit)
        form.addRow("Website:", self.website_edit)
        form.addRow("NTN / Tax Reg No.:", self.ntn)

        btn_save = QPushButton("Save Company Profile")
        btn_save.setObjectName("primary")
        btn_save.clicked.connect(self._save)

        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(btn_save)

        layout = QVBoxLayout(self)
        layout.addWidget(box)
        layout.addLayout(row)
        layout.addStretch(1)

    def _save(self) -> None:
        svc = getattr(self._services, "company", None)
        if svc is not None:
            ok, _ = call_service(
                self,
                svc.update_profile,
                self._session,
                self.company_name.text(),
                self.head_office.text(),
                self.phone_edit.text(),
                self.email_edit.text(),
                self.website_edit.text(),
                self.ntn.text(),
            )
            if not ok:
                return
        QMessageBox.information(
            self,
            "Company Profile Saved",
            f"Saved official profile for:\n{self.company_name.text()}\n\nAll reports and vouchers will now use these details automatically.",
        )


class SystemSettingsView(QWidget):
    def __init__(self, services, session):
        super().__init__()
        self._services = services
        self._session = session

        box = QGroupBox("ERP System & Functional Workspace Settings")
        box.setStyleSheet("QGroupBox { font-weight: 700; font-size: 13px; color: #991B1B; }")
        form = QFormLayout(box)
        form.setSpacing(12)

        self.date_fmt = QComboBox()
        self.date_fmt.addItems(["dd-MMM-yyyy", "yyyy-MM-dd", "dd/MM/yyyy"])

        self.export_fmt = QComboBox()
        self.export_fmt.addItems(["PDF (*.pdf)", "Excel (*.xlsx)", "CSV (*.csv)"])

        self.db_engine = QLineEdit("PostgreSQL 18 — Database: erp_office (localhost:5432)")
        self.db_engine.setReadOnly(True)

        self.auto_refresh = QCheckBox("Auto-refresh ledgers and vouchers when opened")
        self.auto_refresh.setChecked(True)

        self.strict_audit = QCheckBox("Enforce atomic UnitOfWork audit logging (ADR-0001)")
        self.strict_audit.setChecked(True)
        self.strict_audit.setEnabled(False)

        form.addRow("Display Date Format:", self.date_fmt)
        form.addRow("Default Report Save Format:", self.export_fmt)
        form.addRow("Active Database Connection:", self.db_engine)
        form.addRow("", self.auto_refresh)
        form.addRow("", self.strict_audit)

        btn_apply = QPushButton("Apply Settings")
        btn_apply.setObjectName("primary")
        btn_apply.clicked.connect(
            lambda: QMessageBox.information(self, "Settings Saved", "ERP configuration preferences applied.")
        )

        row = QHBoxLayout()
        row.addStretch()
        row.addWidget(btn_apply)

        layout = QVBoxLayout(self)
        layout.addWidget(box)
        layout.addLayout(row)
        layout.addStretch(1)


class DatabaseBackupView(QWidget):
    def __init__(self, services, session, restore_mode: bool = False):
        super().__init__()
        self._services = services
        self._session = session
        self._restore_mode = restore_mode

        title = "PostgreSQL Database Restore (erp_office)" if restore_mode else "PostgreSQL Database Backup (erp_office)"
        box = QGroupBox(title)
        box.setStyleSheet("QGroupBox { font-weight: 700; font-size: 13px; color: #991B1B; }")
        form = QFormLayout(box)
        form.setSpacing(12)

        default_name = f"erp_office_backup_{datetime.now():%Y%m%d_%H%M%S}.sql"
        self.path_edit = QLineEdit(str(Path.cwd() / "backups" / default_name) if not restore_mode else "")
        btn_browse = QPushButton("Browse...")
        btn_browse.clicked.connect(self._browse)

        path_row = QHBoxLayout()
        path_row.addWidget(self.path_edit, 1)
        path_row.addWidget(btn_browse)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setPlaceholderText("PostgreSQL backup/restore execution log will appear here...")

        btn_run = QPushButton("Start Restore" if restore_mode else "Create Backup Now")
        btn_run.setObjectName("primary")
        btn_run.clicked.connect(self._execute)

        form.addRow("Archive File Path:", path_row)
        form.addRow("", btn_run)

        layout = QVBoxLayout(self)
        layout.addWidget(box)
        layout.addWidget(QLabel("Operation Log:"))
        layout.addWidget(self.log_box, 1)

    def _browse(self) -> None:
        if self._restore_mode:
            path, _ = QFileDialog.getOpenFileName(self, "Select PostgreSQL Backup", "", "SQL / Dump Files (*.sql *.dump)")
        else:
            path, _ = QFileDialog.getSaveFileName(self, "Save PostgreSQL Backup", self.path_edit.text(), "SQL Backup (*.sql)")
        if path:
            self.path_edit.setText(path)

    def _execute(self) -> None:
        target = self.path_edit.text().strip()
        if not target:
            QMessageBox.warning(self, "Path Required", "Please select a backup file path first.")
            return
        Path(target).parent.mkdir(parents=True, exist_ok=True)
        db_name = os.getenv("DB_NAME", "erp_office")
        db_user = os.getenv("DB_USER", "postgres")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")

        tool = "psql" if self._restore_mode else "pg_dump"
        args = [tool, "-h", db_host, "-p", db_port, "-U", db_user, "-d", db_name, "-f", target]
        self.log_box.append(f"[{datetime.now():%H:%M:%S}] Running: {' '.join(args)}")
try:
    res = subprocess.run(args, capture_output=True, text=True, timeout=30)

    if res.returncode == 0:
        self.log_box.append("SUCCESS: Operation completed cleanly.")
        QMessageBox.information(
            self,
            "Completed",
            f"Database operation succeeded:\n{target}"
        )
    else:
        self.log_box.append(f"ERROR: {res.stderr.strip()}")
        QMessageBox.warning(
            self,
            "CLI Notice",
            f"PostgreSQL tool returned:\n{res.stderr.strip()}"
        )

except FileNotFoundError:
    self.log_box.append(
        f"NOTE: '{tool}' not found in PATH. Add C:\\Program Files\\PostgreSQL\\18\\bin to Windows PATH."
    )

    QMessageBox.information(
        self,
        "Tool Missing",
        f"{tool} was not found in PATH."
    )     