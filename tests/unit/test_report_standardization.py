import os
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QCoreApplication, QEvent
from PySide6.QtWidgets import QApplication
import pytest

from src.app.application.session import Session
from src.app.domain.security import permissions as P
from src.app.ui.accounts_view import AccountsView
from src.app.ui.admin_views import UsersRolesView
from src.app.ui.employees_view import EmployeesView
from src.app.ui.report_headings import (
    ACCOUNTS_HEADINGS,
    BANK_RECONCILIATION_HEADINGS,
    BALANCE_SHEET_ASSET_HEADINGS,
    BALANCE_SHEET_LIABILITY_HEADINGS,
    BALANCE_SHEET_SUBGROUPS,
    EMPLOYEES_HEADINGS,
    GENERAL_LEDGER_HEADINGS,
    TRIAL_BALANCE_HEADINGS,
    USERS_HEADINGS,
    VOUCHER_HEADINGS,
)
from src.app.ui.reports_view import ReportsView
from src.app.ui.support import (
    _html,
    export_table,
    render_markdown_table,
    render_text_table,
)
from src.app.ui.users_view import UsersView
from src.app.ui.voucher_dialog import VoucherDialog
from src.app.ui.vouchers_view import VouchersView


def _column_headers(table):
    return tuple(
        table.horizontalHeaderItem(column).text()
        for column in range(table.columnCount())
    )


def test_approved_heading_sets_and_text_formats():
    assert VOUCHER_HEADINGS == (
        "AcCode", "Account Head Title", "Particulars", "Debit", "Credit",
    )
    assert TRIAL_BALANCE_HEADINGS == (
        "AcCode", "Account Head Title", "Opening Bal", "Total Debit",
        "Total Credit", "Closing Bal",
    )
    assert GENERAL_LEDGER_HEADINGS == (
        "Date", "Voucher No", "Src", "Particulars / Contra", "Debit",
        "Credit", "Running Bal",
    )
    assert BANK_RECONCILIATION_HEADINGS == (
        "Date", "PV/RV No", "Party / Account", "Chq No", "Chq Date", "Amount",
    )
    assert USERS_HEADINGS == (
        "UserName", "Designation", "Add/Edit Rights", "Delete Rights",
        "Reports Access", "Backup Restore",
    )
    assert EMPLOYEES_HEADINGS == (
        "Employee ID", "Employee Name", "Department", "Designation", "CNIC",
        "Phone No.", "Joining Date", "Salary", "Status",
    )
    assert ACCOUNTS_HEADINGS == (
        "AcCode", "AcName", "TypeCode", "Opening Balance", "Current Balance",
        "Active",
    )
    assert BALANCE_SHEET_ASSET_HEADINGS == ("ASSETS", "Amount (PKR)")
    assert BALANCE_SHEET_LIABILITY_HEADINGS == (
        "LIABILITIES & CAPITAL", "Amount (PKR)",
    )
    assert BALANCE_SHEET_SUBGROUPS == (
        "NON-CURRENT / FIXED ASSETS",
        "CURRENT ASSETS (CASH & BANK)",
        "CAPITAL & RESERVES",
        "NON-CURRENT / CURRENT LIABILITIES",
    )

    text = render_text_table(VOUCHER_HEADINGS, [("100", "Cash", "Sale", 25, 25)])
    markdown = render_markdown_table(VOUCHER_HEADINGS, [("100", "Cash", "A | B", 25, 25)])
    assert text.splitlines()[0] == "\t".join(VOUCHER_HEADINGS)
    assert markdown.splitlines()[0] == "| " + " | ".join(VOUCHER_HEADINGS) + " |"
    assert r"A \| B" in markdown


@pytest.mark.parametrize(
    ("file_format", "expected_header"),
    [
        ("txt", "\t".join(VOUCHER_HEADINGS)),
        ("md", "| " + " | ".join(VOUCHER_HEADINGS) + " |"),
    ],
)
def test_file_exports_preserve_approved_headings(tmp_path, file_format, expected_header):
    extension = "md" if file_format == "md" else "txt"
    output = tmp_path / f"voucher.{extension}"
    with (
        patch(
            "src.app.ui.support.QFileDialog.getSaveFileName",
            return_value=(str(output), ""),
        ),
        patch("src.app.ui.support.QMessageBox.information"),
    ):
        export_table(None, "Voucher", VOUCHER_HEADINGS, [], file_format)

    assert output.read_text(encoding="utf-8").splitlines()[0] == expected_header


def test_print_html_preserves_approved_headings():
    rendered = _html("Voucher", "", VOUCHER_HEADINGS, [], ())
    assert "".join(f"<th>{heading}</th>" for heading in VOUCHER_HEADINGS) in rendered


def test_active_grids_use_approved_headings():
    app = QApplication.instance() or QApplication([])
    session = Session(1, "report-test", frozenset({
        P.ACCOUNT_VIEW, P.VOUCHER_VIEW, P.VOUCHER_CREATE, P.REPORT_VIEW,
    }))

    class FakeService:
        def list_accounts(self, *args):
            return []

        def list_vouchers(self, *args):
            return []

        def list_employees(self):
            return []

        def get_all_users(self):
            return []

    services = SimpleNamespace(
        accounts=FakeService(),
        vouchers=FakeService(),
        reports=FakeService(),
        employees=FakeService(),
        auth=FakeService(),
    )
    widgets = [
        AccountsView(services, session),
        ReportsView(services, session),
        VouchersView(services, session),
        VoucherDialog([SimpleNamespace(id=1, code="100", name="Cash")]),
        UsersRolesView(services, session),
        UsersView(services.auth),
        EmployeesView(services, session),
    ]
    try:
        assert _column_headers(widgets[0].table) == ACCOUNTS_HEADINGS
        assert _column_headers(widgets[1].tb_table) == TRIAL_BALANCE_HEADINGS
        assert _column_headers(widgets[1].lg_table) == GENERAL_LEDGER_HEADINGS
        assert _column_headers(widgets[2].detail) == VOUCHER_HEADINGS
        assert _column_headers(widgets[3].table) == VOUCHER_HEADINGS
        assert _column_headers(widgets[4].table) == USERS_HEADINGS
        assert _column_headers(widgets[5].table) == USERS_HEADINGS
        assert _column_headers(widgets[6].table) == EMPLOYEES_HEADINGS
        widgets[1]._tb_rows = [
            SimpleNamespace(
                code="100",
                name="Cash",
                debit=Decimal("30"),
                credit=Decimal("0"),
                total_debit=Decimal("50"),
                total_credit=Decimal("20"),
            )
        ]
        assert widgets[1]._tb_data() == [
            ("100", "Cash", "", Decimal("50"), Decimal("20"), Decimal("30")),
            ("", "TOTAL", "", Decimal("50"), Decimal("20"), Decimal("30")),
        ]
    finally:
        for widget in widgets:
            widget.close()
            widget.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        app.processEvents()
