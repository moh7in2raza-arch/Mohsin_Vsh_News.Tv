from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

from src.app.domain.accounting.chart import ACCOUNT_TYPES
from src.app.domain.security import permissions as P
from src.app.ui.support import call_service, fill_table, print_table

_HEADERS = ["Code", "Name", "Type", "Normal balance"]


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
        btn_print = QPushButton("Print")
        btn_print.clicked.connect(self._print)

        bar = QHBoxLayout()
        bar.addStretch()
        bar.addWidget(self.btn_new)
        bar.addWidget(btn_print)

        self.table = QTableWidget()
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

        layout = QVBoxLayout(self)
        layout.addLayout(bar)
        layout.addWidget(self.table)

    def _data(self):
        return [(a.code, a.name, a.type, a.normal_balance) for a in self._rows]

    def refresh(self) -> None:
        ok, rows = call_service(self, self._accounts.list_accounts, self._session, False)
        self._rows = rows if ok else []
        fill_table(self.table, _HEADERS, self._data())

    def _new(self) -> None:
        dialog = _AccountDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            ok, _ = call_service(self, self._accounts.create_account, self._session,
                                 dialog.code.text(), dialog.name.text(), dialog.type.currentText())
            if ok:
                self.refresh()

    def _print(self) -> None:
        print_table(self, "Chart of accounts", _HEADERS, self._data())
