from PySide6.QtCore import QTemporaryFile, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from src.app.domain.security import permissions as P
from src.app.domain.workflow import TRANSITIONS, can_transition
from src.app.ui.report_headings import VOUCHER_HEADINGS
from src.app.ui.support import (
    call_service,
    create_export_menu,
    export_table,
    fill_table,
)
from src.app.ui.voucher_dialog import VoucherDialog
from src.app.application.services.voucher_pdf_service import (
    VoucherPdfError,
    VoucherPdfService,
)

_HEADERS = VOUCHER_HEADINGS


def _table() -> QTableWidget:
    t = QTableWidget()
    t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    t.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    t.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    return t


class VouchersView(QWidget):

    def __init__(self, services, session):
        super().__init__()
        self._vouchers = services.vouchers
        self._accounts = services.accounts
        self._company = services.company
        self._session = session
        self._rows = []
        self._voucher_pdf = VoucherPdfService()
        self._selected_voucher_detail = None
        self._preview_file = None

        self.status_filter = QComboBox()
        self.status_filter.addItems(["All", *TRANSITIONS])
        self.status_filter.currentIndexChanged.connect(self.refresh)

        self.btn_new = self._button("New voucher", self._new, primary=True)
        self.btn_edit = self._button("Edit draft", self._edit_selected)
        self.btn_submit = self._button("Submit", lambda: self._move("submit"))
        self.btn_approve = self._button("Approve", lambda: self._move("approve"))
        self.btn_back = self._button("Return to draft", lambda: self._move("return_to_draft"))
        self.btn_post = self._button("Post", lambda: self._move("post", confirm=True))
        self.btn_reverse = self._button("Reverse", lambda: self._move("reverse", confirm=True))
        self.btn_print = QToolButton()
        self.btn_print.setText("Export voucher")
        self.btn_print.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.btn_print.setMenu(create_export_menu(self.btn_print, self._export))

        bar = QHBoxLayout()
        bar.addWidget(QLabel("Status"))
        bar.addWidget(self.status_filter)
        bar.addStretch()
        for b in (self.btn_new, self.btn_edit, self.btn_submit, self.btn_approve, self.btn_back,
                  self.btn_post, self.btn_reverse, self.btn_print):
            bar.addWidget(b)

        self.table = QListWidget()
        self.table.currentRowChanged.connect(self._on_select)
        self.detail = _table()
        self._selected_detail = []
        fill_table(self.detail, _HEADERS, [])

        layout = QVBoxLayout(self)
        layout.addLayout(bar)
        layout.addWidget(self.table, 1)
        layout.addWidget(self.detail, 2)
        self._update_buttons()

    def _button(self, text, handler, primary=False):
        b = QPushButton(text)
        if primary:
            b.setObjectName("primary")
        b.clicked.connect(handler)
        return b

    def _selected(self):
        r = self.table.currentRow()
        return self._rows[r] if 0 <= r < len(self._rows) else None

    def refresh(self) -> None:
        status = self.status_filter.currentText()
        ok, rows = call_service(self, self._vouchers.list_vouchers, self._session,
                                None if status == "All" else status)
        self._rows = rows if ok else []
        self.table.blockSignals(True)
        self.table.clear()
        for voucher in self._rows:
            self.table.addItem(
                f"{voucher.voucher_no} | {voucher.voucher_date:%d-%b-%Y} | "
                f"{voucher.narration or ''} | {voucher.status}"
            )
        self.table.setCurrentRow(-1)
        self.table.blockSignals(False)
        self.detail.clear()
        self.detail.setRowCount(0)
        self._selected_detail = []
        self._selected_voucher_detail = None
        if self._rows:
            self.table.setCurrentRow(0)
        else:
            self._update_buttons()

    def _on_select(self) -> None:
        self._update_buttons()
        v = self._selected()
        if v is None:
            self._selected_detail = []
            self._selected_voucher_detail = None
            self.detail.clear()
            self.detail.setRowCount(0)
            return
        ok, detail = call_service(self, self._vouchers.get_voucher, self._session, v.id)
        if ok:
            self._selected_voucher_detail = detail
            self._selected_detail = [
                (line.account_code, line.account_name, line.description,
                 line.debit, line.credit)
                for line in detail.lines
            ]
            fill_table(self.detail, _HEADERS, self._selected_detail, right_cols=(3, 4))
        else:
            self._selected_detail = []
            self._selected_voucher_detail = None
            self.detail.clear()
            self.detail.setRowCount(0)
        self._update_buttons()

    def _update_buttons(self) -> None:
        s = self._session
        v = self._selected()
        status = v.status if v else None

        def allowed(target, perm):
            return bool(status) and s.has(perm) and can_transition(status, target)

        self.btn_new.setEnabled(s.has(P.VOUCHER_CREATE))
        self.btn_edit.setEnabled(
            bool(v and status == "Draft" and s.has(P.VOUCHER_EDIT_DRAFT))
        )
        self.btn_submit.setEnabled(allowed("Submitted", P.VOUCHER_SUBMIT))
        self.btn_approve.setEnabled(allowed("Approved", P.VOUCHER_APPROVE))
        self.btn_back.setEnabled(allowed("Draft", P.VOUCHER_APPROVE))
        self.btn_post.setEnabled(allowed("Posted", P.VOUCHER_POST))
        self.btn_reverse.setEnabled(allowed("Reversed", P.VOUCHER_REVERSE))
        self.btn_print.setEnabled(bool(self._selected_detail))

    def _new(self) -> None:
        ok, accounts = call_service(self, self._accounts.list_accounts, self._session)
        if not ok:
            return
        if not accounts:
            QMessageBox.information(self, "No accounts",
                                    "At least two active PostgreSQL account heads are required.")
            return
        dialog = VoucherDialog(accounts, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            ok, _ = call_service(self, self._vouchers.create_draft, self._session,
                                 **dialog.values())
            if ok:
                self.refresh()

    def _edit_selected(self) -> None:
        selected = self._selected()
        if selected is None:
            return
        ok, accounts = call_service(
            self, self._accounts.list_accounts, self._session
        )
        if not ok or not accounts:
            if ok:
                QMessageBox.information(
                    self,
                    "No accounts",
                    "At least two active PostgreSQL account heads are required.",
                )
            return
        ok, detail = call_service(
            self, self._vouchers.get_voucher, self._session, selected.id
        )
        if not ok:
            return
        dialog = VoucherDialog(accounts, self, voucher=detail)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            ok, _ = call_service(
                self,
                self._vouchers.update_draft,
                self._session,
                selected.id,
                **dialog.values(),
            )
            if ok:
                self.refresh()

    def _move(self, action: str, confirm: bool = False) -> None:
        v = self._selected()
        if v is None:
            return
        if confirm and QMessageBox.question(
            self, "Confirm", f"{action.capitalize()} voucher {v.voucher_no}?"
        ) != QMessageBox.StandardButton.Yes:
            return
        ok, _ = call_service(self, getattr(self._vouchers, action), self._session, v.id)
        if ok:
            self.refresh()

    def _export(self, file_format: str) -> None:
        selected = self._selected()
        if file_format in ("pdf", "print"):
            if selected is None:
                QMessageBox.information(self, "Voucher", "Select a voucher to export.")
                return
            preview_file = None
            if file_format == "pdf":
                path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Save payment voucher",
                    f"{selected.voucher_no}.pdf",
                    "PDF (*.pdf)",
                )
                if not path:
                    return
                if not path.lower().endswith(".pdf"):
                    path += ".pdf"
            else:
                preview_file = QTemporaryFile("VSH-voucher-XXXXXX.pdf", self)
                if not preview_file.open():
                    QMessageBox.critical(
                        self, "Voucher PDF", "Could not create a temporary PDF for preview."
                    )
                    return
                path = preview_file.fileName()
                preview_file.close()
            ok, detail = call_service(
                self, self._vouchers.get_voucher, self._session, selected.id
            )
            if not ok:
                if preview_file is not None:
                    preview_file.remove()
                return
            try:
                self._voucher_pdf.generate(
                    detail,
                    self._company.get_profile(self._session),
                    path,
                )
            except VoucherPdfError as ex:
                if preview_file is not None:
                    preview_file.remove()
                QMessageBox.critical(self, "Voucher PDF", str(ex))
                return
            if preview_file is not None:
                if not QDesktopServices.openUrl(QUrl.fromLocalFile(path)):
                    preview_file.remove()
                    QMessageBox.critical(
                        self, "Voucher PDF", "Could not open the voucher PDF preview."
                    )
                    return
                if self._preview_file is not None:
                    self._preview_file.remove()
                self._preview_file = preview_file
                return
            QMessageBox.information(
                self, "Saved", f"Payment voucher saved to:\n{path}"
            )
            return
        title = f"Voucher {selected.voucher_no}" if selected is not None else "Voucher"
        export_table(
            self, title, _HEADERS, self._selected_detail, file_format,
            subtitle=selected.narration or "" if selected is not None else "",
            right_cols=(3, 4),
        )
