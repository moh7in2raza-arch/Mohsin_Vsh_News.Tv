import sqlite3, sys

db_path = sys.argv[1]
fields = {
    "payee": "TEXT",
    "cheque_no": "TEXT",
    "cheque_date": "TEXT",
    "amount_in_words": "TEXT",
    "prepared_by_name": "TEXT",
    "verified_by_name": "TEXT",
    "received_by_name": "TEXT",
    "checked_by_name": "TEXT",
    "approved_by_name": "TEXT",
}

con = sqlite3.connect(db_path)
try:
    con.execute("PRAGMA foreign_keys=ON")
    con.execute("BEGIN IMMEDIATE")
    tables = {r[0] for r in con.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    )}
    required = {"schema_info", "vouchers", "voucher_lines", "accounts"}
    if not required.issubset(tables):
        raise RuntimeError("Expected VSH Accounting tables are missing; database unchanged.")

    existing = {r[1] for r in con.execute("PRAGMA table_info(vouchers)")}
    added = []
    for name, sql_type in fields.items():
        if name not in existing:
            con.execute(f"ALTER TABLE vouchers ADD COLUMN {name} {sql_type}")
            added.append(name)

    version = con.execute(
        "SELECT value FROM schema_info WHERE key='version'"
    ).fetchone()
    if version:
        con.execute(
            "INSERT INTO schema_info(key,value) VALUES('voucher_format','2') "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value"
        )
    con.commit()

    print("Migration successful.")
    print("New columns:", ", ".join(added) if added else "None; already present")
    print("Existing voucher count:", con.execute(
        "SELECT COUNT(*) FROM vouchers"
    ).fetchone()[0])
    print("Existing account count:", con.execute(
        "SELECT COUNT(*) FROM accounts"
    ).fetchone()[0])
    print("Existing audit rows:", con.execute(
        "SELECT COUNT(*) FROM audit_log"
    ).fetchone()[0])
    print("Voucher fields now available:")
    for row in con.execute("PRAGMA table_info(vouchers)"):
        if row[1] in fields:
            print(" -", row[1], row[2])
except Exception:
    con.rollback()
    raise
finally:
    con.close()
