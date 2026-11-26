import os
from datetime import date
from decimal import Decimal
from types import SimpleNamespace

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from src.app.application.dto import (
    VoucherDetail,
    VoucherLineRow,
    VoucherRow,
)
from src.app.ui.voucher_dialog import VoucherDialog


def test_searchable_account_input_and_draft_edit_preserve_description():
    app = QApplication.instance() or QApplication([])
    accounts = [
        SimpleNamespace(id=1, code="5400000005", name="Salaries"),
        SimpleNamespace(id=2, code="1101010001", name="Petty Cash"),
    ]
    initial = VoucherDetail(
        header=VoucherRow(
            id=3,
            voucher_no="V-2026-000001",
            voucher_date=date(2026, 11, 25),
            narration="November payroll",
            status="Draft",
            debit=Decimal("100.00"),
            credit=Decimal("100.00"),
            party_name="Payroll",
            cheque_no="CHQ-1",
            cheque_date=date(2026, 11, 25),
        ),
        lines=[
            VoucherLineRow(
                account_id=1,
                account_code="5400000005",
                account_name="Salaries",
                debit=Decimal("100.00"),
                credit=Decimal("0.00"),
                description="November salary",
            ),
            VoucherLineRow(
                account_id=2,
                account_code="1101010001",
                account_name="Petty Cash",
                debit=Decimal("0.00"),
                credit=Decimal("100.00"),
                description="Cash payment",
            ),
        ],
    )

    dialog = VoucherDialog(accounts, voucher=initial)
    try:
        combo = dialog.table.cellWidget(0, 0)
        assert combo.isEditable()
        assert combo.itemText(1) == "5400000005 | Salaries"
        assert combo.completer().filterMode().name == "MatchContains"

        payload = dialog.values()
        assert payload["party_name"] == "Payroll"
        assert payload["cheque_no"] == "CHQ-1"
        assert payload["cheque_date"] == date(2026, 11, 25)
        assert payload["lines"][0]["description"] == "November salary"
        assert payload["lines"][1]["description"] == "Cash payment"
    finally:
        dialog.close()
        app.processEvents()


def test_new_voucher_defaults_to_journal_and_captures_reference():
    app = QApplication.instance() or QApplication([])
    accounts = [SimpleNamespace(id=1, code="1000", name="Cash")]
    dialog = VoucherDialog(accounts)
    try:
        assert dialog.voucher_type.currentText() == "Journal"
        dialog.voucher_type.setCurrentText("Purchase")
        dialog.reference_no.setText("SUP-INV-7")
        assert dialog.values()["voucher_type"] == "Purchase"
        assert dialog.values()["reference_no"] == "SUP-INV-7"
    finally:
        dialog.close()
        app.processEvents()
