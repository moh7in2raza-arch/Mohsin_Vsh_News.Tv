from datetime import date
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql

from src.app.application.services.account_service import AccountService
from src.app.application.services.report_service import ReportService
from src.app.application.services.voucher_service import VoucherError, VoucherService
from src.app.application.session import Session
from src.app.domain.security import permissions as P
from src.app.infrastructure.database.connection import get_connection
from src.app.infrastructure.database.migrator import MIGRATIONS_DIR, _NAME
from src.app.infrastructure.database.unit_of_work import UnitOfWork


@pytest.fixture
def accounting():
    try:
        conn = get_connection()
    except Exception as exc:
        pytest.skip(f"database not reachable: {exc}")

    schema = f"voucher_test_{uuid4().hex}"
    try:
        conn.execute(sql.SQL("CREATE SCHEMA {}").format(sql.Identifier(schema)))
    except psycopg.Error as exc:
        conn.close()
        pytest.skip(f"database role cannot create isolated schemas: {exc}")

    try:
        conn.execute(
            sql.SQL("SET LOCAL search_path TO {}, public").format(
                sql.Identifier(schema)
            )
        )
        paths = sorted(
            path for path in MIGRATIONS_DIR.glob("*.sql") if _NAME.match(path.name)
        )
        for path in paths:
            if path.name == "0012_accounting_vouchers_and_chart.sql":
                with conn.cursor() as cursor:
                    cursor.executemany(
                        """INSERT INTO accounts
                               (code, name, type, normal_balance, is_active)
                           VALUES (%s, %s, %s, %s, TRUE)""",
                        [
                            ("1000", "Cash in hand", "Asset", "D"),
                            ("1010", "Bank", "Asset", "D"),
                            ("1100", "Accounts receivable", "Asset", "D"),
                            ("1500", "Fixed assets", "Asset", "D"),
                            ("2000", "Accounts payable", "Liability", "C"),
                            ("2100", "Salaries payable", "Liability", "C"),
                            ("3000", "Owner's capital", "Equity", "C"),
                            ("3100", "Retained earnings", "Equity", "C"),
                            ("4000", "Service income", "Income", "C"),
                            ("4100", "Other income", "Income", "C"),
                            ("5000", "Salaries expense", "Expense", "D"),
                            ("5100", "Rent expense", "Expense", "D"),
                            ("5200", "Utilities expense", "Expense", "D"),
                            ("5300", "Office expense", "Expense", "D"),
                        ],
                    )
            conn.execute(path.read_text(encoding="utf-8-sig"))

        user_id = conn.execute(
            """INSERT INTO users (username, full_name, password_hash)
               VALUES (%s, %s, %s) RETURNING id""",
            (f"voucher-test-{uuid4().hex}", "Voucher Test", "unused"),
        ).fetchone()[0]
        factory = lambda: UnitOfWork(connection=conn)
        session = Session(user_id, "voucher-test", frozenset(P.ALL))
        yield conn, factory, session
    finally:
        conn.rollback()
        conn.close()


