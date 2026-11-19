"""Verifies the tables/columns the new code relies on, and compares the
permission codes in the database with src/app/domain/security/permissions.py.
Run BEFORE migrate.py:  python tools\\"""
from src.app.domain.security import permissions as P
from src.app.infrastructure.database.connection import get_connection

EXPECTED = {
    "users": {"id", "username", "password_hash", "is_active", "must_change_password"},
    "permissions": {"id", "code"},
    "role_permissions": {"role_id", "permission_id"},
    "user_roles": {"user_id", "role_id"},
    "accounts": {"id", "code", "name", "type", "normal_balance", "is_active"},
    "voucher_headers": {"id", "voucher_no", "voucher_date", "narration", "status"},
    "voucher_lines": {"id", "voucher_id", "account_id", "debit", "credit"},
}


def main() -> int:
    bad = False
    with get_connection() as conn:
        cols: dict[str, set] = {}
        for table, column in conn.execute(
            "SELECT table_name, column_name FROM information_schema.columns "
            "WHERE table_schema = 'public'"
        ):
            cols.setdefault(table, set()).add(column)

        for table, wanted in EXPECTED.items():
            missing = wanted - cols.get(table, set())
            print(f"[{'FAIL' if missing else ' ok '}] {table}"
                  + (f"  missing: {sorted(missing)}" if missing else ""))
            bad |= bool(missing)

        applied = conn.execute(
            "SELECT COALESCE(MAX(version), 0) FROM schema_version").fetchone()[0]
        print(f"\nschema_version = {applied} (run tools\\migrate.py until it reaches 6)")

        if "code" in cols.get("permissions", set()):
            have = {r[0] for r in conn.execute("SELECT code FROM permissions")}
            print("\nPermission codes in database:", ", ".join(sorted(have)) or "(none)")
            missing = [c for c in P.ALL if c not in have]
            if missing:
                print("\nNot in database (the app uses these codes):")
                for c in missing:
                    print("  -", c)
                print("\nEither rename the constants in domain/security/permissions.py to match "
                      "your existing codes, or INSERT the missing ones and grant them to a role.")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
