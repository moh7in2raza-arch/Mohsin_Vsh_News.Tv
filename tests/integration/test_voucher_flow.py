"""Runs the real services against PostgreSQL inside ONE outer transaction that
is rolled back at the end, so erp_office is left untouched.
Skipped automatically if the database is unreachable or 0006 is not applied."""
from datetime import date
from decimal import Decimal

import psycopg
import pytest

from src.app.application.services.account_service import AccountService
from src.app.application.services.permission_service import PermissionDenied
from src.app.application.services.report_service import ReportService
from src.app.application.services.voucher_service import VoucherError, VoucherService
from src.app.application.session import Session
from src.app.domain.security import permissions as P
from src.app.infrastructure.database.connection import get_connection
from src.app.infrastructure.database.unit_of_work import UnitOfWork


@pytest.fixture
def conn():
    try:
        c = get_connection()
    except Exception as ex:
        pytest.skip(f"database not reachable: {ex}")
    c.execute("SELECT 1")                      # open the outer transaction
    version = c.execute("SELECT COALESCE(MAX(version), 0) FROM schema_version").fetchone()[0]
    if version < 6:
        c.close()
        pytest.skip("run tools\\migrate.py first (0006 not applied)")
    yield c
    c.rollback()
    c.close()


@pytest.fixture
def env(conn):
    row = conn.execute("SELECT id FROM users ORDER BY id LIMIT 1").fetchone()
    if row is None:
        pytest.skip("no user in the database")
    factory = lambda: UnitOfWork(connection=conn)       # noqa: E731
    session = Session(row[0], "tester", frozenset(P.ALL))
    return conn, factory, session


def test_full_voucher_lifecycle(env):
    conn, factory, session = env
    accounts, vouchers, reports = (AccountService(factory), VoucherService(factory),
                                   ReportService(factory))
    cash = accounts.create_account(session, "T-1001", "Test cash", "Asset")
    sales = accounts.create_account(session, "T-4001", "Test sales", "Income")

    vid = vouchers.create_draft(session, date.today(), "test sale", [
        {"account_id": cash, "debit": "250.00", "credit": "0"},
        {"account_id": sales, "debit": "0", "credit": "250.00"},
    ])
    with pytest.raises(VoucherError):                      # cannot skip approval
        vouchers.post(session, vid)

    vouchers.submit(session, vid)
    vouchers.approve(session, vid)
    vouchers.post(session, vid)

    tb = {r.code: r for r in reports.trial_balance(session, date.today())}
    assert tb["T-1001"].debit == Decimal("250.00")
    assert tb["T-4001"].credit == Decimal("250.00")

    vouchers.reverse(session, vid)
    tb = {r.code: r for r in reports.trial_balance(session, date.today())}
    assert tb["T-1001"].debit == 0 and tb["T-4001"].credit == 0
    assert vouchers.get_voucher(session, vid).header.status == "Reversed"

    actions = [r[0] for r in conn.execute(
        "SELECT action FROM audit_log WHERE entity = 'voucher' AND entity_id = %s ORDER BY id",
        (vid,)).fetchall()]
    assert actions == ["voucher.create", "voucher.submit", "voucher.approve",
                       "voucher.post", "voucher.reverse"]


def test_ledger_is_append_only(env):
    conn, factory, session = env
    accounts, vouchers = AccountService(factory), VoucherService(factory)
    a = accounts.create_account(session, "T-1002", "Test A", "Asset")
    b = accounts.create_account(session, "T-4002", "Test B", "Income")
    vid = vouchers.create_draft(session, date.today(), "x", [
        {"account_id": a, "debit": "10", "credit": "0"},
        {"account_id": b, "debit": "0", "credit": "10"},
    ])
    vouchers.submit(session, vid)
    vouchers.approve(session, vid)
    vouchers.post(session, vid)
    with pytest.raises(psycopg.errors.RaiseException):
        with conn.transaction():
            conn.execute("UPDATE journal_lines SET debit = debit + 1")


def test_missing_permission_is_refused(env):
    _, factory, session = env
    weak = Session(session.user_id, "weak", frozenset({P.VOUCHER_VIEW}))
    with pytest.raises(PermissionDenied):
        VoucherService(factory).post(weak, 1)
        