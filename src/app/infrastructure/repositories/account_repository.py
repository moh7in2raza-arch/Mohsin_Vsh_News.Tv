from src.app.infrastructure.repositories._sql import fetch_all, fetch_one


class AccountRepository:
    def __init__(self, conn):
        self.conn = conn

    def list_all(self, active_only=True) -> list[dict]:
        return fetch_all(
            self.conn,
            """SELECT a.id, a.code, a.name, a.type, a.normal_balance, a.is_active,
                      h.name AS header_name
               FROM accounts a
               LEFT JOIN account_headers h ON h.id = a.header_id
               WHERE (NOT %s OR a.is_active)
               ORDER BY a.code""",
            (active_only,),
        )

    def list_headers(self) -> list[dict]:
        return fetch_all(
            self.conn,
            """SELECT id, code, name, type
               FROM account_headers WHERE is_active ORDER BY type, code""",
        )

    def header_type(self, header_id: int):
        row = fetch_one(
            self.conn,
            "SELECT type FROM account_headers WHERE id = %s AND is_active",
            (header_id,),
        )
        return row["type"] if row else None

    def default_header_id(self, account_type: str):
        row = fetch_one(
            self.conn,
            """SELECT id FROM account_headers
               WHERE type = %s AND code = %s AND is_active""",
            (account_type, f"{account_type.upper()}_OTHER"),
        )
        return row["id"] if row else None

    def header_id_by_code(self, code: str):
        row = fetch_one(
            self.conn,
            "SELECT id FROM account_headers WHERE code = %s AND is_active",
            (code,),
        )
        return row["id"] if row else None

    def code_exists(self, code: str) -> bool:
        return self.conn.execute(
            "SELECT 1 FROM accounts WHERE code = %s", (code,)
        ).fetchone() is not None

    def name_exists(self, name: str, account_type: str) -> bool:
        return self.conn.execute(
            """SELECT 1 FROM accounts
               WHERE lower(name) = lower(%s) AND type = %s""",
            (name, account_type),
        ).fetchone() is not None

    def insert(
        self, code, name, account_type, normal_balance, header_id=None
    ) -> int:
        row = self.conn.execute(
            """INSERT INTO accounts
                   (code, name, type, normal_balance, is_active, header_id)
               VALUES (%s, %s, %s, %s, TRUE, %s) RETURNING id""",
            (code, name, account_type, normal_balance, header_id),
        ).fetchone()
        return row[0]

    def usable_ids(self, ids) -> set:
        rows = self.conn.execute(
            "SELECT id FROM accounts WHERE id = ANY(%s) AND is_active", (list(ids),)
        ).fetchall()
        return {r[0] for r in rows}

    def posting_details(self, ids) -> dict[int, dict]:
        rows = fetch_all(
            self.conn,
            """SELECT a.id, a.type, h.code AS header_code
               FROM accounts a
               LEFT JOIN account_headers h ON h.id = a.header_id
               WHERE a.id = ANY(%s) AND a.is_active""",
            (list(ids),),
        )
        return {row["id"]: row for row in rows}
    