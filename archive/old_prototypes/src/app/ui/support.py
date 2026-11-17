"""Shared UI helpers: filling tables, printing tables with repeating headers,
and calling services with friendly error messages."""
import html
import logging
from datetime import date, datetime
from decimal import Decimal

from PySide6.QtCore import Qt
from PySide6.QtGui import QPageSize, QTextDocument
from PySide6.QtPrintSupport import QPrintDialog, QPrinter
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
)

from src.app.application.services.account_service import AccountError
from src.app.application.services.permission_service import PermissionDenied
from src.app.application.services.posting_service import PostingError
from src.app.application.services.voucher_service import VoucherError

log = logging.getLogger(__name__)
USER_ERRORS = (VoucherError, PermissionDenied, PostingError, AccountError)
_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


def fmt(value) -> str:
    if value is None:
        return ""
    if isinstance(value, Decimal):
        return f"{value:,.2f}"
    if isinstance(value, (date, datetime)):
        return value.strftime("%d-%b-%Y")
    return str(value)


def fill_table(table: QTableWidget, headers, rows, right_cols=()) -> None:
    table.clear()
    table.setColumnCount(len(headers))
    table.setHorizontalHeaderLabels(list(headers))
    table.setRowCount(len(rows))
    for r, row in enumerate(rows):
        for c, value in enumerate(row):
            item = QTableWidgetItem(fmt(value))
            if c in right_cols or isinstance(value, Decimal):
                item.setTextAlignment(_RIGHT)
            table.setItem(r, c, item)
    table.resizeColumnsToContents()
    table.horizontalHeader().setStretchLastSection(True)


def _html(title, subtitle, headers, rows, right_cols):
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = ""
    for row in rows:
        cells = ""
        for c, value in enumerate(row):
            align = ' align="right"' if (c in right_cols or isinstance(value, Decimal)) else ""
            cells += f"<td{align}>{html.escape(fmt(value))}</td>"
        body += f"<tr>{cells}</tr>"
    return (
        f"<h2>{html.escape(title)}</h2><p>{html.escape(subtitle)}</p>"
        '<table border="1" cellspacing="0" cellpadding="4" width="100%">'
        f"<thead><tr bgcolor='#e8edf3'>{head}</tr></thead><tbody>{body}</tbody></table>"
    )


def print_table(parent, title, headers, rows, subtitle="", right_cols=(), to_pdf=False) -> None:
    """Print (or save as PDF) a table; the header row repeats on every page."""
    printer = QPrinter(QPrinter.PrinterMode.HighResolution)
    printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    if to_pdf:
        path, _ = QFileDialog.getSaveFileName(parent, "Save PDF", f"{title}.pdf", "PDF (*.pdf)")
        if not path:
            return
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(path)
    elif QPrintDialog(printer, parent).exec() != QDialog.DialogCode.Accepted:
        return
    doc = QTextDocument()
    doc.setHtml(_html(title, subtitle, headers, rows, right_cols))
    doc.print_(printer)


def call_service(parent, fn, *args, **kwargs):
    """Run a service call. Returns (True, result) or (False, None) after
    showing a message; business errors are shown, unexpected ones logged."""
    try:
        return True, fn(*args, **kwargs)
    except USER_ERRORS as ex:
        QMessageBox.warning(parent, "Not allowed", str(ex))
    except Exception:
        log.exception("Unexpected error in %s", getattr(fn, "__name__", fn))
        QMessageBox.critical(parent, "Error",
                             "Something went wrong. Details were written to the log file.")
    return False, None