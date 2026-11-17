from datetime import date

from PySide6.QtCore import QDate
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDateEdit,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from src.app.ui.support import call_service, fill_table, print_table

_TB_HEADERS = ["Code", "Account", "Debit", "Credit"]
_LG_HEADERS = ["Date", "Voucher", "Narration", "Debit", "Credit", "Balance"]


def _date_edit(qdate: QDate) -> QDateEdit:
    e = QDateEdit(qdate)
    e.setCalendarPopup(True)
    e.setDisplayFormat("dd-MMM-yyyy")
    return e


def _py(e: QDateEdit) -> date:
    d = e.date()
    return date(d.year(), d.month(), d.day())


def _table() -> QTableWidget:
    t = QTableWidget()
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    return t


def _balance_text(value) -> str:
    return f"{abs(value):,.2f} {'Dr' if value >= 0 else 'Cr'}"


class ReportsView(QWidget):

    def __init__(self, services, session):
        super().__init__()
        self._reports = services.reports
        self._accounts = services.accounts
        self._session = session
        self._tb_rows = []
        self._lg_rows = []

        tabs = QTabWidget()
        tabs.addTab(self._build_trial_balance(), "Trial balance")
        tabs.addTab(self._build_ledger(), "Account ledger")
        layout = QVBoxLayout(self)
        layout.addWidget(tabs)

    # ---- trial balance ----
    def _build_trial_balance(self) -> QWidget:
        self.tb_date = _date_edit(QDate.currentDate())
        run = QPushButton("Run")
        run.setObjectName("primary")
        run.clicked.connect(self._run_tb)
        pdf = QPushButton("PDF")
        pdf.clicked.connect(lambda: self._print_tb(True))
        prn = QPushButton("Print")
        prn.clicked.connect(lambda: self._print_tb(False))
        bar = QHBoxLayout()
        bar.addWidget(QLabel("As of"))
        bar.addWidget(self.tb_date)
        bar.addWidget(run)
        bar.addStretch()
        bar.addWidget(pdf)
        bar.addWidget(prn)
        self.tb_table = _table()
        self.tb_total = QLabel()
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addLayout(bar)
        lay.addWidget(self.tb_table)
        lay.addWidget(self.tb_total)
        return w

    def _tb_data(self):
        data = [(r.code, r.name, r.debit, r.credit) for r in self._tb_rows]
        if self._tb_rows:
            data.append(("", "TOTAL", sum(r.debit for r in self._tb_rows),
                         sum(r.credit for r in self._tb_rows)))
        return data

    def _run_tb(self) -> None:
        ok, rows = call_service(self, self._reports.trial_balance, self._session,
                                _py(self.tb_date))
        if ok:
            self._tb_rows = rows
            data = self._tb_data()
            fill_table(self.tb_table, _TB_HEADERS, data)
            if rows:
                d, c = data[-1][2], data[-1][3]
                self.tb_total.setText(f"Total debit {d:,.2f}   Total credit {c:,.2f}")
            else:
                self.tb_total.setText("No posted entries up to this date.")

    def _print_tb(self, to_pdf: bool) -> None:
        print_table(self, "Trial balance", _TB_HEADERS, self._tb_data(),
                    subtitle=f"As of {_py(self.tb_date):%d-%b-%Y}", right_cols=(2, 3),
                    to_pdf=to_pdf)

    # ---- ledger ----
    def _build_ledger(self) -> QWidget:
        self.lg_account = QComboBox()
        today = QDate.currentDate()
        self.lg_from = _date_edit(QDate(today.year(), 1, 1))
        self.lg_to = _date_edit(today)
        run = QPushButton("Run")
        run.setObjectName("primary")
        run.clicked.connect(self._run_ledger)
        pdf = QPushButton("PDF")
        pdf.clicked.connect(lambda: self._print_ledger(True))
        prn = QPushButton("Print")
        prn.clicked.connect(lambda: self._print_ledger(False))
        bar = QHBoxLayout()
        for widget in (QLabel("Account"), self.lg_account, QLabel("From"), self.lg_from,
                       QLabel("To"), self.lg_to, run):
            bar.addWidget(widget)
        bar.addStretch()
        bar.addWidget(pdf)
        bar.addWidget(prn)
        self.lg_table = _table()
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.addLayout(bar)
        lay.addWidget(self.lg_table)
        return w

    def _lg_data(self):
        return [(r.entry_date, r.voucher_no, r.narration, r.debit, r.credit,
                 _balance_text(r.balance)) for r in self._lg_rows]

    def _run_ledger(self) -> None:
        account_id = self.lg_account.currentData()
        if account_id is None:
            return
        ok, rows = call_service(self, self._reports.account_ledger, self._session,
                                account_id, _py(self.lg_from), _py(self.lg_to))
        if ok:
            self._lg_rows = rows
            fill_table(self.lg_table, _LG_HEADERS, self._lg_data(), right_cols=(5,))

    def _print_ledger(self, to_pdf: bool) -> None:
        sub = (f"{self.lg_account.currentText()}  |  "
               f"{_py(self.lg_from):%d-%b-%Y} to {_py(self.lg_to):%d-%b-%Y}")
        print_table(self, "Account ledger", _LG_HEADERS, self._lg_data(), subtitle=sub,
                    right_cols=(3, 4, 5), to_pdf=to_pdf)

    def refresh(self) -> None:
        ok, accounts = call_service(self, self._accounts.list_accounts, self._session)
        if ok:
            self.lg_account.clear()
            for a in accounts:
                self.lg_account.addItem(f"{a.code} - {a.name}", a.id)
