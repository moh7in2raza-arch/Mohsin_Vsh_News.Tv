import csv

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from src.app.domain.accounting.chart import ACCOUNT_TYPES
from src.app.domain.security import permissions as P
from src.app.ui.report_headings import ACCOUNTS_HEADINGS
from src.app.ui.support import (
    call_service,
    export_table,
    fill_table,
)

_HEADERS = ACCOUNTS_HEADINGS


class _AccountDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New account")
        self.code = QLineEdit()
        self.name = QLineEdit()
        self.type = QComboBox()
        self.type.addItems(list(ACCOUNT_TYPES))
        form = QFormLayout(self)
        form.addRow("Code", self.code)
        form.addRow("Name", self.name)
        form.addRow("Type", self.type)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)


class AccountsView(QWidget):

    def __init__(self, services, session):
        super().__init__()
        self._accounts = services.accounts
        self._session = session
        self._rows = []

        self.btn_new = QPushButton("New account")
        self.btn_new.setObjectName("primary")
        self.btn_new.setEnabled(session.has(P.ACCOUNT_MANAGE))
        self.btn_new.clicked.connect(self._new)

        self.btn_save = QPushButton("Export")
        save_menu = QMenu(self.btn_save)
        act_preview = QAction("Print Preview", self)
        act_pdf = QAction("Save as PDF (*.pdf)", self)
        act_txt = QAction("Save as TXT (*.txt)", self)
        act_md = QAction("Save as Markdown (*.md)", self)
        act_csv = QAction("Save as CSV (*.csv)", self)
        act_xlsx = QAction("Save as Excel (*.xlsx)", self)
        act_preview.triggered.connect(lambda: self._export("print"))
        act_pdf.triggered.connect(lambda: self._export("pdf"))
        act_txt.triggered.connect(lambda: self._export("txt"))
        act_md.triggered.connect(lambda: self._export("md"))
        act_csv.triggered.connect(self._save_csv)
        act_xlsx.triggered.connect(self._save_excel)
        save_menu.addAction(act_preview)
        save_menu.addAction(act_pdf)
        save_menu.addAction(act_txt)
        save_menu.addAction(act_md)
        save_menu.addAction(act_csv)
        save_menu.addAction(act_xlsx)
        self.btn_save.setMenu(save_menu)

        bar = QHBoxLayout()
        bar.addStretch()
        bar.addWidget(self.btn_new)
        bar.addWidget(self.btn_save)

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        fill_table(self.table, _HEADERS, [])

        layout = QVBoxLayout(self)
        layout.addLayout(bar)
        layout.addWidget(self.table)

    def _indent_level(self, code: str) -> int:
        c = str(code).strip()
        if "-" in c:
            return c.count("-")
        if len(c) <= 1:
            return 0
        if len(c) <= 4:
            return 1
        return 2

    def _data(self):
        return [
            (a.code, f"{'    ' * self._indent_level(a.code)}{a.name}", a.type,
             "", "", a.is_active)
            for a in self._rows
        ]

    def refresh(self) -> None:
        ok, rows = call_service(self, self._accounts.list_accounts, self._session, False)
        self._rows = rows if ok else []
        fill_table(self.table, _HEADERS, self._data())

    def _new(self) -> None:
        dialog = _AccountDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            ok, _ = call_service(
                self,
                self._accounts.create_account,
                self._session,
                dialog.code.text(),
                dialog.name.text(),
                dialog.type.currentText(),
            )
            if ok:
                self.refresh()

    def _save_pdf(self) -> None:
        self._export("pdf")

    def _export(self, file_format: str) -> None:
        export_table(
            self, "Chart of Accounts", _HEADERS, self._data(), file_format,
            right_cols=(3, 4),
        )

    def _save_csv(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Chart of Accounts (CSV)", "Chart_of_Accounts.csv", "CSV Files (*.csv)"
        )
        if not path:
            return
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Visionary Baluchistan Media Corporation (Pvt) Ltd"])
            writer.writerow(["CHART OF ACCOUNTS"])
            writer.writerow([])
            writer.writerow(_HEADERS)
            writer.writerows(self._data())
        QMessageBox.information(self, "Saved", f"Chart of Accounts saved to:\n{path}")

    def _save_excel(self) -> None:
        try:
            import openpyxl
            from openpyxl.styles import Alignment, Font
        except ImportError:
            QMessageBox.warning(
                self, "Missing Package", "Please install openpyxl first:\npip install openpyxl"
            )
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "Save Chart of Accounts (Excel)", "Chart_of_Accounts.xlsx", "Excel Files (*.xlsx)"
        )
        if not path:
            return

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Chart of Accounts"
        ws.append(["Visionary Baluchistan Media Corporation (Pvt) Ltd"])
        ws.append(["CHART OF ACCOUNTS"])
        ws.append([])
        ws.append(_HEADERS)
        for cell in ws:
            cell.font = Font(bold=True)

        for a, data in zip(self._rows, self._data()):
            level = self._indent_level(a.code)
            ws.append(list(data))
            r_idx = ws.max_row
            ws.cell(row=r_idx, column=2).alignment = Alignment(indent=level * 2)
            if level == 0:
                for col in range(1, len(_HEADERS) + 1):
                    ws.cell(row=r_idx, column=col).font = Font(bold=True)

        for column, width in zip("ABCDEF", (16, 55, 18, 18, 18, 12)):
            ws.column_dimensions[column].width = width
        wb.save(path)
        QMessageBox.information(self, "Saved", f"Chart of Accounts saved to:\n{path}")

