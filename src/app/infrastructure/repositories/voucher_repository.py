class rom:
    ...

from src.app.infrastructure.repositories._sql import fetch_all, fetch_one

_HEADER_SQL = """
    SELECT h.id, h.voucher_no, h.voucher_date, h.narration, h.status,
           COALESCE((SELECT SUM(debit)  FROM voucher_lines WHERE voucher_id = h.id), 0) AS debit,
           COALESCE((SELECT SUM(credit) FROM voucher_lines WHERE voucher_id = h.id), 0) AS credit
    FROM voucher_headers h
"""


class VoucherRepository:
    """All SQL for vouchers and journal entries. Works on a shared connection
    so callers can keep business data and audit rows in one transaction."""

    def __init__(self, conn):
        self.conn = conn

    # ---- vouchers ----
    def next_voucher_no(self, year: int) -> str:
        n = self.conn.execute("SELECT nextval('voucher_no_seq')").fetchone()[0]
        return f"V-{year}-{n:06d}"

    def insert_header(self, voucher_no, voucher_date, narration, created_by) -> int:
        row = self.conn.execute(
            """INSERT INTO voucher_headers
                   (voucher_no, voucher_date, narration, status, created_by)
               VALUES (%s, %s, %s, 'Draft', %s) RETURNING id""",
            (voucher_no, voucher_date, narration, created_by),
        ).fetchone()
        return row[0]

    def insert_lines(self, voucher_id, lines) -> None:
        with self.conn.cursor() as cur:
            cur.executemany(
                """INSERT INTO voucher_lines (voucher_id, account_id, debit, credit)
                   VALUES (%s, %s, %s, %s)""",
                [(voucher_id, l.account_id, l.debit, l.credit) for l in lines],
            )

    def get_header(self, voucher_id, lock=False):
        sql = _HEADER_SQL + " WHERE h.id = %s"
        if lock:
            sql += " FOR UPDATE OF h"
        return fetch_one(self.conn, sql, (voucher_id,))

    def get_lines(self, voucher_id) -> list[dict]:
        return fetch_all(
            self.conn,
            """SELECT l.account_id, a.code AS account_code, a.name AS account_name,
                      l.debit, l.credit
               FROM voucher_lines l JOIN accounts a ON a.id = l.account_id
               WHERE l.voucher_id = %s ORDER BY l.id""",
            (voucher_id,),
        )

    def set_status(self, voucher_id, status) -> None:
        self.conn.execute(
            "UPDATE voucher_headers SET status = %s WHERE id = %s",
            (status, voucher_id),
        )

    def list_headers(self, status=None, limit=500) -> list[dict]:
        return fetch_all(
            self.conn,
            _HEADER_SQL
            + " WHERE (%s::text IS NULL OR h.status = %s) ORDER BY h.id DESC LIMIT %s",
            (status, status, limit),
        )

    # ---- journal ----
    def create_journal_entry(
        self, voucher_id: int, user_id: int,
        kind: str = "Posting", reverses_entry_id: int | None = None,
    ) -> int:
        row = self.conn.execute(
            """INSERT INTO journal_entries (voucher_id, posted_by, kind, reverses_entry_id)
               VALUES (%s, %s, %s, %s) RETURNING id""",
            (voucher_id, user_id, kind, reverses_entry_id),
        ).fetchone()
        return row[0]

    def insert_journal_lines(self, entry_id, lines) -> None:
        with self.conn.cursor() as cur:
            cur.executemany(
                """INSERT INTO journal_lines (entry_id, account_id, debit, credit)
                   VALUES (%s, %s, %s, %s)""",
                [(entry_id, l.account_id, l.debit, l.credit) for l in lines],
            )

    def find_posting_entry(self, voucher_id):
        row = self.conn.execute(
            "SELECT id FROM journal_entries WHERE voucher_id = %s AND kind = 'Posting'",
            (voucher_id,),
        ).fetchone()
        return row[0] if row else None

    def get_journal_lines(self, entry_id) -> list[dict]:
        return fetch_all(
            self.conn,
            "SELECT account_id, debit, credit FROM journal_lines WHERE entry_id = %s ORDER BY id",
            (entry_id,),
        )
    
