"""Maps a menu key to the screen that opens. Keys with no entry open a 'not built yet' page.

Screens are imported lazily so one broken or unfinished screen cannot stop the app starting.
Screens talk to application services only, never to SQL (ADR-001).
"""
from __future__ import annotations

from typing import Callable

from PySide6.QtWidgets import QWidget


def _employees() -> QWidget:
    from src.app.ui.employees_view import EmployeesView      # adjust to your class name
    return EmployeesView()


def _vouchers() -> QWidget:
    from src.app.ui.voucher_view import VoucherView          # adjust to your class name
    return VoucherView()


SCREENS: dict[str, Callable[[], QWidget]] = {
    "employees": _employees,
    "payment": _vouchers,
    # "receipt": ..., "journal": ..., add one line per finished screen
}
