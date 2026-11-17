from src.app.infrastructure.repositories._sql import fetch_all


class AccountRepository:
    def __init__(self, conn):
        self.conn = conn

    def list_all(self, active_only=True) -> list[dict]:
        return fetch_all(
            self.conn,
            """SELECT id, code, name, type, normal_balance, is_active
               FROM accounts WHERE (NOT %s OR is_active) ORDER BY code""",
            (active_only,),
        )

    def code_exists(self, code: str) -> bool:
        return self.conn.execute(
            "SELECT 1 FROM accounts WHERE code = %s", (code,)
        ).fetchone() is not None

    def insert(self, code, name, account_type, normal_balance) -> int:
        row = self.conn.execute(
            """INSERT INTO accounts (code, name, type, normal_balance, is_active)
               VALUES (%s, %s, %s, %s, TRUE) RETURNING id""",
            (code, name, account_type, normal_balance),
        ).fetchone()
        return row[0]

    def usable_ids(self, ids) -> set:
        rows = self.conn.execute(
            "SELECT id FROM accounts WHERE id = ANY(%s) AND is_active", (list(ids),)
        ).fetchall()
        return {r[0] for r in rows}
    