def test_voucher_types_edit_soft_delete_post_and_ledger(accounting):
    conn, factory, session = accounting
    accounts = AccountService(factory)
    vouchers = VoucherService(factory)
    reports = ReportService(factory)
    by_name = {
        account.name.lower(): account
        for account in accounts.list_accounts(session)
    }
    required_accounts = {
        "cash in hand", "cash at bank", "accounts receivable", "inventory",
        "fixed assets", "accounts payable", "accrued expenses", "loans payable",
        "owner capital", "retained earnings", "sales revenue", "service revenue",
        "other income", "salary expense", "rent expense", "utilities expense",
        "office expense", "transport expense", "miscellaneous expense",
    }
    assert required_accounts <= by_name.keys()
    assert conn.execute("SELECT COUNT(*) FROM account_groups").fetchone()[0] == 5
    assert conn.execute("SELECT COUNT(*) FROM account_headers").fetchone()[0] >= 20
    assert conn.execute(
        "SELECT COUNT(*) FROM fiscal_periods WHERE is_closed = FALSE"
    ).fetchone()[0] == 1
    assert conn.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 24
    assert conn.execute(
        "SELECT name FROM accounts WHERE code = '1000'"
    ).fetchone()[0] == "Cash in hand"
    assert conn.execute(
        "SELECT COUNT(*) FROM accounts WHERE header_id IS NULL"
    ).fetchone()[0] == 0
    cash = by_name["cash in hand"]
    bank = by_name["cash at bank"]
    rent = by_name["rent expense"]
    payable = by_name["accounts payable"]
    sales = by_name["sales revenue"]

    with pytest.raises(VoucherError, match="open financial year"):
        vouchers.create_draft(
            session,
            date(2000, 1, 1),
            "Outside the fiscal year",
            [
                {"account_id": rent.id, "debit": "1", "credit": "0"},
                {"account_id": cash.id, "debit": "0", "credit": "1"},
            ],
        )

    voucher_id = vouchers.create_draft(
        session,
        date.today(),
        "Office rent",
        [
            {"account_id": rent.id, "debit": "100.00", "credit": "0"},
            {"account_id": cash.id, "debit": "0", "credit": "100.00"},
        ],
        party_name="Landlord",
        cheque_no="CHQ-100",
        cheque_date=date.today(),
        voucher_type="Payment",
        reference_no="INV-PV-001",
    )
    detail = vouchers.get_voucher(session, voucher_id)
    assert detail.header.voucher_no.startswith("PV-")
    assert detail.header.voucher_type == "Payment"
    assert detail.header.reference_no == "INV-PV-001"

    with pytest.raises(VoucherError, match="balanced"):
        vouchers.create_draft(
            session,
            date.today(),
            "Unbalanced",
            [
                {"account_id": rent.id, "debit": "10", "credit": "0"},
                {"account_id": cash.id, "debit": "0", "credit": "9"},
            ],
        )

    vouchers.update_draft(
        session,
        voucher_id,
        date.today(),
        "Updated rent",
        [
            {"account_id": rent.id, "debit": "125.00", "credit": "0",
             "description": "Monthly rent"},
            {"account_id": cash.id, "debit": "0", "credit": "125.00",
             "description": "Paid by cheque"},
        ],
        party_name="Landlord",
        cheque_no="CHQ-101",
        cheque_date=date.today(),
        voucher_type="Payment",
        reference_no="INV-PV-002",
    )
    assert vouchers.get_voucher(session, voucher_id).header.reference_no == "INV-PV-002"
    assert len(vouchers.list_vouchers(session, query="INV-PV-002")) == 1

    vouchers.submit(session, voucher_id)
    vouchers.approve(session, voucher_id)
    vouchers.post(session, voucher_id)
    posted = vouchers.get_voucher(session, voucher_id)
    assert posted.header.status == "Posted"
    assert posted.header.debit == posted.header.credit == Decimal("125.00")

    ledger = reports.account_ledger(
        session, rent.id, date.today(), date.today()
    )
    assert ledger[-1].debit == Decimal("125.00")
    assert ledger[-1].voucher_no == posted.header.voucher_no
    trial_balance = {
        row.code: row for row in reports.trial_balance(session, date.today())
    }
    assert trial_balance[rent.code].debit == Decimal("125.00")
    assert conn.execute(
        "SELECT COUNT(*) FROM journal_entries WHERE voucher_id = %s",
        (voucher_id,),
    ).fetchone()[0] == 1
    with pytest.raises(VoucherError, match="Only draft vouchers"):
        vouchers.update_draft(
            session,
            voucher_id,
            date.today(),
            "Not editable",
            [
                {"account_id": rent.id, "debit": "125", "credit": "0"},
                {"account_id": cash.id, "debit": "0", "credit": "125"},
            ],
        )
    with pytest.raises(VoucherError, match="Only draft vouchers"):
        vouchers.delete_draft(session, voucher_id)

    journal_voucher = vouchers.create_draft(
        session,
        date.today(),
        "Journal adjustment",
        [
            {"account_id": rent.id, "debit": "10", "credit": "0"},
            {"account_id": payable.id, "debit": "0", "credit": "10"},
        ],
    )
    assert vouchers.get_voucher(session, journal_voucher).header.voucher_no.startswith(
        "JV-"
    )

    sales_voucher = vouchers.create_draft(
        session,
        date.today(),
        "Cash sale",
        [
            {"account_id": cash.id, "debit": "25", "credit": "0"},
            {"account_id": sales.id, "debit": "0", "credit": "25"},
        ],
        party_name="Customer",
        voucher_type="Sales",
        reference_no="INV-S-01",
    )

    receipt_voucher = vouchers.create_draft(
        session,
        date.today(),
        "Customer receipt",
        [
            {"account_id": cash.id, "debit": "25", "credit": "0"},
            {"account_id": sales.id, "debit": "0", "credit": "25"},
        ],
        voucher_type="Receipt",
    )
    contra_voucher = vouchers.create_draft(
        session,
        date.today(),
        "Bank deposit",
        [
            {"account_id": bank.id, "debit": "25", "credit": "0"},
            {"account_id": cash.id, "debit": "0", "credit": "25"},
        ],
        voucher_type="Contra",
    )
    purchase_voucher = vouchers.create_draft(
        session,
        date.today(),
        "Office supply purchase",
        [
            {"account_id": rent.id, "debit": "25", "credit": "0"},
            {"account_id": payable.id, "debit": "0", "credit": "25"},
        ],
        party_name="Supplier",
        voucher_type="Purchase",
        reference_no="SUP-INV-01",
    )
    for voucher_id, voucher_type, prefix in (
        (sales_voucher, "Sales", "SV-"),
        (receipt_voucher, "Receipt", "RV-"),
        (contra_voucher, "Contra", "CV-"),
        (purchase_voucher, "Purchase", "PU-"),
    ):
        header = vouchers.get_voucher(session, voucher_id).header
        assert header.voucher_type == voucher_type
        assert header.voucher_no.startswith(prefix)

    with pytest.raises(VoucherError, match="must credit a cash or bank"):
        vouchers.create_draft(
            session,
            date.today(),
            "Invalid payment",
            [
                {"account_id": rent.id, "debit": "25", "credit": "0"},
                {"account_id": sales.id, "debit": "0", "credit": "25"},
            ],
            voucher_type="Payment",
        )

    vouchers.delete_draft(session, sales_voucher)
    vouchers.delete_draft(session, receipt_voucher)
    vouchers.delete_draft(session, contra_voucher)
    vouchers.delete_draft(session, purchase_voucher)
    vouchers.delete_draft(session, journal_voucher)
    deleted = vouchers.get_voucher(session, sales_voucher)
    assert deleted.header.status == "Deleted"
    assert len(deleted.lines) == 2
    assert all(
        row.id != sales_voucher for row in vouchers.list_vouchers(session)
    )
    assert any(
        row.id == sales_voucher
        for row in vouchers.list_vouchers(session, status="Deleted")
    )
    assert conn.execute(
        "SELECT COUNT(*) FROM journal_entries WHERE voucher_id = %s",
        (sales_voucher,),
    ).fetchone()[0] == 0

