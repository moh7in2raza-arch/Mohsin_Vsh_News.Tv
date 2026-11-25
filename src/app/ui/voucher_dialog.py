from datetime import date
from decimal import Decimal, InvalidOperation

from PySide6.QtCore import QDate, QRegularExpression, Qt
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QComboBox,
    QCheckBox,
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
    QTableWidgetItem,
    QVBoxLayout,
)

from src.app.ui.report_headings import VOUCHER_HEADINGS

_ZERO = Decimal("0")


def _amount(edit: QLineEdit) -> Decimal:
    try:
        return Decimal(edit.text().strip() or "0")
    except InvalidOperation:
        return _ZERO


class VoucherDialog(QDialog):
    """Voucher entry form. Returns plain values; the service validates them."""

    def __init__(self, accounts, parent=None, voucher=None):
        super().__init__(parent)
        self.setWindowTitle("Edit draft voucher" if voucher else "New voucher")
        self.resize(760, 480)
        self._accounts = accounts

        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.date.setDisplayFormat("dd-MMM-yyyy")
        self.narration = QLineEdit()
        self.party_name = QLineEdit()
        self.cheque_no = QLineEdit()
        self.cheque_date_enabled = QCheckBox("Enter cheque date")
        self.cheque_date = QDateEdit(QDate.currentDate())
        self.cheque_date.setCalendarPopup(True)
        self.cheque_date.setDisplayFormat("dd-MMM-yyyy")
        self.cheque_date.setEnabled(False)
        self.cheque_date_enabled.toggled.connect(self.cheque_date.setEnabled)
        form = QFormLayout()
        form.addRow("Date", self.date)
        form.addRow("Payee", self.party_name)
        form.addRow("Narration", self.narration)
        form.addRow("Cheque No", self.cheque_no)
        form.addRow("Cheque Date", self.cheque_date_enabled)
        form.addRow("", self.cheque_date)

        self.table = QTableWidget(0, len(VOUCHER_HEADINGS))
        self.table.setHorizontalHeaderLabels(list(VOUCHER_HEADINGS))
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
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

        if voucher is None:
            self.add_row()
            self.add_row()
        else:
            header = voucher.header
            self.date.setDate(QDate(
                header.voucher_date.year,
                header.voucher_date.month,
                header.voucher_date.day,
            ))
            self.party_name.setText(header.party_name)
            self.narration.setText(header.narration or "")
            self.cheque_no.setText(header.cheque_no)
            if header.cheque_date is not None:
                self.cheque_date_enabled.setChecked(True)
                self.cheque_date.setDate(QDate(
                    header.cheque_date.year,
                    header.cheque_date.month,
                    header.cheque_date.day,
                ))
            for line in voucher.lines:
                self.add_row(line)
            self.add_row()

    def add_row(self, line=None) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)
        combo = QComboBox()
        combo.setEditable(True)
        combo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        combo.addItem("", None)
        account_names = {}
        for a in self._accounts:
            combo.addItem(f"{a.code} | {a.name}", a.id)
            account_names[a.id] = str(a.name)
        completer = combo.completer()
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.table.setCellWidget(row, 0, combo)
        account_title = QTableWidgetItem()
        account_title.setFlags(account_title.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.table.setItem(row, 1, account_title)
        self.table.setItem(row, 2, QTableWidgetItem())
        combo.currentIndexChanged.connect(
            lambda index, box=combo, title=account_title, names=account_names:
                title.setText(names.get(box.itemData(index), ""))
        )
        validator = QRegularExpressionValidator(QRegularExpression(r"^\d{0,12}(\.\d{0,2})?$"))
        for col in (3, 4):
            edit = QLineEdit()
            edit.setValidator(validator)
            edit.setPlaceholderText("0.00")
            edit.textChanged.connect(self._refresh)
            self.table.setCellWidget(row, col, edit)
        if line is not None:
            combo.setCurrentIndex(combo.findData(line.account_id))
            self.table.item(row, 2).setText(line.description)
            self.table.cellWidget(row, 3).setText(str(line.debit))
            self.table.cellWidget(row, 4).setText(str(line.credit))
        self._refresh()

    def _remove_row(self) -> None:
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
            self._refresh()

    def _read(self):
        lines, ok = [], True
        for r in range(self.table.rowCount()):
            account_combo = self.table.cellWidget(r, 0)
            account_id = account_combo.currentData()
            debit = _amount(self.table.cellWidget(r, 3))
            credit = _amount(self.table.cellWidget(r, 4))
            if debit == 0 and credit == 0:
                continue
            if account_id is None or (debit > 0) == (credit > 0):
                ok = False
            lines.append(
                {
                    "account_id": account_id,
                    "debit": debit,
                    "credit": credit,
                    "description": self.table.item(r, 2).text().strip(),
                }
            )
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
            "party_name": self.party_name.text().strip(),
            "narration": self.narration.text().strip(),
            "cheque_no": self.cheque_no.text().strip(),
            "cheque_date": (
                date(
                    self.cheque_date.date().year(),
                    self.cheque_date.date().month(),
                    self.cheque_date.date().day(),
                )
                if self.cheque_date_enabled.isChecked()
                else None
            ),
            "lines": lines,
        }
    