from datetime import date
from decimal import Decimal, InvalidOperation

from PySide6.QtCore import QDate, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
)

_ZERO = Decimal("0")


def _amount(edit: QLineEdit) -> Decimal:
    try:
        return Decimal(edit.text().strip() or "0")
    except InvalidOperation:
        return _ZERO


class VoucherDialog(QDialog):
    """Voucher entry form. Returns plain values; the service validates them."""

    def __init__(self, accounts, parent=None):
        super().__init__(parent)
        self.setWindowTitle("New voucher")
        self.resize(760, 480)
        self._accounts = accounts

        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("dd-MMM-yyyy")
        self.narration = QLineEdit()
        form = QFormLayout()
        form.addRow("Date", self.date)
        form.addRow("Narration", self.narration)

        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Account", "Debit", "Credit"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        add = QPushButton("Add line")
        add.clicked.connect(self.add_row)
        remove = QPushButton("Remove selected line")
        remove.clicked.connect(self._remove_row)
        tools = QHBoxLayout()
        tools.addWidget(add)
        tools.addWidget(remove)
        tools.addStretch()

        self.summary = QLabel()
        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.table)
        layout.addLayout(tools)
        layout.addWidget(self.summary)
        layout.addWidget(self.buttons)

        self.add_row()
        self.add_row()

    def add_row(self) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        combo = QComboBox()
        combo.addItem("Select account...", None)
        for a in self._accounts:
            combo.addItem(f"{a.code} - {a.name}", a.id)
        combo.currentIndexChanged.connect(self._refresh)
        self.table.setCellWidget(row, 0, combo)
        validator = QRegularExpressionValidator(QRegularExpression(r"^\d{0,12}(\.\d{0,2})?$"))
        for col in (1, 2):
            edit = QLineEdit()
            edit.setValidator(validator)
            edit.setPlaceholderText("0.00")
            edit.textChanged.connect(self._refresh)
            self.table.setCellWidget(row, col, edit)
        self._refresh()

    def _remove_row(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
            self._refresh()

    def _read(self):
        lines, ok = [], True
        for r in range(self.table.rowCount()):
            account_id = self.table.cellWidget(r, 0).currentData()
            debit = _amount(self.table.cellWidget(r, 1))
            credit = _amount(self.table.cellWidget(r, 2))
            if debit == 0 and credit == 0:
                continue
            if account_id is None or (debit > 0) == (credit > 0):
                ok = False
            lines.append({"account_id": account_id, "debit": debit, "credit": credit})
        return lines, ok

    def _refresh(self) -> None:
        lines, ok = self._read()
        debit = sum((l["debit"] for l in lines), _ZERO)
        credit = sum((l["credit"] for l in lines), _ZERO)
        balanced = ok and len(lines) >= 2 and debit == credit and debit > 0
        self.summary.setText(
            f"Debit {debit:,.2f}   Credit {credit:,.2f}   Difference {debit - credit:,.2f}"
        )
        self.summary.setObjectName("ok" if balanced else "bad")
        self.summary.style().unpolish(self.summary)
        self.summary.style().polish(self.summary)
        self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(balanced)

    def values(self) -> dict:
        lines, _ = self._read()
        d = self.date.date()
        return {
            "voucher_date": date(d.year(), d.month(), d.day()),
            "narration": self.narration.text().strip(),
            "lines": lines,
        }
    