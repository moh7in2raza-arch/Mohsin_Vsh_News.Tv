from src.app.infrastructure.repositories._sql import fetch_all, fetch_one

_FROM = """
    FROM journal_lines jl
    JOIN journal_entries je ON je.id = jl.entry_id
    JOIN voucher_headers vh ON vh.id = je.voucher_id
"""


class ReportRepository:
    def __init__(self, conn):
        self.conn = conn

    def trial_balance(self, as_of) -> list[dict]:
        return fetch_all(
            self.conn,
            """SELECT a.code, a.name,
                      GREATEST(SUM(jl.debit) - SUM(jl.credit), 0)  AS debit,
                      GREATEST(SUM(jl.credit) - SUM(jl.debit), 0)  AS credit"""
            + _FROM
            + """ JOIN accounts a ON a.id = jl.account_id
                  WHERE vh.voucher_date <= %s
                  GROUP BY a.code, a.name ORDER BY a.code""",
            (as_of,),
        )

    def ledger_opening(self, account_id, date_from):
        row = fetch_one(
            self.conn,
            "SELECT COALESCE(SUM(jl.debit) - SUM(jl.credit), 0) AS net" + _FROM
            + " WHERE jl.account_id = %s AND vh.voucher_date < %s",
            (account_id, date_from),
        )
        return row["net"]

    def ledger_rows(self, account_id, date_from, date_to) -> list[dict]:
        return fetch_all(
            self.conn,
            """SELECT vh.voucher_date AS entry_date, vh.voucher_no, je.kind,
                      vh.narration, jl.debit, jl.credit""" + _FROM
            + """ WHERE jl.account_id = %s AND vh.voucher_date BETWEEN %s AND %s
                  ORDER BY vh.voucher_date, je.id, jl.id""",
            (account_id, date_from, date_to),
        )
    