import re
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from src.app.infrastructure.database.connection import get_connection

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
_NAME = re.compile(r"^(\d{4})_.+\.sql$")


def _discover() -> list[tuple[int, Path]]:
    found = []
    for path in MIGRATIONS_DIR.glob("*.sql"):
        match = _NAME.match(path.name)
        if match:
            found.append((int(match.group(1)), path))
    return sorted(found)


def _backup_database() -> Path:
    """Create a restorable PostgreSQL dump before any pending migration runs."""
    database = os.environ["DB_NAME"]
    backup_root = Path(
        os.environ.get("LOCALAPPDATA")
        or (Path.home() / "AppData" / "Local")
    ) / "VSH ERP" / "database-backups"
    backup_root.mkdir(parents=True, exist_ok=True)
    backup_path = backup_root / (
        f"{database}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.dump"
    )
    pg_dump = shutil.which("pg_dump")
    if pg_dump is None:
        raise RuntimeError(
            "pg_dump is required to back up the database; no migration was applied"
        )

    env = os.environ.copy()
    backup_user = os.environ.get("DB_BACKUP_USER") or os.environ["DB_USER"]
    backup_password = (
        os.environ.get("DB_BACKUP_PASSWORD") or os.environ["DB_PASSWORD"]
    )
    env["PGPASSWORD"] = backup_password
    env["PGCONNECT_TIMEOUT"] = env.get("PGCONNECT_TIMEOUT", "15")
    command = [
        pg_dump,
        "--no-password",
        "--format=custom",
        "--host", os.environ["DB_HOST"],
        "--port", os.environ["DB_PORT"],
        "--username", backup_user,
        "--dbname", database,
        "--file", str(backup_path),
    ]
    try:
        subprocess.run(
            command, check=True, capture_output=True, text=True, env=env
        )
        if not backup_path.is_file() or backup_path.stat().st_size == 0:
            raise RuntimeError("pg_dump created an empty backup")
    except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
        backup_path.unlink(missing_ok=True)
        details = (
            exc.stderr.strip()
            if isinstance(exc, subprocess.CalledProcessError) and exc.stderr
            else str(exc)
        )
        raise RuntimeError(
            f"Database backup failed; no migration was applied: {details}"
        ) from exc
    return backup_path


def migrate() -> list[str]:
    """Back up once, then apply every migration newer than the recorded version."""
    applied = []
    with get_connection() as conn:
        has_version_table = conn.execute(
            "SELECT to_regclass('public.schema_version') IS NOT NULL"
        ).fetchone()[0]
        current = (
            conn.execute(
                "SELECT COALESCE(MAX(version), 0) FROM schema_version"
            ).fetchone()[0]
            if has_version_table else 0
        )
        pending = [
            (version, path)
            for version, path in _discover()
            if version > current
        ]
        if not pending:
            return applied

        _backup_database()
        conn.execute(
            """CREATE TABLE IF NOT EXISTS schema_version (
                   version    INTEGER PRIMARY KEY,
                   name       TEXT NOT NULL,
                   applied_at TIMESTAMPTZ NOT NULL DEFAULT now())"""
        )
        conn.commit()
        for version, path in pending:
            with conn.transaction():
                conn.execute(path.read_text(encoding="utf-8-sig"))
                conn.execute(
                    "INSERT INTO schema_version (version, name) VALUES (%s, %s)",
                    (version, path.name),
                )
            applied.append(path.name)
    return applied
