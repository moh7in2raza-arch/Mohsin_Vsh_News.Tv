"""Shared UI helpers: filling tables, printing tables with official VSH logo header,
and calling services with friendly error messages."""
import base64
import html
import logging
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

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

from src.app.application.dto import CompanyProfile
from src.app.application.services.account_service import AccountError
from src.app.application.services.permission_service import PermissionDenied
from src.app.application.services.posting_service import PostingError
from src.app.application.services.voucher_service import VoucherError

log = logging.getLogger(__name__)
USER_ERRORS = (VoucherError, PermissionDenied, PostingError, AccountError)
_RIGHT = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter


def active_company_profile(services) -> CompanyProfile:
    company_service = getattr(services, "company", None)
    if company_service is None:
        raise RuntimeError("Company profile service is not configured")
    return company_service.get_profile()


def _logo_data_uri() -> str:
    """Resolve official VSH NEWS logo from assets/ (supports source & PyInstaller bundle)."""
    bases = []
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bases.append(Path(sys._MEIPASS))
    bases.extend([Path(__file__).resolve().parents[3], Path.cwd()])
    for base in bases:
        for rel in ("assets/vsh_logo.png.png", "assets/vsh_logo.png", "vsh_logo.png.png"):
            p = base / rel
            if p.exists():
                encoded = base64.b64encode(p.read_bytes()).decode("ascii")
                return f"data:image/png;base64,{encoded}"
    return ""


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
    logo_uri = _logo_data_uri()
    logo_cell = (
        f'<td width="76"><img src="{logo_uri}" width="64" height="64" /></td>'
        if logo_uri else ""
    )
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = ""
    for row in rows:
        cells = ""
        for c, value in enumerate(row):
            align = ' align="right"' if (c in right_cols or isinstance(value, Decimal)) else ""
            cells += f"<td{align}>{html.escape(fmt(value))}</td>"
        body += f"<tr>{cells}</tr>"
    return (
        '<table width="100%" cellspacing="0" cellpadding="6" '
        'style="border-bottom:2px solid #DC2626; margin-bottom:10px;">'
        f"<tr>{logo_cell}"
        "<td>"
        '<div style="font-size:17pt; font-weight:bold; color:#991B1B;">VSH NEWS TV</div>'
        '<div style="font-size:10pt; color:#334155;">Visionary Baluchistan Media Corporation (Pvt) Ltd</div>'
        f'<div style="font-size:13pt; font-weight:bold; color:#0F172A; margin-top:4px;">{html.escape(title)}</div>'
        f'<div style="font-size:9pt; color:#475569;">{html.escape(subtitle)}</div>'
        "</td></tr></table>"
        '<table border="1" cellspacing="0" cellpadding="4" width="100%">'
        f"<thead><tr bgcolor='#fee2e2'>{head}</tr></thead><tbody>{body}</tbody></table>"
    )


def print_table(parent, title, headers, rows, subtitle="", right_cols=(), to_pdf=False) -> None:
    """Print (or save as PDF) a table with official VSH NEWS logo header."""
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
