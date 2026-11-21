"""Menu structure of the main window. Pure data: no widgets, no database (ADR-001 ui/ layer).

To add a form: add a NavItem here, then register its screen in screens.py.
To add a module (e.g. Broadcast later): add one Category and, if wanted, a sidebar entry.
`permission` is cosmetic (greys the button). Services re-check every permission.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class UserInfo:
    full_name: str
    user_id: str
    role: str


@dataclass(frozen=True)
class NavItem:
    key: str
    title: str
    glyph: str
    permission: str | None = None


@dataclass(frozen=True)
class Category:
    key: str
    title: str
    glyph: str
    color: str
    items: tuple[NavItem, ...]


@dataclass(frozen=True)
class SidebarEntry:
    key: str
    title: str
    glyph: str
    category_keys: tuple[str, ...] = ()   # empty = plain button (Home, Exit)


CATEGORIES: tuple[Category, ...] = (
    Category("master", "Master Data", "👥", "#1E6FE0", (
        NavItem("accounts",  "Accounts",  "🗄️", "account.view"),
        NavItem("employees", "Employees", "👤", "staff.view"),
        NavItem("customers", "Customers", "🧑‍💼", "customer.view"),
        NavItem("suppliers", "Suppliers", "🚚", "supplier.view"),
    )),
    Category("transactions", "Transactions", "🔁", "#2EA043", (
        NavItem("payment", "Payment", "💸", "voucher.view"),
        NavItem("receipt", "Receipt", "🧾", "voucher.view"),
        NavItem("journal", "Journal", "📒", "voucher.view"),
        NavItem("sales",   "Sales",   "📈", "sales.view"),
    )),
    Category("reports", "Financial Reports", "📄", "#7B3FC4", (
        NavItem("ledger",        "Ledger",        "📘", "report.view"),
        NavItem("trial_balance", "Trial Balance", "⚖️", "report.view"),
        NavItem("pnl",           "P&L Statement", "📑", "report.view"),
        NavItem("balance_sheet", "Balance Sheet", "📊", "report.view"),
    )),
    Category("statements", "Statements & Reconcile", "🗒️", "#F28C1B", (
        NavItem("statements", "Statements", "📃", "report.view"),
        NavItem("reconcile",  "Reconcile",  "✅", "report.view"),
    )),
    Category("payroll", "Attendance & Payroll", "🗓️", "#139BAA", (
        NavItem("attendance",     "Attendance",     "📅", "attendance.view"),
        NavItem("payroll",        "Payroll",        "💵", "payroll.view"),
        NavItem("salary_reports", "Salary Reports", "🧮", "payroll.view"),
    )),
    Category("settings", "Settings", "⚙️", "#4A5F82", (
        NavItem("users_roles",     "Users & Roles",   "🔐", "user.manage"),
        NavItem("system_settings", "System Settings", "🛠️", "settings.manage"),
        NavItem("company_profile", "Company Profile", "🏢", "settings.manage"),
    )),
    Category("backup", "Backup & Restore", "💾", "#D6303B", (
        NavItem("backup_db",  "Backup Database",  "💽", "backup.run"),
        NavItem("restore_db", "Restore Database", "♻️", "backup.run"),
    )),
    Category("exit", "Exit", "⏻", "#E3242B", (
        NavItem("exit", "Close Application", "⏻"),
    )),
)

SIDEBAR: tuple[SidebarEntry, ...] = (
    SidebarEntry("home",         "Home",               "🏠"),
    SidebarEntry("side_master",  "Master Data",        "🗄️", ("master",)),
    SidebarEntry("side_trans",   "Transactions",       "🔁", ("transactions",)),
    SidebarEntry("side_reports", "Reports",            "📊", ("reports", "statements")),
    SidebarEntry("side_payroll", "Attendance & Payroll", "🗓️", ("payroll",)),
    SidebarEntry("side_settings", "Settings",          "⚙️", ("settings",)),
    SidebarEntry("side_backup",  "Backup & Restore",   "💾", ("backup",)),
    SidebarEntry("exit",         "Exit",               "⏻"),
)

CATEGORY_BY_KEY = {c.key: c for c in CATEGORIES}
ITEM_BY_KEY = {i.key: i for c in CATEGORIES for i in c.items}
